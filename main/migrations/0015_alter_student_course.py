# Generated by Django 3.2.9 on 2021-12-07 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_alter_student_room'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='course',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
