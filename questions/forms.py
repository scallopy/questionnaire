from django import forms
from django.forms import models
from django.db.models import Prefetch
from django.urls import reverse
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField

from .signals import quiz_completed
from .models import Question, QuestionChoice, Quiz, Response, Answer


class ResponseForm(models.ModelForm):

    FIELDS = {
        QuestionChoice.TEXT: forms.CharField,
        QuestionChoice.SHORT_TEXT: forms.CharField,
        QuestionChoice.SELECT_MULTIPLE: forms.MultipleChoiceField,
        QuestionChoice.INTEGER: forms.IntegerField,
        QuestionChoice.FLOAT: forms.FloatField,
        QuestionChoice.UPLOAD_FILE: forms.FileField,
        QuestionChoice.DATE: forms.DateField,
    }

    WIDGETS = {
        QuestionChoice.TEXT: forms.Textarea,
        QuestionChoice.SHORT_TEXT: forms.TextInput,
        QuestionChoice.RADIO: forms.RadioSelect,
        QuestionChoice.SELECT: forms.Select,
        QuestionChoice.UPLOAD_FILE: forms.FileInput,
        QuestionChoice.SELECT_MULTIPLE: forms.CheckboxSelectMultiple,
    }

    class Meta:
        model = Response
        fields = ()

    def __init__(self, *args, **kwargs):
        self.quiz = kwargs.pop("quiz")
        try:
            self.user = kwargs.pop("user")
        except KeyError:
            self.user = None
        try:
            self.step = int(kwargs.pop("step"))
        except KeyError:
            self.step = None
        print("1.1: ", "Quiz: ", self.quiz)
        super().__init__(*args, **kwargs)
        # self.uuid = uuid.uuid4().hex

        self.questions = QuestionChoice.objects.filter(
            quiz=self.quiz.pk).order_by('position')
        self.steps_count = len(self.questions)
        print("1.2: ", "Steps count:", self.steps_count)

        self.response = False
        self.answers = False

        self.add_questions(kwargs.get("data"))

        if self.response is not None:
            for name in self.fields.keys():
                self.fields[name].widget.attrs["disabled"] = True

    def add_questions(self, data):
        for i, question in enumerate(self.questions.all()):
            not_to_keep = i != self.step and self.step is not None
            if self.quiz.display_questions == Quiz.BY_QUESTION and not_to_keep:
                continue
            self.add_question(question, data)

    def get_question_initial(self, question, data):
        initial = None
        user=self.user
        quiz=self.quiz
        print(self.user)
        print(self.quiz)
        print(Response.objects.prefetch_related(Prefetch('user', queryset=self.user)))
        try:
            self.response = Response.objects.prefetch_related("user", "quiz").get(
                user=self.user, quiz=self.quiz
            )
            print(self.response)
        except Response.DoesNotExist:
            self.response = None
        print("Response: ", self.response)

        if question.type == QuestionChoice.SELECT_MULTIPLE:
            initial = []
            if answer.body == "[]":
                pass
            elif "[" in answer.body and "]" in answer.body:
                initial = []
                unformated_choices = answer.body[1:-1].strip()
                for unformated_choice in unformated_choices.split(settings.CHOICES_SEPARATOR):
                    choice = unformated_choice.split("'")[1]
                    initial.append(slugify(choice))
            else:
                initial.append(slugify(answer.body))
        else:
            initial = answer.body
        if data:
            initial = data.get("question_%d" % question.pk)
        print("Initial: ", initial)
        return initial

    def get_question_widget(self, question):
        try:
            return self.WIDGETS[question.type]
        except KeyError:
            return None

    @staticmethod
    def get_question_choices(question):
        qchoices = None
        if question.type not in [
            QuestionChoice.TEXT,
            QuestionChoice.SHORT_TEXT,
            QuestionChoice.INTEGER,
            QuestionChoice.FLOAT,
            QuestionChoice.UPLOAD_FILE,
            QuestionChoice.DATE,
        ]:
            qchoices = question.get_choices()
            if question.type in [QuestionChoice.SELECT]:
                qchoices = tuple([("", "------------")]) + qchoices
        return qchoices

    def get_question_field(self, question, **kwargs):
        print("1.3: ", "Get Question field")
        try:
            print(self.FIELDS[question.type](**kwargs))
            return self.FIELDS[question.type](**kwargs)
        except KeyError:
            print("Error: ", "forms.ChoiceField(**kwargs)")
            print(kwargs['choices'])
            return forms.ChoiceField(**kwargs)

    def add_question(self, question, data):
        my_label = str(question.position) + ". " + question.question_text
        label = my_label + question.description
        kwargs = {"label": label}

        # initial = self.get_question_initial(question, data)
        # if initial:
        #     kwargs["initial"] = initial
        choices = self.get_question_choices(question)
        if choices:
            kwargs["choices"] = choices
        widget = self.get_question_widget(question)
        if widget:
            kwargs["widget"] = widget
        field = self.get_question_field(question, **kwargs)

        if question.type == QuestionChoice.DATE:
            field.widget.attrs["class"] = "date"
        self.fields["question_%d" % question.pk] = field

    def has_next_step(self):
        if not self.quiz.is_all_in_one_page():

            if self.step < self.steps_count - 1:
                return True
        return False

    def next_step_url(self):
        if self.has_next_step():
            context = {"pk": self.quiz.id, "step": self.step + 1}
            return reverse("quiz_detail_step", kwargs=context)

    def current_step_url(self):
        context = {"id": self.quiz.id, "step": self.step}
        print("Current step: ", context)
        return reverse("quiz_detail_step", kwargs=context)


        """
    def save(self, commit=True):
        instance = super(ResponseForm, self).save(commit=False)
        print("Instance: ", instance)
        instance.save()
        return instance
        response = self.fields
        if self.response is None:
            response = super().save(commit=False)
        print("Response:", response)
        if self.user.is_authenticated:
            response.user = self.user
        response.save()
        data = {"quiz_id": response.quiz.id, "responses": []}
        for field_name, field_value in list(self.cleaned_data.items()):
            if field_name.startswith("questionchoice_"):
                q_id = int(field_name.split("_")[1])
                question = QuestionChoice.objects.get(pk=q_id)
                if self.answer is None:
                    answer = Answer(question=question)
                if question.type == QuestionChoice.UPLOAD_FILE:
                    value, file_url = field_value.split(":", 1)
                answer.body = field_value
                data["responses"].append(answer.question.id, answer.body)
                answer.response = response
                answer.save()
        quiz_completed.send(sender=Response, instance=response, data=data)
        return response
        """


class AnswerForm(forms.ModelForm):
    description = RichTextUploadingField('Description')

    class Meta:
        model = Question
        fields = ['answer']

    def clean(self):
        cleaned_data = super(AnswerForm, self).clean()
        return cleaned_data

    def save(self, commit=True):
        question = super(AnswerForm, self).save(commit=False)
        question.save()
        return question
