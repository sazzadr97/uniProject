# Generated by Django 3.1.1 on 2021-04-26 15:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manCal', '0010_notes_complited'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='notes',
            options={'ordering': ['complited', 'id']},
        ),
    ]