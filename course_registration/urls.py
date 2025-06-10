from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    path('', views.Login.as_view(), name='login'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('create-account/', views.CreateAccount.as_view(), name='create_account'),
    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),


    # Student URLs

    path('student/info/', views.StudentInfo.as_view(), name='student_info'),
    path('student/info/delete/<int:pk>/', views.DeleteStudent.as_view(), name='delete_student'),
    path('student/info/edit/', views.EditStudentInfo.as_view(), name='edit_student_info'),
    path('student/info/edit/<int:pk>/', views.EditStudentInfo.as_view(), name='edit_student_info_with_pk'),

    path('student/courses/', views.ViewCourses.as_view(), name='view_courses'),
    path('student/courses/delete/<int:pk>/', views.DeleteCourse.as_view(), name='delete_course'),

    path('student/enrollments/', views.MyEnrollments.as_view(), name='my_enrollments'),
    path('student/enrollments/delete/<int:pk>/', views.DeleteEnrollment.as_view(), name='delete_enrollment'),
    path('student/enrollments/create/<int:pk>/', views.CreateEnrollment.as_view(), name='create_enrollment'),
    

    # Advisor URLs

    path('advisor/students/', views.ViewStudents.as_view(), name='view_students'),
    path('advisor/students/delete/<int:pk>/', views.DeleteStudentAdvisor.as_view(), name='delete_student_advisor'),
    path('advisor/students/edit/', views.EditStudent.as_view(), name='edit_student'),
    path('advisor/students/edit/<int:pk>/', views.EditStudent.as_view(), name='edit_student_with_pk'),

    path('advisor/enrollments/', views.EditEnrollment.as_view(), name='edit_enrollment'),
    path('advisor/enrollments/delete/<int:pk>/', views.DeleteAdvisorEnrollment.as_view(), name='delete_advisor_enrollment'),
    path('advisor/enrollments/edit/<str:pk>/', views.EditEnrollmentDetail.as_view(), name='edit_enrollment_detail'),

    path('advisor/pre-reqs/', views.ViewPreReqs.as_view(), name='view_pre_reqs'),
    path('advisor/pre-reqs/delete/<int:pk>/', views.DeletePreReq.as_view(), name='delete_pre_req'),
    path('advisor/pre-reqs/edit/', views.EditPreReqs.as_view(), name='edit_pre_reqs'),
    path('advisor/pre-reqs/edit/<int:pk>/', views.EditPreReqs.as_view(), name='edit_pre_reqs_with_pk'),

    path('advisor/faculty/', views.Faculty.as_view(), name='faculty'),
    path('advisor/faculty/delete/<int:pk>/', views.DeleteFaculty.as_view(), name='delete_faculty'),
    path('advisor/faculty/edit/', views.EditFaculty.as_view(), name='edit_faculty'),
    path('advisor/faculty/edit/<int:pk>/', views.EditFaculty.as_view(), name='edit_faculty_with_pk'),

    path('advisor/programs/', views.ViewPrograms.as_view(), name='view_programs'),
    path('advisor/programs/delete/<int:pk>/', views.DeleteProgram.as_view(), name='delete_program'),
    path('advisor/programs/edit/', views.EditPrograms.as_view(), name='edit_programs'),
    path('advisor/programs/edit/<int:pk>/', views.EditPrograms.as_view(), name='edit_programs_with_pk'),

    path('advisor/reports/', views.GenerateReports.as_view(), name='generate_reports'),
    

    # Admin URLs

    path('admin/semesters/', views.ViewSemesters.as_view(), name='view_semesters'),
    path('admin/semesters/delete/<int:pk>/', views.DeleteSemester.as_view(), name='delete_semester'),
    path('admin/semesters/edit/', views.EditSemester.as_view(), name='edit_semester'),
    path('admin/semesters/edit/<int:pk>/', views.EditSemester.as_view(), name='edit_semester_with_pk'),

    path('admin/advisors/', views.ViewAdvisors.as_view(), name='view_advisors'),
    path('admin/advisors/delete/<int:pk>/', views.DeleteAdvisor.as_view(), name='delete_advisor'),
    path('admin/advisors/edit/', views.EditAdvisors.as_view(), name='edit_advisors'),
    path('admin/advisors/edit/<int:pk>/', views.EditAdvisors.as_view(), name='edit_advisors_with_pk'),

    path('admin/courses/edit/', views.EditCourse.as_view(), name='edit_course'),
    path('admin/courses/edit/<int:pk>/', views.EditCourse.as_view(), name='edit_course_with_pk'),
    

    # API URLs
    
    path('api/roles/', api_views.RoleListCreate.as_view(), name='role-list-create'),
    path('api/roles/<int:pk>/', api_views.RoleRetrieveUpdateDestroy.as_view(), name='role-detail'),
    
    path('api/users/', api_views.UserListCreate.as_view(), name='user-list-create'),
    path('api/users/<int:pk>/', api_views.UserRetrieveUpdateDestroy.as_view(), name='user-detail'),
    
    path('api/semesters/', api_views.SemesterListCreate.as_view(), name='semester-list-create'),
    path('api/semesters/<int:pk>/', api_views.SemesterRetrieveUpdateDestroy.as_view(), name='semester-detail'),
    
    path('api/students/', api_views.StudentListCreate.as_view(), name='student-list-create'),
    path('api/students/<int:pk>/', api_views.StudentRetrieveUpdateDestroy.as_view(), name='student-detail'),
    
    path('api/faculty/', api_views.FacultyListCreate.as_view(), name='faculty-list-create'),
    path('api/faculty/<int:pk>/', api_views.FacultyRetrieveUpdateDestroy.as_view(), name='faculty-detail'),
    
    path('api/courses/', api_views.CourseListCreate.as_view(), name='course-list-create'),
    path('api/courses/<int:pk>/', api_views.CourseRetrieveUpdateDestroy.as_view(), name='course-detail'),
    
    path('api/prerequisites/', api_views.PrerequisiteListCreate.as_view(), name='prerequisite-list-create'),
    path('api/prerequisites/<int:pk>/', api_views.PrerequisiteRetrieveUpdateDestroy.as_view(), name='prerequisite-detail'),
    
    path('api/enrollments/', api_views.EnrollmentListCreate.as_view(), name='enrollment-list-create'),
    path('api/enrollments/<int:pk>/', api_views.EnrollmentRetrieveUpdateDestroy.as_view(), name='enrollment-detail'),
]
