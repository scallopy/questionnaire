# Generated by Django 3.2.9 on 2021-11-12 22:11

import ckeditor_uploader.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0002_auto_20211112_2148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='answer',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True, verbose_name='Answer'),
        ),
    ]