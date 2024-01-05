from django.urls import path

from study.apps import StudyConfig
from study.views.ssr_views import (HomeTemplateView, SectionCreateView, SectionListView, SectionDetailView,
                                   SectionUpdateView,
                                   SectionDeleteView, LessonCreateView, LessonListView, LessonDetailView,
                                   LessonUpdateView,
                                   LessonDeleteView, TestCreateView, TestListView, TestDetailView, TestUpdateView,
                                   TestDeleteView, next_question_view, QuestionUpdateView, testing,
                                   report, statistics)

app_name = StudyConfig.name

urlpatterns = [
    path('', HomeTemplateView.as_view(), name='home'),

    path('sections/', SectionListView.as_view(), name='sections'),
    path('sections/create/', SectionCreateView.as_view(), name='section_create'),
    path('sections/<int:pk>/', SectionDetailView.as_view(), name='section'),
    path('sections/<int:pk>/update/', SectionUpdateView.as_view(), name='section_update'),
    path('sections/<int:pk>/delete/', SectionDeleteView.as_view(), name='section_delete'),

    path('lessons/', LessonListView.as_view(), name='lessons'),
    path('lessons/create/', LessonCreateView.as_view(), name='lesson_create'),
    path('lessons/<int:pk>/', LessonDetailView.as_view(), name='lesson'),
    path('lessons/<int:pk>/update/', LessonUpdateView.as_view(), name='lesson_update'),
    path('lessons/<int:pk>/delete/', LessonDeleteView.as_view(), name='lesson_delete'),

    path('tests/', TestListView.as_view(), name='tests'),
    path('tests/create/', TestCreateView.as_view(), name='test_create'),
    path('tests/<int:pk>/', TestDetailView.as_view(), name='test'),
    path('tests/<int:pk>/update/', TestUpdateView.as_view(), name='test_update'),
    path('tests/<int:pk>/delete/', TestDeleteView.as_view(), name='test_delete'),

    path('question/<int:pk>/update/', QuestionUpdateView.as_view(), name='question_update'),

    path('testing/<int:test_pk>/<int:question_index>/', testing, name='testing'),
    path('question/<int:test_pk>/<int:question_index>/next/', next_question_view, name='next_question'),
    path('testing/<int:test_pk>/report/', report, name='report'),
    path('statistics/', statistics, name='statistics'),
]
