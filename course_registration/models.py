from django.db import models

class Role(models.Model):
    role_name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.role_name

class Programs(models.Model):
    program_name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.program_name

class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=100, null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"

class Semester(models.Model):
    semester_name = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()
    
    def __str__(self):
        return self.semester_name

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    home_address = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)
    current_semester = models.ForeignKey(Semester, on_delete=models.SET_NULL, null=True, blank=True)
    program = models.ForeignKey(Programs, on_delete=models.CASCADE, null=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class Advisors(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Advisor: {self.user.first_name} {self.user.last_name}"

class Faculty(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    program = models.ForeignKey(Programs, on_delete=models.CASCADE, null=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Course(models.Model):
    course_name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    instructor = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    credits = models.PositiveIntegerField()
    semester = models.ForeignKey(Semester, on_delete=models.SET_NULL, null=True, blank=True)
    quota = models.PositiveIntegerField(default=0)
    open_to_enrollment = models.BooleanField(default=True)
    
    def __str__(self):
        return self.course_name

class Prerequisite(models.Model):
    course = models.ForeignKey(Course, related_name='main_course', on_delete=models.CASCADE)
    prereq_course = models.ForeignKey(Course, related_name='prerequisite_course', on_delete=models.CASCADE)
    min_grade = models.CharField(max_length=2, null=True, blank=True)
    
    def __str__(self):
        if self.min_grade:
            return f"{self.prereq_course.course_name} (min: {self.min_grade}) > {self.course.course_name}"
        else:
            return f"{self.prereq_course.course_name} > {self.course.course_name}"

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    year = models.PositiveIntegerField()
    grade = models.CharField(max_length=10, default="NotGraded")
    date_enrolled = models.DateField(null=True)
    date_dropped = models.DateField(null=True)
    
    def __str__(self):
        status = "Dropped" if self.date_dropped else "Active"
        return f"{self.student} - {self.course} ({status})"