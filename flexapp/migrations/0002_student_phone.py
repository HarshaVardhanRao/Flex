# Generated by Django 5.1.1 on 2025-02-11 08:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flexapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='phone',
            field=models.CharField(blank=True, default='', max_length=12, null=True),
        ),
    ]
