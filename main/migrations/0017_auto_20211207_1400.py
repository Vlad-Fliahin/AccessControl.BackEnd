# Generated by Django 3.2.9 on 2021-12-07 14:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_alter_staff_job'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='course',
            field=models.IntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='room',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, to='main.room'),
        ),
    ]
