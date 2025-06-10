from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from .models import Role, User, Semester, Student, Faculty, Course, Prerequisite, Enrollment, Programs, Advisors

# Custom Admin Classes
class CourseAdmin(admin.ModelAdmin):
    def change_view(self, request, object_id, form_url='', extra_context=None):
        # Redirect to your custom edit page
        return redirect(reverse('edit_course_with_pk', args=[object_id]))

class FacultyAdmin(admin.ModelAdmin):
    def change_view(self, request, object_id, form_url='', extra_context=None):
        # Redirect to your custom edit page
        return redirect(reverse('edit_faculty_with_pk', args=[object_id]))

class SemesterAdmin(admin.ModelAdmin):
    def change_view(self, request, object_id, form_url='', extra_context=None):
        # Redirect to your custom edit page
        return redirect(reverse('edit_semester_with_pk', args=[object_id]))

class StudentAdmin(admin.ModelAdmin):
    def change_view(self, request, object_id, form_url='', extra_context=None):
        # Redirect to your custom edit page
        return redirect(reverse('dashboard'))

class AdvisorAdmin(admin.ModelAdmin):
    def change_view(self, request, object_id, form_url='', extra_context=None):
        # Check if the user is an advisor
        user = User.objects.get(pk=object_id)
        if user.role.role_name.lower() == 'advisor':
            return redirect(reverse('edit_advisors_with_pk', args=[object_id]))
        return super().change_view(request, object_id, form_url, extra_context)

# Register your models here.
admin.site.register(Role)
admin.site.register(User, AdvisorAdmin)
admin.site.register(Semester, SemesterAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Faculty, FacultyAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Prerequisite)
admin.site.register(Enrollment)
admin.site.register(Programs)
admin.site.register(Advisors)
