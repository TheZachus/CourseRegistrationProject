from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.urls import reverse
from .models import Student, Faculty as FacultyModel, Course, Semester, Prerequisite, User, Enrollment, Programs, Role, Advisors
from .forms import FacultyForm, CourseForm, SemesterForm, PrerequisiteForm, AdvisorForm, EnrollmentForm, StudentUserForm, ProgramForm, CreateAccountForm
from django.contrib import messages
from datetime import date
from django.contrib.auth.hashers import make_password, check_password

# Custom session-based login required mixin because it wasnt working with the default one, also easier for role management
#also needed for APIs which is annoying because you have to extract the csrf token from the login page
class SessionLoginRequiredMixin:
    """Verify that the current user has an active session and the appropriate role"""
    
    # Roles allowed to access the view
    allowed_roles = []
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user is logged in
        if 'user_id' not in request.session:
            messages.error(request, "Please log in to access this page.")
            return redirect('login')
        
        # Check if user has the required role(s)
        user_role = request.session.get('role')
        if self.allowed_roles and user_role not in self.allowed_roles:
            messages.error(request, "You don't have permission to access this page.")
            return redirect('dashboard')
            
        return super().dispatch(request, *args, **kwargs)

# Authentication Views
class Login(View):
    def get(self, request):
        # If user is already logged in, redirect to dashboard
        if 'user_id' in request.session:
            return redirect('dashboard')
        return render(request, 'login.html')
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            # Find user with matching username
            user = User.objects.get(username=username)
            
            # Check if password matches
            if check_password(password, user.password):
                
                # Store user info in session
                request.session['user_id'] = user.id
                request.session['first_name'] = user.first_name
                request.session['role'] = user.role.role_name
                
                messages.success(request, f"Welcome, {user.first_name}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid password. Please try again.")
        except User.DoesNotExist:
            messages.error(request, "Username not found. Please try again.")
        
        return render(request, 'login.html')

class Logout(SessionLoginRequiredMixin, View):
    allowed_roles = ['Student', 'Advisor', 'Admin']
    
    def get(self, request):
        # Clear session data
        request.session.flush()
        messages.success(request, "You have been logged out successfully.")
        return redirect('login')

class Dashboard(SessionLoginRequiredMixin, View):
    # Allow all authenticated users to access dashboard
    allowed_roles = ['Student', 'Advisor', 'Admin']
    
    def get(self, request):
        user_role = request.session.get('role')
        return render(request, 'dashboard.html', {'user_role': user_role})

# STUDENT VIEWS
class StudentInfo(SessionLoginRequiredMixin, View):
    allowed_roles = ['Student']
    
    def get(self, request):
        # Get current user's role from session
        user_role = request.session.get('role')
        user_id = request.session.get('user_id')
        
        # For students, only show their own information
        try:
            user = User.objects.get(id=user_id)
            student = Student.objects.get(user=user)
            students = [student]  # Put in list to keep template compatible
        except (User.DoesNotExist, Student.DoesNotExist):
            messages.error(request, "Student record not found.")
            students = []
            
        return render(request, 'student/student-info.html', {'students': students, 'user_role': user_role})
    
    def post(self, request):
        student_id = request.POST.get('student_id')
        if student_id:
            student = get_object_or_404(Student, id=student_id)
            # Students shouldn't be able to delete student records
            messages.error(request, "You don't have permission to delete student records.")
        return redirect('student_info')

class ViewCourses(SessionLoginRequiredMixin, View):
    allowed_roles = ['Student', 'Advisor', 'Admin']
    
    def get(self, request):
        courses = Course.objects.all()
        user_role = request.session.get('role')
        
        # Add enrollment count for each course
        for course in courses:
            course.enrolled = Enrollment.objects.filter(course=course).count()
            
            # Fetch prerequisites for this course
            prerequisites = Prerequisite.objects.filter(course=course)
            prereq_list = []
            for prereq in prerequisites:
                if prereq.min_grade:
                    prereq_list.append(f"{prereq.prereq_course.course_name} (min grade: {prereq.min_grade})")
                else:
                    prereq_list.append(prereq.prereq_course.course_name)
            course.prereq_display = ", ".join(prereq_list) if prereq_list else "None"
            
        return render(request, 'student/view-courses.html', {'courses': courses, 'user_role': user_role})
    
    def post(self, request):
        course_id = request.POST.get('course_id')
        if course_id:
            course = get_object_or_404(Course, id=course_id)
            course.delete()
        return redirect('view_courses')

class MyEnrollments(SessionLoginRequiredMixin, View):
    allowed_roles = ['Student']
    
    def get(self, request):
        user_role = request.session.get('role')
        user_id = request.session.get('user_id')
        
        # Students can only see their own enrollments. error handling for 
        try:
            user = User.objects.get(id=user_id)
            student = Student.objects.get(user=user)
            all_enrollments = Enrollment.objects.filter(student=student)

        except (User.DoesNotExist, Student.DoesNotExist):
            messages.error(request, "Student record not found.")
            all_enrollments = Enrollment.objects.none()
        
        current_enrollments = all_enrollments.filter(date_dropped__isnull=True)
        past_enrollments = all_enrollments.filter(date_dropped__isnull=False)
        
        context = {
            'current_enrollments': current_enrollments,
            'past_enrollments': past_enrollments,
            'user_role': user_role
        }
        
        return render(request, 'student/my-enrollments.html', context)
    
    def post(self, request):
        enrollment_id = request.POST.get('enrollment_id')
        if enrollment_id:
            enrollment = get_object_or_404(Enrollment, id=enrollment_id)
            
            # Ensure students can only drop their own enrollments
            user_id = request.session.get('user_id')
            try:
                user = User.objects.get(id=user_id)
                student = Student.objects.get(user=user)
                if enrollment.student.id != student.id:
                    messages.error(request, "You can only drop your own enrollments.")
                    return redirect('my_enrollments')
            except (User.DoesNotExist, Student.DoesNotExist):
                messages.error(request, "Student record not found.")
                return redirect('my_enrollments')
                
            enrollment.date_dropped = date.today()
            enrollment.save()
            messages.success(request, f"Successfully dropped course: {enrollment.course.course_name}")
        return redirect('my_enrollments')

class ViewStudents(SessionLoginRequiredMixin, View):
    allowed_roles = ['Advisor', 'Admin']
    
    def get(self, request):
        students = Student.objects.all()
        user_role = request.session.get('role')
        return render(request, 'advisor/view-students.html', {'students': students, 'user_role': user_role})
    
    def post(self, request):
        student_id = request.POST.get('student_id')
        if student_id:
            student = get_object_or_404(Student, id=student_id)
            student.delete()
        return redirect('view_students')

class Faculty(SessionLoginRequiredMixin, View):
    allowed_roles = ['Admin']
    
    def get(self, request):
        faculty_members = FacultyModel.objects.all()
        user_role = request.session.get('role')
        return render(request, 'advisor/faculty.html', {'faculty_members': faculty_members, 'user_role': user_role})
    
    def post(self, request):
        faculty_id = request.POST.get('faculty_id')
        if faculty_id:
            faculty = get_object_or_404(FacultyModel, id=faculty_id)
            faculty.delete()
        return redirect('faculty')

class GenerateReports(SessionLoginRequiredMixin, View):
    allowed_roles = ['Advisor', 'Admin']
    
    def get(self, request):
        user_role = request.session.get('role')
        # Get all students with their enrollments for GPA calc
        students = Student.objects.all()
        student_data = []
        
        for student in students:
            # Calc GPA for each student based on grades
            enrollments = Enrollment.objects.filter(student=student)
            total_points = 0
            total_credits = 0
            
            for enrollment in enrollments:
                if enrollment.grade and enrollment.grade != "NotGraded":
                    # Convert letter grade to points
                    grade_points = {
                        'A': 4.0, 'A-': 3.7,'B+': 3.3, 'B': 3.0, 'B-': 2.7,
                        'C+': 2.3, 'C': 2.0, 'C-': 1.7, 'D+': 1.3, 'D': 1.0, 'D-': 0.7,'F': 0.0
                    }
                    
                    if enrollment.grade in grade_points:
                        # Multiply grade points by course credits
                        course_credits = enrollment.course.credits
                        total_points += grade_points[enrollment.grade] * course_credits
                        total_credits += course_credits
            
            gpa = total_points / total_credits if total_credits > 0 else 0
            
            student_data.append({
                'student': student,
                'gpa': round(gpa, 2),
                'enrollments': enrollments
            })
        
        # Sort students by GPA (descending)
        students_by_gpa = sorted(student_data, key=lambda x: x['gpa'], reverse=True)
        
        # Get all courses and semesters for filtering
        courses = Course.objects.all().order_by('course_name')
        semesters = Semester.objects.all().order_by('-start_date')
        
        # Get selected semester for filtering courses
        selected_semester_id = request.GET.get('semester_id')
        filtered_courses = courses
        selected_semester = None
        
        if selected_semester_id:
            selected_semester = get_object_or_404(Semester, id=selected_semester_id)
            # Filter courses by the selected semester
            filtered_courses = courses.filter(semester=selected_semester)
            
        # Get selected course for student enrollments
        selected_course_id = request.GET.get('course_id')
        students_by_course = []
        selected_course = None
        
        if selected_course_id:
            selected_course = get_object_or_404(Course, id=selected_course_id)
            # Get all enrollments for the selected course
            course_enrollments = Enrollment.objects.filter(course=selected_course).order_by('-grade')
            students_by_course = course_enrollments
        
        context = {
            'students_by_gpa': students_by_gpa,
            'semesters': semesters,
            'selected_semester': selected_semester,
            'filtered_courses': filtered_courses,
            'courses': courses,
            'selected_course': selected_course,
            'students_by_course': students_by_course,
            'user_role': user_role
        }
        
        return render(request, 'advisor/generate-reports.html', context)

# ADMIN VIEWS
class ViewSemesters(SessionLoginRequiredMixin, View):
    allowed_roles = ['Admin']
    
    def get(self, request):
        semesters = Semester.objects.all()
        user_role = request.session.get('role')
        return render(request, 'admin/view-semesters.html', {'semesters': semesters, 'user_role': user_role})
    
    def post(self, request):
        semester_id = request.POST.get('semester_id')
        if semester_id:
            semester = get_object_or_404(Semester, id=semester_id)
            semester.delete()
        return redirect('view_semesters')

class ViewAdvisors(SessionLoginRequiredMixin, View):
    allowed_roles = ['Admin']
    
    def get(self, request):
        user_role = request.session.get('role')
        # Get all users with the Advisor role
        advisor_role = Role.objects.filter(role_name='Advisor').first()
        if advisor_role:
            advisors = User.objects.filter(role=advisor_role)
        else:
            advisors = User.objects.none()
        
        return render(request, 'admin/view-advisors.html', {'advisors': advisors, 'user_role': user_role})
    
    def post(self, request):
        advisor_id = request.POST.get('advisor_id')
        if advisor_id:
            advisor = get_object_or_404(User, id=advisor_id)
            # Also delete the advisors record if it exists
            try:
                if hasattr(advisor, 'advisors'):
                    advisor.advisors.delete()
            except Advisors.DoesNotExist:
                pass
            advisor.delete()
            messages.success(request, "Advisor deleted successfully.")
        return redirect('view_advisors')

class ViewPreReqs(SessionLoginRequiredMixin, View):
    allowed_roles = ['Advisor', 'Admin']
    
    def get(self, request):
        prerequisites = Prerequisite.objects.all()
        user_role = request.session.get('role')
        return render(request, 'advisor/view-pre-reqs.html', {'prerequisites': prerequisites, 'user_role': user_role})
    
#some of the views that we did were specifically for the "delete" functionalilty, so instead of a post method, we had a separate "delete" view.
#why didn't we change it? work.

class ViewPrograms(SessionLoginRequiredMixin, View):
    allowed_roles = ['Advisor', 'Admin']
    
    def get(self, request):
        programs = Programs.objects.all()
        user_role = request.session.get('role')
        return render(request, 'advisor/view-programs.html', {'programs': programs, 'user_role': user_role})

# EDIT Views
class EditStudentInfo(SessionLoginRequiredMixin, View):
    allowed_roles = ['Student']
    
    def get(self, request, pk=None):
        user_role = request.session.get('role')
        user_id = request.session.get('user_id')
        
        # Students can only edit their own information
        try:
            user = User.objects.get(id=user_id)
            student = Student.objects.get(user=user)
            if pk and int(pk) != student.id:
                messages.error(request, "You can only edit your own information.")
                return redirect('student_info')
            
            # Pass the user object directly to the form
            form = StudentUserForm(instance=user)
        except (User.DoesNotExist, Student.DoesNotExist):
            messages.error(request, "Student record not found.")
            return redirect('student_info')
                
        return render(request, 'student/edit-student-info.html', {'form': form, 'user_role': user_role, 'student_id': student.id})
    
    def post(self, request, pk=None):
        user_role = request.session.get('role')
        user_id = request.session.get('user_id')
        
        # verify student is editing own information
        try:
            user = User.objects.get(id=user_id)
            student = Student.objects.get(user=user)
            if pk and int(pk) != student.id:
                messages.error(request, "You can only edit your own information.")
                return redirect('student_info')
        except (User.DoesNotExist, Student.DoesNotExist):
            messages.error(request, "Student record not found.")
            return redirect('student_info')
        
        form = StudentUserForm(request.POST)
        
        if form.is_valid():
            # Update student fields
            student.home_address = form.cleaned_data['home_address']
            student.phone_number = form.cleaned_data['phone_number']
            student.current_semester = form.cleaned_data['current_semester']
            student.program = form.cleaned_data['program']
            
            # Update user fields
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            
            # Only update password if provided
            if form.cleaned_data['password']:
                user.password = make_password(form.cleaned_data['password'])
            
            # Save both objects
            user.save()
            student.save()
            
            messages.success(request, "Your information has been updated successfully.")
            return redirect('student_info')
        
        return render(request, 'student/edit-student-info.html', {'form': form, 'user_role': user_role, 'student_id': student.id})

class EditPreReqs(SessionLoginRequiredMixin, View):
    allowed_roles = ['Advisor', 'Admin']
    
    def get(self, request, pk=None):
        user_role = request.session.get('role')
        if pk:
            prerequisite = get_object_or_404(Prerequisite, pk=pk)
            form = PrerequisiteForm(instance=prerequisite)
        else:
            form = PrerequisiteForm()
        return render(request, 'advisor/edit-pre-reqs.html', {'form': form, 'user_role': user_role})
    
    def post(self, request, pk=None):
        if pk:
            prerequisite = get_object_or_404(Prerequisite, pk=pk)
            form = PrerequisiteForm(request.POST, instance=prerequisite)
        else:
            form = PrerequisiteForm(request.POST)
        
        if form.is_valid():
            form.save()
            return redirect('view_pre_reqs')
        
        return render(request, 'advisor/edit-pre-reqs.html', {'form': form})

class EditFaculty(SessionLoginRequiredMixin, View):
    allowed_roles = ['Admin']
    
    def get(self, request, pk=None):
        user_role = request.session.get('role')
        if pk:
            faculty = get_object_or_404(FacultyModel, pk=pk)
            form = FacultyForm(instance=faculty)
        else:
            form = FacultyForm()
        return render(request, 'advisor/edit-faculty.html', {'form': form, 'user_role': user_role})
    
    def post(self, request, pk=None):
        if pk:
            faculty = get_object_or_404(FacultyModel, pk=pk)
            form = FacultyForm(request.POST, instance=faculty)
        else:
            form = FacultyForm(request.POST)
        
        if form.is_valid():
            form.save()
            return redirect('faculty')
        
        return render(request, 'advisor/edit-faculty.html', {'form': form})

class EditSemester(SessionLoginRequiredMixin, View):
    allowed_roles = ['Admin']
    
    def get(self, request, pk=None):
        user_role = request.session.get('role')
        if pk:
            semester = get_object_or_404(Semester, pk=pk)
            form = SemesterForm(instance=semester)
        else:
            form = SemesterForm()
        return render(request, 'admin/edit-semester.html', {'form': form, 'user_role': user_role})
    
    def post(self, request, pk=None):
        if pk:
            semester = get_object_or_404(Semester, pk=pk)
            form = SemesterForm(request.POST, instance=semester)
        else:
            form = SemesterForm(request.POST)
        
        if form.is_valid():
            form.save()
            return redirect('view_semesters')
        
        return render(request, 'admin/edit-semester.html', {'form': form})

class EditAdvisors(SessionLoginRequiredMixin, View):
    allowed_roles = ['Admin']
    
    def get(self, request, pk=None):
        user_role = request.session.get('role')
        if pk:
            advisor = get_object_or_404(User, pk=pk)
            form = AdvisorForm(instance=advisor)
        else:
            form = AdvisorForm()
        return render(request, 'admin/edit-advisors.html', {'form': form, 'user_role': user_role, 'advisor_id': pk})
    
    def post(self, request, pk=None):
        user_role = request.session.get('role')
        form = AdvisorForm(request.POST)
        
        if form.is_valid():
            if pk:
                # Update existing advisor
                advisor = get_object_or_404(User, pk=pk)
                
                # Check if username is being changed and if it already exists for another user
                new_username = form.cleaned_data['username']
                if advisor.username != new_username and User.objects.filter(username=new_username).exists():
                    messages.error(request, f"Username '{new_username}' is already taken. Please choose a different username.")
                    return render(request, 'admin/edit-advisors.html', {'form': form, 'user_role': user_role, 'advisor_id': pk})
                
                advisor.username = new_username
                # only update password if provided
                if form.cleaned_data['password']:
                    advisor.password = make_password(form.cleaned_data['password'])
                advisor.first_name = form.cleaned_data['first_name']
                advisor.last_name = form.cleaned_data['last_name']
                advisor.email = form.cleaned_data['email']
                
                # Sets role to advisor
                if advisor.role.role_name != 'Advisor':
                    advisor.role = form.advisor_role
                
                advisor.save()
            else:
                # Check if username exists before creating new advisor
                if User.objects.filter(username=form.cleaned_data['username']).exists():
                    messages.error(request, f"Username '{form.cleaned_data['username']}' is already taken. Please choose a different username.")
                    return render(request, 'admin/edit-advisors.html', {'form': form, 'user_role': user_role, 'advisor_id': pk})
                
                # Create new advisor
                advisor = User.objects.create(
                    username=form.cleaned_data['username'],
                    password=make_password(form.cleaned_data['password']),
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    email=form.cleaned_data['email'],
                    role=form.advisor_role
                )
            
            # Create or update the advisor
            try:
                advisor_profile = Advisors.objects.get(user=advisor)
            except Advisors.DoesNotExist:
                advisor_profile = Advisors(user=advisor)
                advisor_profile.save()
                
            messages.success(request, "Advisor saved successfully.")
            return redirect('view_advisors')
        
        return render(request, 'admin/edit-advisors.html', {'form': form, 'user_role': user_role, 'advisor_id': pk})

class EditCourse(SessionLoginRequiredMixin, View):
    allowed_roles = ['Admin', 'Advisor']
    
    def get(self, request, pk=None):
        user_role = request.session.get('role')
        if pk:
            course = get_object_or_404(Course, pk=pk)
            form = CourseForm(instance=course)
        else:
            form = CourseForm()
        return render(request, 'admin/edit-course.html', {'form': form, 'user_role': user_role})
    
    def post(self, request, pk=None):
        if pk:
            course = get_object_or_404(Course, pk=pk)
            form = CourseForm(request.POST, instance=course)
        else:
            form = CourseForm(request.POST)
        
        if form.is_valid():
            form.save()
            return redirect('view_courses')
        
        return render(request, 'admin/edit-course.html', {'form': form})

class EditEnrollment(SessionLoginRequiredMixin, View):
    allowed_roles = ['Advisor', 'Admin']
    
    def get(self, request):
        user_role = request.session.get('role')
        students = Student.objects.all()
        selected_student = None
        current_enrollments = None
        past_enrollments = None
        
        student_id = request.GET.get('student_id')
        if student_id:
            selected_student = get_object_or_404(Student, id=student_id)
            all_enrollments = Enrollment.objects.filter(student=selected_student)
            current_enrollments = all_enrollments.filter(date_dropped__isnull=True)
            past_enrollments = all_enrollments.filter(date_dropped__isnull=False)
            
        context = {
            'students': students,
            'selected_student': selected_student,
            'current_enrollments': current_enrollments,
            'past_enrollments': past_enrollments,
            'user_role': user_role
        }
        
        return render(request, 'advisor/edit-enrollment.html', context)

class EditEnrollmentDetail(SessionLoginRequiredMixin, View):
    allowed_roles = ['Advisor', 'Admin']
    
    def get(self, request, pk):
        user_role = request.session.get('role')
        
        # Check if we're creating a new enrollment
        if pk == 'new':
            student_id = request.GET.get('student_id')
            if not student_id:
                messages.error(request, "Student ID is required to create a new enrollment.")
                return redirect('edit_enrollment')
                
            student = get_object_or_404(Student, id=student_id)
            # create an empty enrollment object
            enrollment = Enrollment(student=student)
            # Set today's date as the default enrollment date
            from datetime import date
            form = EnrollmentForm(initial={
                'student': student,
                'date_enrolled': date.today()
            })
            template_context = {'form': form, 'enrollment': enrollment, 'user_role': user_role}
        else:
            # Regular edit enrollment
            enrollment = get_object_or_404(Enrollment, pk=pk)
            form = EnrollmentForm(instance=enrollment)
            template_context = {'form': form, 'enrollment': enrollment, 'user_role': user_role}
            
        return render(request, 'advisor/edit-enrollment-detail.html', template_context)
    
    def post(self, request, pk):
        # For new enrollments
        if pk == 'new':
            form = EnrollmentForm(request.POST)
            if form.is_valid():
                enrollment = form.save()
                student_id = enrollment.student.id
                messages.success(request, "New enrollment created successfully.")
                return redirect(f'{reverse("edit_enrollment")}?student_id={student_id}')
            else:
                student_id = request.GET.get('student_id')
                if student_id:
                    student = get_object_or_404(Student, id=student_id)
                    enrollment = Enrollment(student=student)
                    return render(request, 'advisor/edit-enrollment-detail.html', {'form': form, 'enrollment': enrollment})
                return render(request, 'advisor/edit-enrollment-detail.html', {'form': form})
        
        # For existing enrollments
        enrollment = get_object_or_404(Enrollment, pk=pk)
        form = EnrollmentForm(request.POST, instance=enrollment)
        
        if form.is_valid():
            form.save()
            student_id = enrollment.student.id
            messages.success(request, "Enrollment updated successfully.")
            return redirect(f'{reverse("edit_enrollment")}?student_id={student_id}')
        
        return render(request, 'advisor/edit-enrollment-detail.html', {'form': form, 'enrollment': enrollment})

# Create/Add Views
class CreateAccount(View):
    def get(self, request):
        form = CreateAccountForm()
        return render(request, 'create-account.html', {'form': form})
    
    def post(self, request):
        form = CreateAccountForm(request.POST)
        
        if form.is_valid():
            # Get form data
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            role = form.cleaned_data['role']
            
            # Check if username already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists. Please choose a different username.")
                return render(request, 'create-account.html', {'form': form})
            
            # Create the user record with hashed password
            user = User.objects.create(
                username=username,
                password=make_password(password),  # Hash the password
                first_name=first_name,
                last_name=last_name,
                email=email,
                role=role
            )
            
            # Handles role-specific record creation for students
            if role.role_name == 'Student':
                home_address = form.cleaned_data['home_address']
                phone_number = form.cleaned_data['phone_number']
                current_semester = form.cleaned_data['current_semester']
                program = form.cleaned_data['program']
                
                # Create student record
                Student.objects.create(
                    user=user,
                    home_address=home_address,
                    phone_number=phone_number,
                    current_semester=current_semester,
                    program=program
                )
                
                messages.success(request, "Student account created successfully.")
                
            elif role.role_name == 'Advisor':
                # Create advisor record
                Advisors.objects.create(user=user)
                messages.success(request, "Advisor account created successfully.")
                
            else:
                messages.success(request, "User account created successfully.")
            
            return redirect('login')
        
        return render(request, 'create-account.html', {'form': form})

class CreateEnrollment(SessionLoginRequiredMixin, View):
    allowed_roles = ['Student', 'Advisor', 'Admin']
    
    def post(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        user_role = request.session.get('role')
        user_id = request.session.get('user_id')
        
        # If user is student, use own record
        if user_role == 'Student':
            try:
                user = User.objects.get(id=user_id)
                student = Student.objects.get(user=user)
            except (User.DoesNotExist, Student.DoesNotExist):
                messages.error(request, "Student record not found.")
                return redirect('view_courses')
        else:
            # For advisors/admins, we'd need a student ID passed in somehow
            # For simplicity, using the first student
            student_id = request.POST.get('student_id')
            if student_id:
                student = get_object_or_404(Student, id=student_id)
            else:
                # Fallback to first student
                student = Student.objects.first()
                if not student:
                    messages.error(request, "No student records found.")
                    return redirect('view_courses')
        
        # Use the current semester from the student's profile
        semester = student.current_semester
        # Use the current year because parsing numbers from strings is hard
        from datetime import datetime
        current_year = datetime.now().year
        
        # Check if course is closed to enrollment
        if not course.open_to_enrollment:
            messages.error(request, f"Cannot enroll in {course.course_name}. This course is not open for enrollment.")
            return redirect('view_courses')
        
        # Check if student is already enrolled in this course
        if Enrollment.objects.filter(student=student, course=course).exists():
            messages.error(request, f"Cannot enroll in {course.course_name}. You are already enrolled in this course.")
            return redirect('view_courses')
            
        # Check if course quota has been reached (capacity of seats)
        current_enrollment_count = Enrollment.objects.filter(course=course).count()
        if current_enrollment_count >= course.quota:
            messages.error(request, f"Cannot enroll in {course.course_name}. Course quota ({course.quota}) has been reached.")
            return redirect('view_courses')
        
        # Check if the course has prerequisites
        prerequisites = Prerequisite.objects.filter(course=course)
        
        # If no prerequisites exist, proceed
        if not prerequisites.exists():
            # Create enrollment record
            Enrollment.objects.create(
                student=student,
                course=course,
                semester=semester,
                year=current_year,
                date_enrolled=date.today()
                # grade will use the default value "NotGraded"
            )
            messages.success(request, f"Successfully enrolled in {course.course_name}.")
            return redirect('my_enrollments')
        
        # If prerequisites exist, check if student has completed them with minimum grade
        missing_prerequisites = []
        grade_not_met = []
        
        # Define grade hierarchy for comparison
        grade_values = {
            'A': 12, 'A-': 11,'B+': 10, 'B': 9, 'B-': 8, 'C+': 7, 'C': 6, 'C-': 5,
            'D+': 4, 'D': 3, 'D-': 2,'F': 1, 'NotGraded': 0
        }
        
        for prerequisite in prerequisites:
            prereq_course = prerequisite.prereq_course
            # Check if student has enrollment record for this prerequisite course
            prereq_enrollment = Enrollment.objects.filter(student=student, course=prereq_course).first()
            
            if not prereq_enrollment:
                # Missing prerequisite course entirely
                missing_prerequisites.append(prereq_course.course_name)
            elif prerequisite.min_grade and prereq_enrollment.grade != "NotGraded":
                # Check if the grade meets the minimum requirement
                min_grade_value = grade_values.get(prerequisite.min_grade, 0)
                student_grade_value = grade_values.get(prereq_enrollment.grade, 0)
                
                if student_grade_value < min_grade_value:
                    # Student's grade is lower than the minimum required
                    grade_not_met.append(f"{prereq_course.course_name} (earned: {prereq_enrollment.grade}, required: {prerequisite.min_grade})")
        
        # Only enroll if all prerequisites are met and all minimum grades earned
        if not missing_prerequisites and not grade_not_met:
            Enrollment.objects.create(
                student=student,
                course=course,
                semester=semester,
                year=current_year,
                date_enrolled=date.today()
                # grade will use the default value "NotGraded"
            )
            messages.success(request, f"Successfully enrolled in {course.course_name}.")
        else:
            # Write error message
            error_message = f"Cannot enroll in {course.course_name}. "
            
            if missing_prerequisites:
                prereq_list = ", ".join(missing_prerequisites)
                error_message += f"Missing prerequisites: {prereq_list}. "
                
            if grade_not_met:
                grade_list = ", ".join(grade_not_met)
                error_message += f"Minimum grade requirements not met for: {grade_list}."
                
            messages.error(request, error_message)
        
        return redirect('view_courses')

# DELETE Views
#probs should have made some of these "Post" methods to save space, but code creep
class DeleteStudent(SessionLoginRequiredMixin, View):
    allowed_roles = ['Admin']
    
    def post(self, request, pk):
        student = get_object_or_404(Student, pk=pk)
        student.delete()
        return redirect('student_info')

class DeleteCourse(SessionLoginRequiredMixin, View):
    allowed_roles = ['Admin']
    
    def post(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        course.delete()
        return redirect('view_courses')

class DeleteEnrollment(SessionLoginRequiredMixin, View):
    allowed_roles = ['Student']
    
    def post(self, request, pk):
        enrollment = get_object_or_404(Enrollment, pk=pk)
        
        # Students can only drop own enrollments
        user_id = request.session.get('user_id')
        
        try:
            user = User.objects.get(id=user_id)
            student = Student.objects.get(user=user)
            if enrollment.student.id != student.id:
                messages.error(request, "You can only drop your own enrollments.")
                return redirect('my_enrollments')
        except (User.DoesNotExist, Student.DoesNotExist):
            messages.error(request, "Student record not found.")
            return redirect('my_enrollments')
        
        enrollment.delete()
        return redirect('my_enrollments')

class DeleteStudentAdvisor(SessionLoginRequiredMixin, View):
    allowed_roles = ['Advisor', 'Admin']
    
    def post(self, request, pk):
        student = get_object_or_404(Student, pk=pk)
        student.delete()
        return redirect('view_students')

class DeleteFaculty(SessionLoginRequiredMixin, View):
    allowed_roles = ['Admin']
    
    def post(self, request, pk):
        faculty = get_object_or_404(FacultyModel, pk=pk)
        faculty.delete()
        return redirect('faculty')

class DeleteSemester(SessionLoginRequiredMixin, View):
    allowed_roles = ['Admin']
    
    def post(self, request, pk):
        semester = get_object_or_404(Semester, pk=pk)
        semester.delete()
        return redirect('view_semesters')

class DeleteAdvisor(SessionLoginRequiredMixin, View):
    allowed_roles = ['Admin']
    
    def post(self, request, pk):
        advisor = get_object_or_404(User, pk=pk)
        advisor.delete()
        return redirect('view_advisors')

class DeleteAdvisorEnrollment(SessionLoginRequiredMixin, View):
    allowed_roles = ['Advisor', 'Admin']
    
    def post(self, request, pk):
        enrollment = get_object_or_404(Enrollment, pk=pk)
        student_id = enrollment.student.id
        enrollment.delete()
        return redirect(f'{reverse("edit_enrollment")}?student_id={student_id}')

class DeletePreReq(SessionLoginRequiredMixin, View):
    allowed_roles = ['Advisor', 'Admin']
    
    def post(self, request, pk):
        prerequisite = get_object_or_404(Prerequisite, pk=pk)
        prerequisite.delete()
        return redirect('view_pre_reqs')

class DeleteProgram(SessionLoginRequiredMixin, View):
    allowed_roles = ['Admin']
    
    def post(self, request, pk):
        program = get_object_or_404(Programs, pk=pk)
        program.delete()
        return redirect('view_programs')

class EditStudent(SessionLoginRequiredMixin, View):
    allowed_roles = ['Admin', 'Advisor']
    
    def get(self, request, pk=None):
        user_role = request.session.get('role')
        if pk:
            student = get_object_or_404(Student, pk=pk)
            # Pass the user object directly to the form
            form = StudentUserForm(instance=student.user)
        else:
            form = StudentUserForm()
        return render(request, 'admin/edit-student.html', {'form': form, 'user_role': user_role, 'student_id': pk})
    
    def post(self, request, pk=None):
        user_role = request.session.get('role')
        form = StudentUserForm(request.POST)
        
        if form.is_valid():
            if pk:
                # Update existing student and user
                student = get_object_or_404(Student, pk=pk)
                student.home_address = form.cleaned_data['home_address']
                student.phone_number = form.cleaned_data['phone_number']
                student.current_semester = form.cleaned_data['current_semester']
                student.program = form.cleaned_data['program']
                
                # Update user information
                if student.user:
                    student.user.first_name = form.cleaned_data['first_name']
                    student.user.last_name = form.cleaned_data['last_name']
                    student.user.email = form.cleaned_data['email']
                    
                    # Only update password if provided
                    if form.cleaned_data['password']:
                        student.user.password = make_password(form.cleaned_data['password'])
                    
                    student.user.save()
                
                student.save()
                messages.success(request, "Student information updated successfully.")
            else:
                # Create a new user with student role
                # Use the student_role from form
                if not form.student_role:
                    messages.error(request, "Student role not found in the system.")
                    return render(request, 'admin/edit-student.html', {'form': form, 'user_role': user_role, 'student_id': pk})
                
                # Create user
                user = User.objects.create(
                    username=form.cleaned_data['username'],
                    password=make_password(form.cleaned_data['password']),
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    email=form.cleaned_data['email'],
                    role=form.student_role
                )
                
                # Create student
                student = Student.objects.create(
                    user=user,
                    home_address=form.cleaned_data['home_address'],
                    phone_number=form.cleaned_data['phone_number'],
                    current_semester=form.cleaned_data['current_semester'],
                    program=form.cleaned_data['program']
                )
                
                messages.success(request, "New student created successfully.")
            
            return redirect('view_students')
        
        return render(request, 'admin/edit-student.html', {'form': form, 'user_role': user_role, 'student_id': pk})

class EditPrograms(SessionLoginRequiredMixin, View):
    allowed_roles = ['Advisor', 'Admin']
    
    def get(self, request, pk=None):
        user_role = request.session.get('role')
        if pk:
            program = get_object_or_404(Programs, pk=pk)
            form = ProgramForm(instance=program)
        else:
            form = ProgramForm()
        return render(request, 'advisor/edit-programs.html', {'form': form, 'user_role': user_role})
    
    def post(self, request, pk=None):
        if pk:
            program = get_object_or_404(Programs, pk=pk)
            form = ProgramForm(request.POST, instance=program)
        else:
            form = ProgramForm(request.POST)
        
        if form.is_valid():
            form.save()
            return redirect('view_programs')
        
        return render(request, 'advisor/edit-programs.html', {'form': form})
