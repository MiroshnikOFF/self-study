from django.urls import path
from rest_framework import routers

from study.apps import StudyConfig
from study.views.api_views import SectionViewSet, LessonViewSet, TestViewSet, QuestionViewSet, AnswerViewSet, \
    ReportAPIView, StatisticsListAPIView

app_name = StudyConfig.name

router = routers.DefaultRouter()
router.register('sections', SectionViewSet, basename='sections')
router.register('lessons', LessonViewSet, basename='lessons')
router.register('tests', TestViewSet, basename='tests')
router.register('questions', QuestionViewSet, basename='questions')
router.register('answers', AnswerViewSet, basename='answers')

urlpatterns = [
    path('report/', ReportAPIView.as_view(), name='report'),
    path('statistics/', StatisticsListAPIView.as_view(), name='statistics'),
]

urlpatterns += router.urls
