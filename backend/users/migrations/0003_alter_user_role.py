# Generated by Django 3.2.16 on 2023-04-07 05:58

import users.enums
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_first_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('user', users.enums.Role['USER']), ('admin', users.enums.Role['ADMIN'])], default='user', max_length=20, verbose_name='Право достапа'),
        ),
    ]
