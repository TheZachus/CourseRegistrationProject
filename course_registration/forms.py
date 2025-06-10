from django import forms
from .models import Faculty as FacultyModel, Course, Semester, Prerequisite, Enrollment, Programs, Role

class StudentUserForm(forms.Form):
    # User fields
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(max_length=128, required=True, widget=forms.PasswordInput())
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=False)
    
    # Student fields
    home_address = forms.CharField(max_length=200, required=True)
    phone_number = forms.CharField(max_length=20, required=True)
    current_semester = forms.ModelChoiceField(queryset=Semester.objects.all(), required=False)
    program = forms.ModelChoiceField(queryset=Programs.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        super(StudentUserForm, self).__init__(*args, **kwargs)
        
        # Set student role (hidden from the form)
        self.student_role = Role.objects.filter(role_name='Student').first()
        
        # If instance is provided, populate fields
        if instance:
            self.initial['username'] = instance.username
            self.initial['first_name'] = instance.first_name
            self.initial['last_name'] = instance.last_name
            self.initial['email'] = instance.email
            # Password not populated for security reasons
            
            # Set student-specific fields if available
            if hasattr(instance, 'student'):
                self.initial['home_address'] = instance.student.home_address
                self.initial['phone_number'] = instance.student.phone_number
                self.initial['current_semester'] = instance.student.current_semester
                self.initial['program'] = instance.student.program

#had to create this from scratch because it's submitting the form to create an account of various roles.
#this is the same thing with the advisor form and student form.
class CreateAccountForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(max_length=128, required=True, widget=forms.PasswordInput())
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=False)
    role = forms.ModelChoiceField(queryset=Role.objects.all(), required=True)
    
    # Student-specific fields
    home_address = forms.CharField(max_length=200, required=False)
    phone_number = forms.CharField(max_length=20, required=False)
    current_semester = forms.ModelChoiceField(queryset=Semester.objects.all(), required=False)
    program = forms.ModelChoiceField(queryset=Programs.objects.all(), required=False)
    
    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        super(CreateAccountForm, self).__init__(*args, **kwargs)
        
        # If instance is provided, populate fields
        if instance:
            self.initial['username'] = instance.username
            self.initial['first_name'] = instance.first_name
            self.initial['last_name'] = instance.last_name
            self.initial['email'] = instance.email
            # Password is not populated for security reasons
            
            # Set role if possible
            if instance.role:
                self.initial['role'] = instance.role
                
            # Set student-specific fields if this is student account
            if hasattr(instance, 'student'):
                self.initial['home_address'] = instance.student.home_address
                self.initial['phone_number'] = instance.student.phone_number
                self.initial['current_semester'] = instance.student.current_semester
                self.initial['program'] = instance.student.program

class FacultyForm(forms.ModelForm):
    class Meta:
        model = FacultyModel
        fields = '__all__'

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = '__all__'

class SemesterForm(forms.ModelForm):
    class Meta:
        model = Semester
        fields = '__all__'

class PrerequisiteForm(forms.ModelForm):
    class Meta:
        model = Prerequisite
        fields = '__all__'

# learned about the initialization section. did not want to change other forms to match initialization.
class AdvisorForm(forms.Form):
    # User fields
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(max_length=128, required=True, widget=forms.PasswordInput())
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=False)
    
    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        super(AdvisorForm, self).__init__(*args, **kwargs)
        
        # Set advisor role, hidden from the form
        self.advisor_role = Role.objects.filter(role_name='Advisor').first()
        
        # If instance is provided, populate fields
        if instance:
            self.initial['username'] = instance.username
            self.initial['first_name'] = instance.first_name
            self.initial['last_name'] = instance.last_name
            self.initial['email'] = instance.email
            # Password is not populated for security reasons

class EnrollmentForm(forms.ModelForm):
    date_dropped = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    
    class Meta:
        model = Enrollment
        fields = '__all__'
        widgets = {
            'date_enrolled': forms.DateInput(attrs={'type': 'date'}),
        }

class ProgramForm(forms.ModelForm):
    class Meta:
        model = Programs
        fields = '__all__'
