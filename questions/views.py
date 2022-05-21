from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
# from django.http.request import HttpRequest
# from django.template import loader
from django.urls import reverse
from django.views import generic

from .models import Question, Choice, QuestionChoice, Category, Quiz
from .forms import AnswerForm, ResponseForm

import random


# Create your views here.
def index(request):
    return render(request, 'questions/base.html')


def question_by_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    questions = Question.objects.filter(category=category)
    quizes = Quiz.objects.filter(category=category)
    context = {
        'category': category,
        'slug': slug,
        'questions': questions,
        'quizes': quizes,
    }
    return render(request, 'questions/question_by_category.html', context)


class DetailView(generic.DetailView):
    model = Question
    template_name = 'questions/question_detail.html'


class QuizesList(generic.ListView):
    model = Quiz
    template_name = 'questions/quizes_list.html'


class QuizDetail(generic.View):
    def get(self, request, *args, **kwargs):
        # print("Kwargs: ", kwargs)
        quiz = get_object_or_404(Quiz, pk=kwargs["pk"])

        step = kwargs.get("step", 0)
        if quiz.is_all_in_one_page():
            template_name = "questions/quiz_detail.html"
        else:
            template_name = "questions/quiz_questions.html"

        form = ResponseForm(quiz=quiz, user=request.user, step=step)

        questions = QuestionChoice.objects.filter(quiz=quiz).order_by('position')
        questions_count = 0
        context = {}
        for question in questions:
            questions_count += 1
            # print("Answer position:", question.answer_position)
            question_choices = question.get_clean_choices()
            context['choices'] = question_choices
            # print("Question choices:", question_choices)
            for choice in question_choices:
                print("Choice: ", choice)

        context.update({
            "response_form": form,
            "quiz": quiz,
            "questions": questions,
            "questions_count": questions_count,
            # "question_choices": question_choices,
            "category": quiz.category,
            "step": step,
        })

        return render(request, template_name, context)
"""


class QuizDetail(generic.UpdateView):
    model = Quiz
    form_class = ResponseForm
    print(form_class)
    template_name = 'questions/quiz_questions.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/login/')
        print("Request: ", request)
        quiz = get_object_or_404(Quiz, pk=int(kwargs['pk']))
        if quiz.is_all_in_one_page() is True:
            template_name = 'questions/one_page_questions.html'
        else:
            template_name = 'questions/quiz_questions.html'

        print("Dispatch kwargs: ", kwargs)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        print("Form kwargs: ", kwargs)
        quiz = kwargs["instance"]
        if quiz.is_all_in_one_page() is True:
            template_name = 'questions/one_page_questions.html'
        else:
            template_name = 'questions/quiz_questions.html'
        print("Quiz: ", quiz.is_all_in_one_page())
        kwargs.update({"quiz": kwargs["instance"]})
        kwargs.update({'user': self.request.user})
        print(kwargs)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        step = kwargs.get("step", 0)
        print("Step: ", step)
        print("Context: ", context)
        quiz = context["quiz"]
        user = self.request.user
        print("Quiz: ", quiz)
        print("User", user)
        questions_count = 0
        if quiz.is_all_in_one_page() is True:
            template_name = 'questions/one_page_questions.html'
        else:
            template_name = 'questions/quiz_questions.html'
        form = ResponseForm(quiz=self.object, user=user, step=step)

        questions = QuestionChoice.objects.filter(quiz=quiz).order_by('position')
        for question in questions:
            questions_count += 1
            print("Answer position:", question.answer_position)
            # question_choices = question.get_choices()

        context['form'] = form
        context['questions_count'] = questions_count
        context['questions'] = questions
        print(context)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.save()
        return super(Quiz, self).form_valid(form)
"""

def question_detail(request, pk):
    question = get_object_or_404(Question, pk=pk)
    return render(request, 'questions/question_detail.html', {
        'question': question,
    })


def add_answer(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    form = AnswerForm()
    if request.method == 'POST':
        form = AnswerForm(request.POST, instance=question)
        context = {
            'form': form,
            'question': question
        }

        if form.is_valid():
            new_answer = form.save()
            new_answer.save()
            context['answer'] = new_answer
            return redirect(reverse('detail',
                                    args=[question.id]))

        else:
            question = get_object_or_404(Question, pk=question_id)
            form = AnswerForm()

    return render(request, 'questions/add_answer.html', {
        'form': form,
        'question': question
    })


def update_answer(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    form = AnswerForm(request.POST or None, instance=question)
    context = {
        'form': form,
        'question': question,
    }
    print(context)
    if request.method == 'POST':
        new_answer = form.save(commit=False)
        new_answer.save()
        context = {
            'question': question,
        }
        print("Updated context: ", context)
        return redirect(reverse('detail', args=[question.id]))

    else:
        question = get_object_or_404(Question, pk=question_id)
        form = AnswerForm(instance=question)

    return render(request, 'questions/answer_update.html', {
        'form': form,
        'question': question,
    })


def delete_answer(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    question.answer = ""
    question.save()
    return redirect(reverse('detail', args=[question.id]))


class ResultView(generic.DetailView):
    model = Question
    template_name = 'questions/results.html'


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'questions/question_detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('results',
                                            args=(question.id,)))


def random_questions(request):
    questions = Question.objects.order_by('question_text')
    question = random.choice(questions)
    print(question)
    template_name = 'questions/random_question.html'
    return render(request, template_name, {'question': question})
