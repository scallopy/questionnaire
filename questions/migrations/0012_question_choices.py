# Generated by Django 3.2.9 on 2022-05-10 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0011_auto_20220510_1210'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='choices',
            field=models.TextField(blank=True, help_text="The choices field is only used if the question type\nif the question type is 'radio', 'select', or\n'select multiple'. Separate choices with | ", null=True, verbose_name='Choices'),
        ),
    ]
