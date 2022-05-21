import sys
import datetime

from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.template.defaultfilters import slugify
# from unidecode import unidecode
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.postgres.fields import ArrayField


if sys.version_info[0] >= 3:
    unicode = str


CHOICES_HELP_TEXT = (
    """The choices field is only used if the question type
if the question type is 'radio', 'select', or
'select multiple'. Separate choices with | character."""
)


def validate_choices(choices):
    """Verifies that there is at least two choices in choices
    :param String choices: The string representing the user choices.
    """
    values = choices.split(settings.CHOICES_SEPARATOR)
    empty = 0
    for value in values:
        if value.replace(" ", "") == "":
            empty += 1
    if len(values) < 2 + empty:
        msg = "The selected field requires an associated list of choices."
        msg += " Choices must contain more than one item."
        raise ValidationError(msg)


# Create your models here.
class Category(models.Model):
    category_name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Catergories"

    def __str__(self):
        return self.category_name

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(unicode(self.category_name))
        super(Category, self).save(*args, **kwargs)

    def get_absolute_url(self):
        kwargs = {
            'slug': self.slug
        }
        return reverse('category', kwargs=kwargs)


class Quiz(models.Model):
    ALL_IN_ONE_PAGE = 0
    BY_QUESTION = 1

    DISPLAY_QUESTIONS = [
        (BY_QUESTION, "By question"),
        (ALL_IN_ONE_PAGE, "All in one page"),
    ]
    title = models.CharField(max_length=200)
    category = models.ForeignKey(Category, null=True,
                                 blank=True, on_delete=models.CASCADE)
    display_questions = models.SmallIntegerField(
        "Display questions", choices=DISPLAY_QUESTIONS, default=ALL_IN_ONE_PAGE
    )
    pub_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name = 'quiz'
        verbose_name_plural = 'quizes'

    def __str__(self):
        return self.title

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

    def get_absolute_url(self):
        return reverse('quiz_detail', args=[self.id])

    def is_all_in_one_page(self):
        return self.display_questions == self.ALL_IN_ONE_PAGE


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    category = models.ForeignKey(Category, null=True,
                                 blank=True, on_delete=models.CASCADE)
    answer = RichTextUploadingField('Answer', null=True, blank=True)

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.datetimedelta(days=1)

    def get_absolute_url(self):
        return reverse('detail', args=[self.id])


class QuestionChoice(models.Model):

    TEXT = "text"
    SHORT_TEXT = "short-text"
    RADIO = "radio"
    SELECT = "select"
    SELECT_MULTIPLE = "select-multiple"
    INTEGER = "integer"
    FLOAT = "float"
    UPLOAD_FILE = "upload_file"
    DATE = "date"

    QUESTION_TYPES = (
        (TEXT, "text (multiple line)"),
        (SHORT_TEXT, "short text (one line)"),
        (RADIO, "radio"),
        (SELECT, "select"),
        (SELECT_MULTIPLE, "Select Multiple"),
        (INTEGER, "integer"),
        (FLOAT, "float"),
        (UPLOAD_FILE, "Upload File"),
        (DATE, "date"),
    )

    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, null=True, blank=True
    )
    question_text = models.CharField("Text", max_length=200, blank=True)
    description = RichTextUploadingField('Description', null=True, blank=True)
    position = models.IntegerField("Position", default=0)
    type = models.CharField("Type", max_length=200, choices=QUESTION_TYPES, default=TEXT)
    choices = models.TextField("Choices", blank=True, null=True, help_text=CHOICES_HELP_TEXT)
    answer_position = models.IntegerField("Answer Position:", default=0)

    class Meta:
        ordering = ["position"]

    def save(self, *args, **kwargs):
        if self.type in [
            QuestionChoice.RADIO,
            QuestionChoice.SELECT,
            QuestionChoice.SELECT_MULTIPLE
        ]:
            validate_choices(self.choices)
        super().save(*args, **kwargs)

    def get_clean_choices(self):
        """Return split and stripped list of choices with no null values."""
        if self.choices is None:
            return []
        choices_list = []
        for choice in self.choices.split(settings.CHOICES_SEPARATOR):
            choice = choice.strip()
            if choice:
                choices_list.append(choice)
        return choices_list

    def get_choices(self):
        """
        Parse the choices field and return a tuple formatted appropriately
        for the 'choices' argument of a form widget.
        """
        choices_list = []
        for choice in self.get_clean_choices():
            choices_list.append(choice)
        choices_tuple = tuple(choices_list)
        return choices_tuple

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)


class Choice(models.Model):
    question = models.CharField("Text", max_length=200, blank=True)
    choice_text = models.TextField('Choice', max_length=79, null=True, blank=True)
    answer = models.BooleanField(default=False)
    # selected_answer = ArrayField(models.IntegerField(),null=True, blank=True)
    selected_answer = models.IntegerField("Selected Answer:", default=0)

    def __str__(self):
        return self.choice_text

    def save(self, *args, **kwargs):
        if self.question.answer_position == self.selected_answer:
            self.answer = True
        else:
            self.answer = False
        super().save(*args, **kwargs)


class Response(models.Model):
    created = models.DateTimeField("Creation date", auto_now_add=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, verbose_name="Quiz", related_name="responses")
    interview_uuid = models.CharField("Interview unique identifier", max_length=36)

    class Meta:
        verbose_name = "Set of answers to surveys"
        verbose_name_plural = "Sets of answers to surveys"

    def __str__(self):
        msg = f"Response to {self.quiz} by {self.user}"
        msg += f" on {self.created}"
        return msg


class Answer(models.Model):
    question = models.ForeignKey(QuestionChoice, on_delete=models.CASCADE, verbose_name="Question", related_name="answers")
    response = models.ForeignKey(Response, on_delete=models.CASCADE, verbose_name="Response", related_name="answers")
    created = models.DateTimeField("Creation date", auto_now_add=True)
    updated = models.DateTimeField("Update date", auto_now=True)
    body = models.TextField("Content", blank=True, null=True)

    def __init__(self, *args, **kwargs):
        try:
            question = QuestionChoice.objects.get(pk=kwargs["question_id"])
        except KeyError:
            question = kwargs.get("question")
        body = kwargs.get("body")
        if question and body:
            self.check_answer_body(question, body)
        super().__init__(*args, **kwargs)

    @property
    def values(self):
        if self.body is None:
            return [None]
        if len(self.body) < 3 or self.body[0:3] != "[u'":
            return [self.body]
        # We do not use eval for security reason but it could work with :
        # eval(self.body)
        # It would permit to inject code into answer though.
        values = []
        raw_values = self.body.split("', u'")
        nb_values = len(raw_values)
        for i, value in enumerate(raw_values):
            if i == 0:
                value = value[3:]
            if i + 1 == nb_values:
                value = value[:-2]
            values.append(value)
        return values

    def check_answer_body(self, question, body):
        if question.type in [Question.RADIO, Question.SELECT, Question.SELECT_MULTIPLE]:
            choices = question.get_clean_choices()
            if body:
                if body[0] == "[":
                    answers = []
                    for i, part in enumerate(body.split("'")):
                        if i % 2 == 1:
                            answers.append(part)
                else:
                    answers = [body]
            for answer in answers:
                if answer not in choices:
                    msg = f"Impossible answer '{body}'"
                    msg += f" should be in {choices} "
                    raise ValidationError(msg)

    def __str__(self):
        return f"{self.__class__.__name__} to '{self.question}' : '{self.body}'"
