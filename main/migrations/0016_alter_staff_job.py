# Generated by Django 3.2.9 on 2021-12-07 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_alter_student_course'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staff',
            name='job',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
