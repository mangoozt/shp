# Generated by Django 3.2.8 on 2021-12-22 16:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('homework', '0002_remove_testattempt_number'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='testattempt',
            options={'ordering': ['-datetime', '-finished']},
        ),
    ]
