from django import template
from hijridate import Hijri, Gregorian as Gre

register = template.Library()

@register.filter
def hijri_date(gregorian_date, lang="en"):
    hijri_date = Gre(gregorian_date.year, gregorian_date.month, gregorian_date.day).to_hijri()
    return f"{hijri_date.day} {hijri_date.month_name(lang)} {hijri_date.year}"

@register.filter
def get_status(lecture_attendance, lecture_id):
    return lecture_attendance.get(lecture_id)

@register.filter
def format_status(status, lang="en"):
    STATUS_CHOICES = {
        'listening': 'Listening',
        'not_yet': 'Not Yet',
        'watched': 'Watched',
    }
    if lang == "ar":
        print("ar")
        STATUS_CHOICES = {
            'listening': "يتم الحضور",
            'not_yet': "لم يتم الحضور",
            'watched': "تم الحضور",
        }
    return STATUS_CHOICES.get(status, 'Not Yet')