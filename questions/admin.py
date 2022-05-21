from django.contrib import admin
from .models import Question, Category, Quiz, Choice, QuestionChoice
from nested_admin import (
    NestedModelAdmin,
    NestedStackedInline,
    NestedTabularInline
)

from django.utils.html import mark_safe


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_name']
    prepopulated_fields = {'slug': ('category_name',)}


def image_obj(self, obj):
    return mark_safe('<img src="{url}" width="auto" height="300" />'
                     .format(url=obj.image.url))


# class ChoiceInline(admin.StackedInline):
#     model = Choice
#     extra = 3


class ChoiceNestedInline(NestedTabularInline):
    model = Choice
    extra = 1
    classes = ['collapse']


# class QuestionChoiceNestedInline(NestedStackedInline):
#     model = QuestionChoice
#     extra = 1
#     fieldsets = [
#         ('Position', {'fields': ['position']}),
#         (None, {'fields': ['answer_position']}),
#         (None, {'fields': ['quiz']}),
#         (None, {'fields': ['question_text']}),
#         (None, {'fields': ['description']}),
#     ]
#     list_display = ['position', 'question_text']
#     inlines = [ChoiceNestedInline]


class QuestionInline(admin.StackedInline):
    model = QuestionChoice
    ordering = ('position',)
    extra = 1


class QuizAdmin(admin.ModelAdmin):
    model = Quiz
    list_display = ['title', 'pub_date']
    list_filter = ('pub_date',)
    inlines = [QuestionInline, ]


# class QuizAdmin(NestedModelAdmin):
#     model = Quiz
#     list_display = ['title', 'pub_date']
#     list_filter = ('pub_date',)
#     inlines = [QuestionChoiceNestedInline, ]


# Register your models here.
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Question)
admin.site.register(Choice)
