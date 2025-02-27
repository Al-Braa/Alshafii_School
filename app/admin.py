from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Lecture, Certificate, Course, LectureAttendance, Exam
from .forms import CustomUserCreationForm, CustomUserChangeForm, CertificateAdminForm

class LectureInline(admin.TabularInline):
    model = Lecture
    extra = 1  # Number of empty forms to display
    fields = ('name', 'date', 'start_time', 'end_time', 'link', 'file')
    show_change_link = True

class LectureAttendanceInline(admin.TabularInline):
    model = LectureAttendance
    extra = 0
    readonly_fields = ('user', 'status')
    can_delete = False

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('username', 'full_name', 'gender', 'nationality', 'phone_number', 'is_staff', 'is_active')
    list_filter = ('username', 'full_name', 'gender', 'nationality', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('full_name', 'gender', 'nationality', 'phone_number')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'full_name', 'gender', 'nationality', 'phone_number', 'is_staff', 'is_active', 'groups', 'user_permissions')}
        ),
    )
    search_fields = ('username', 'full_name', 'gender', 'nationality', 'phone_number')
    ordering = ('username',)
    inlines = [LectureAttendanceInline]

class CourseAdmin(admin.ModelAdmin):
    inlines = [LectureInline]
    list_display = ('name',)
    search_fields = ('name',)

class LectureAdmin(admin.ModelAdmin):
    inlines = [LectureAttendanceInline]
    list_display = ('name', 'date', 'start_time', 'end_time', 'course')
    list_filter = ('date', 'course')
    search_fields = ('name', 'course__name')

class CertificateAdmin(admin.ModelAdmin):
    form = CertificateAdminForm
    list_display = ('name', 'user', 'date_added')
    search_fields = ('name', 'user__id')

class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'link')
    search_fields = ('name', 'course__name')

admin.site.register(Course, CourseAdmin)
admin.site.register(Lecture, LectureAdmin)
admin.site.register(Certificate, CertificateAdmin)
admin.site.register(LectureAttendance)
admin.site.register(Exam, ExamAdmin)
