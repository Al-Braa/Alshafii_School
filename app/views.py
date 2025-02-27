from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from .forms import CustomUserCreationForm, ProfileForm, LectureAttendanceForm
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser, Lecture, Certificate, Course, LectureAttendance, Exam
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from django.utils import timezone
from django.db.models import Prefetch

@login_required
def index(request, error_message=""):
    today = timezone.now().date()
    now = timezone.now().time()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    # Fetch courses and prefetch lectures within the date range
    courses = Course.objects.prefetch_related(
        Prefetch('lecture_set', queryset=Lecture.objects.all())
    )
    # print(courses, "courses")
    # for course in courses:
    #     print(course.lecture_set.all() , "courses")
    # Fetch single lectures (lectures without a course)
    single_lectures = Lecture.objects.filter(course=None)
    
    # Prepare attendance status for each lecture
    lecture_attendance = {}
    for lecture in single_lectures:
        attendance = LectureAttendance.objects.filter(user=request.user, lecture=lecture).first()
        lecture_attendance[lecture.id] = attendance.status if attendance else 'not_yet'
    
    for course in courses:
        for lecture in course.lecture_set.all():
            attendance = LectureAttendance.objects.filter(user=request.user, lecture=lecture).first()
            lecture_attendance[lecture.id] = attendance.status if attendance else 'not_yet'
    
    if request.method == 'POST':
        form = LectureAttendanceForm(request.POST)
        if form.is_valid():
            lecture_id = request.POST.get('lecture_id')
            attendance, created = LectureAttendance.objects.update_or_create(
                user=request.user,
                lecture_id=lecture_id,
                defaults={'status': form.cleaned_data['status']}
            )
            return redirect('index')
    else:
        form = LectureAttendanceForm()

    # Fetch exams for each course
    course_exams = {course.id: Exam.objects.filter(course=course).exists() for course in courses}
    cannot_access = {
        course.id: (not exam.can_access(request.user) if (exam := Exam.objects.filter(course=course).first()) else True)
        for course in courses
    }
    deadlines = {
        course.id: (exam.deadline if (exam := Exam.objects.filter(course=course).first()) else None)
        for course in courses
    }
    print(deadlines, "deadlines")
    # # Handle filtering and sorting
    # filter_status = request.GET.get('status')
    # sort_by = request.GET.get('sort_by', 'date')
    # print(filter_status, "filter_status")
    # if filter_status:
    #     print(filter_status, "filter_status")
    #     single_lectures = single_lectures.filter(lecture_attendances__status=filter_status, lecture_attendances__user=request.user)
    #     for course in courses:
    #         course.lecture_set.set(course.lecture_set.filter(lecture_attendances__status=filter_status, lecture_attendances__user=request.user))
    #         print(course.lecture_set.all() , "courses")
    # print(sort_by, "sort_by")
    
    # # single_lectures = single_lectures.order_by(sort_by)
    # # for course in courses:
    # #     course.lecture_set.set(course.lecture_set.order_by(sort_by))
    # #     print(course.lecture_set.order_by("date") , "courses")
    # for course in courses:
    #     print(course.lecture_set.all() , "courses")
    return render(request, "app/index.html", {
        'lectures': single_lectures,
        'courses': courses,
        'today': today,
        'now': now,
        'form': form,
        'lecture_attendance': lecture_attendance,
        'course_exams': course_exams,
        'error_message': error_message,
        'cannot_access': cannot_access,
        'deadlines': deadlines,
        # 'filter_status': filter_status,
        # 'sort_by': sort_by
    })

def login(request):
    if request.user.is_authenticated:
        return redirect('index')
    error_message = None
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    auth_login(request, user)
                    return redirect('index')
                else:
                    error_message = "This account is inactive."
            else:
                error_message = "Invalid username or password."
        else:
            error_message = "Invalid username or password."
    else:
        form = AuthenticationForm()
    return render(request, "app/login.html", {'form': form, 'error_message': error_message})

def register(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)  # Log the user in after registration
            return redirect('index')  # Redirect to a success page
    else:
        form = CustomUserCreationForm()
    return render(request, "app/register.html", {'form': form})

@login_required
def certificates(request):
    user = CustomUser.objects.get(username=request.user)
    user_certificates = Certificate.objects.filter(user=user)
    certificate_count = user_certificates.count()
    return render(request, "app/certificates.html", {
        'certificates': user_certificates,
        'certificate_count': certificate_count
    })

@login_required
def profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, "app/profile.html", {'form': form})

def logout(request):
    auth_logout(request)
    return redirect('login')

@login_required
def access_exam(request, course_id):
    print(course_id, "course_id")
    try:
        exam = Exam.objects.filter(course_id=course_id).first()
        print(exam, "exam")
    except Exam.DoesNotExist:
        return redirect('index')
    if exam and exam.can_access(request.user):
        return redirect(exam.link)
    else:
        return redirect('index')  # Redirect to a page indicating access is denied