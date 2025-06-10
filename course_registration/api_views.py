from rest_framework import generics
from .models import Role, User, Semester, Student, Faculty as FacultyModel, Course, Prerequisite, Enrollment
from .serializers import RoleSerializer, UserSerializer, SemesterSerializer, StudentSerializer, FacultySerializer, CourseSerializer, PrerequisiteSerializer, EnrollmentSerializer
from .views import SessionLoginRequiredMixin

# Role API Views
class RoleListCreate(SessionLoginRequiredMixin, generics.ListCreateAPIView):
    allowed_roles = ['Admin']
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

class RoleRetrieveUpdateDestroy(SessionLoginRequiredMixin, generics.RetrieveUpdateDestroyAPIView):
    allowed_roles = ['Admin']
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

# User API Views
class UserListCreate(SessionLoginRequiredMixin, generics.ListCreateAPIView):
    allowed_roles = ['Admin']
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserRetrieveUpdateDestroy(SessionLoginRequiredMixin, generics.RetrieveUpdateDestroyAPIView):
    allowed_roles = ['Admin']
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Semester API Views
class SemesterListCreate(SessionLoginRequiredMixin, generics.ListCreateAPIView):
    allowed_roles = ['Admin']
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer

class SemesterRetrieveUpdateDestroy(SessionLoginRequiredMixin, generics.RetrieveUpdateDestroyAPIView):
    allowed_roles = ['Admin']
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer

# Student API Views
class StudentListCreate(SessionLoginRequiredMixin, generics.ListCreateAPIView):
    allowed_roles = ['Admin']
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class StudentRetrieveUpdateDestroy(SessionLoginRequiredMixin, generics.RetrieveUpdateDestroyAPIView):
    allowed_roles = ['Admin']
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

# Faculty API Views
class FacultyListCreate(SessionLoginRequiredMixin, generics.ListCreateAPIView):
    allowed_roles = ['Admin']
    queryset = FacultyModel.objects.all()
    serializer_class = FacultySerializer

class FacultyRetrieveUpdateDestroy(SessionLoginRequiredMixin, generics.RetrieveUpdateDestroyAPIView):
    allowed_roles = ['Admin']
    queryset = FacultyModel.objects.all()
    serializer_class = FacultySerializer

# Course API Views
class CourseListCreate(SessionLoginRequiredMixin, generics.ListCreateAPIView):
    allowed_roles = ['Admin']
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class CourseRetrieveUpdateDestroy(SessionLoginRequiredMixin, generics.RetrieveUpdateDestroyAPIView):
    allowed_roles = ['Admin']
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

# Prerequisite API Views
class PrerequisiteListCreate(SessionLoginRequiredMixin, generics.ListCreateAPIView):
    allowed_roles = ['Admin']
    queryset = Prerequisite.objects.all()
    serializer_class = PrerequisiteSerializer

class PrerequisiteRetrieveUpdateDestroy(SessionLoginRequiredMixin, generics.RetrieveUpdateDestroyAPIView):
    allowed_roles = ['Admin']
    queryset = Prerequisite.objects.all()
    serializer_class = PrerequisiteSerializer

# Enrollment API Views
class EnrollmentListCreate(SessionLoginRequiredMixin, generics.ListCreateAPIView):
    allowed_roles = ['Admin']
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer

class EnrollmentRetrieveUpdateDestroy(SessionLoginRequiredMixin, generics.RetrieveUpdateDestroyAPIView):
    allowed_roles = ['Admin']
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer 