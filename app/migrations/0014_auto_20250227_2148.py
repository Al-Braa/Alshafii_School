from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),  # adjust based on your current migration
    ]

    operations = [
        migrations.RunSQL(
            # This sets the sequence to 999 so the next value will be 1000.
            sql="ALTER SEQUENCE app_customuser_id_seq RESTART WITH 1000;",
            reverse_sql="ALTER SEQUENCE app_customuser_id_seq RESTART WITH 1;",
        ),
    ]
