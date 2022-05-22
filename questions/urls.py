from django.urls import path, re_path
from django.conf.urls import include

from . import views

urlpatterns = [
    path('', views.index, name='base'),
    path('question/', views.random_questions, name='random-question'),
    path('<int:pk>/', views.question_detail, name='detail'),
    path('<slug:slug>/',  views.question_by_category, name='category'),
    path('<int:pk>/results/', views.ResultView.as_view(), name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
    path('<int:question_id>/add/answer/', views.add_answer, name='add-answer'),
    path(
        '<int:question_id>/update/answer/',
        views.update_answer, name='update-answer'),
    path(
        '<int:question_id>/delete/answer/',
        views.delete_answer, name='delete-answer'),
    path('quizes/', views.QuizesList.as_view(), name='quizes'),
    path('quizes/<int:pk>/', views.QuizDetail.as_view(), name='quiz_detail'),
    path('quizes/<int:pk>/<int:step>', views.QuizDetail.as_view(), name='quiz_detail_step'),
    path('quizes/confirm/<int:pk>', views.ConfirmView.as_view(), name="quiz-confirmation"),
    re_path(r'^nested_admin/', include('nested_admin.urls')),
]
