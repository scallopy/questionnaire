# Generated by Django 3.2.9 on 2022-05-10 12:10

import ckeditor_uploader.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0010_auto_20220510_1040'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ['position']},
        ),
        migrations.RemoveField(
            model_name='question',
            name='answer',
        ),
        migrations.RemoveField(
            model_name='question',
            name='category',
        ),
        migrations.RemoveField(
            model_name='question',
            name='pub_date',
        ),
        migrations.AddField(
            model_name='question',
            name='answer_position',
            field=models.IntegerField(default=0, verbose_name='Answer Position:'),
        ),
        migrations.AddField(
            model_name='question',
            name='description',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True, verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='question',
            name='position',
            field=models.IntegerField(default=0, verbose_name='Position'),
        ),
        migrations.AddField(
            model_name='question',
            name='quiz',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='questions.quiz'),
        ),
        migrations.AddField(
            model_name='question',
            name='type',
            field=models.CharField(choices=[('text', 'text (multiple line)'), ('short-text', 'short text (one line)'), ('radio', 'radio'), ('select', 'select'), ('select-multiple', 'Select Multiple'), ('integer', 'integer'), ('float', 'float'), ('upload_file', 'Upload File'), ('date', 'date')], default='text', max_length=200, verbose_name='Type'),
        ),
        migrations.AlterField(
            model_name='choice',
            name='question',
            field=models.CharField(blank=True, max_length=200, verbose_name='Text'),
        ),
        migrations.AlterField(
            model_name='question',
            name='question_text',
            field=models.CharField(blank=True, max_length=200, verbose_name='Text'),
        ),
        migrations.DeleteModel(
            name='QuestionChoice',
        ),
    ]