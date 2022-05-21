# Generated by Django 3.2.9 on 2021-11-12 21:48

import ckeditor_uploader.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='answer',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, default=0, null=True, verbose_name='Answer'),
        ),
        migrations.DeleteModel(
            name='Answer',
        ),
    ]
