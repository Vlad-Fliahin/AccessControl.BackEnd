# Generated by Django 3.2.9 on 2021-11-13 15:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_alter_user_card'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='card',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, to='main.card'),
        ),
    ]
