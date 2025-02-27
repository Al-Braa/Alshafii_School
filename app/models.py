from django.db import models
from django.contrib.auth.models import AbstractUser
from django_countries.fields import CountryField
from datetime import timedelta, datetime
from django.utils import timezone
from hijridate import Hijri, Gregorian as Gre

class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')])
    nationality = CountryField()
    phone_number = models.CharField(max_length=15)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',  # Add related_name to avoid clashes
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',  # Add related_name to avoid clashes
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.username

def default_start_time():
    return timezone.now().time()

def default_end_time():
    return (timezone.now() + timedelta(hours=1)).time()

class Course(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Lecture(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateField()
    start_time = models.TimeField(default=default_start_time)
    end_time = models.TimeField(default=default_end_time)
    link = models.URLField(max_length=200, blank=True)
    file = models.FileField(upload_to='lectures/files/', blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name
    
    @property
    def is_time(self):
        now = timezone.now()
        start_datetime = timezone.make_aware(datetime.combine(self.date, self.start_time), timezone.get_current_timezone())
        end_datetime = timezone.make_aware(datetime.combine(self.date, self.end_time), timezone.get_current_timezone())
        if end_datetime <= start_datetime:
            end_datetime += timedelta(days=1)
        return start_datetime <= now <= end_datetime

    @property
    def hijri_date(self):
        hijri_date = Gre(self.date.year, self.date.month, self.date.day).to_hijri()
        return hijri_date

class Certificate(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date_added = models.DateField(default=timezone.now)
    file = models.FileField(upload_to='certificates/files/', blank=True)

    def __str__(self):
        return f"Certificate: {self.name} by {self.user.username}"

    @property
    def hijri_date(self):
        hijri_date = Gre(self.date_added.year, self.date_added.month, self.date_added.day).to_hijri()
        return hijri_date

class LectureAttendance(models.Model):
    STATUS_CHOICES = [
        ('not_yet', 'Not Yet'),
        ('listening', 'Listening'),
        ('watched', 'Watched'),
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='lecture_attendances')
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name='lecture_attendances')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='not_yet')

    class Meta:
        unique_together = ('user', 'lecture')

    def __str__(self):
        return f"{self.user.username} - {self.lecture.name} - {self.get_status_display()}"

class Exam(models.Model):
    name = models.CharField(max_length=255)
    link = models.URLField(max_length=200)
    deadline = models.DateField(default=timezone.now, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def can_access(self, user):
        lectures = self.course.lecture_set.all()
        for lecture in lectures:
            attendance = LectureAttendance.objects.filter(user=user, lecture=lecture).first()
            if not attendance or attendance.status != 'watched':
                return False
        return True

