# Generated by Django 5.1.1 on 2025-05-11 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flexapp', '0010_remove_publications_publication_abstract_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filloutfield',
            name='field_type',
            field=models.CharField(choices=[('text', 'Text'), ('number', 'Number'), ('date', 'Date'), ('choice', 'Multiple Choice'), ('file_awk', 'Pick Certificate')], max_length=20),
        ),
    ]
