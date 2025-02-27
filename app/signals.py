from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.utils import timezone
from .models import Exam, Course
from django.db import connection

@receiver(post_save, sender=Exam)
def delete_course_after_deadline(sender, instance, **kwargs):
    """Deletes the Course if the Exam deadline has passed."""
    if instance.deadline < timezone.now().date():
        instance.course.delete()

@receiver(post_migrate)
def set_custom_user_sequence(sender, **kwargs):
    # Make sure to run only for your app
    if sender.name == 'app':  # adjust if your app name is different
        with connection.cursor() as cursor:
            # For PostgreSQL: sets the next id to 1000
            cursor.execute("SELECT setval(pg_get_serial_sequence('app_customuser', 'id'), 999, false);")
