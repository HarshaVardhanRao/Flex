# Generated by Django 5.0.8 on 2024-08-08 02:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flexapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='forignlanguages',
            name='certificate',
            field=models.FileField(null=True, upload_to='certificates/'),
        ),
    ]