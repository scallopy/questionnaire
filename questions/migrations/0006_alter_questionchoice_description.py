# Generated by Django 3.2.9 on 2022-05-08 10:42

import ckeditor_uploader.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0005_auto_20220508_1000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questionchoice',
            name='description',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True, verbose_name='Answer'),
        ),
    ]
