# Generated by Django 5.0.2 on 2024-10-28 15:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('odorwatch', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='unidadfiscalizable',
            name='estado',
        ),
    ]