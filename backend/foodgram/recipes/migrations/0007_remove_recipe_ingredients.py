# Generated by Django 2.2.19 on 2022-07-12 20:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_auto_20220712_1934'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='ingredients',
        ),
    ]
