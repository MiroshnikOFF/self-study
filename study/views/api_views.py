from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from study.services import get_statistics
from study.models import Section, Lesson, Test, Question, Answer, UserAnswer
from study.pagination import SectionPaginator, LessonPaginator, TestPaginator, QuestionPaginator, AnswerPaginator, \
    StatisticPaginator
from study.serializers import SectionSerializer, LessonSerializer, TestSerializer, QuestionSerializer, AnswerSerializer, \
    ReportSerializer, Statistics, AnswerShortSerializer
from study.permissions import IsStaff, ReadOnly, IsStaffOrReadOnly


class SectionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, IsStaffOrReadOnly,)
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    pagination_class = SectionPaginator


class LessonViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, IsStaffOrReadOnly,)
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = LessonPaginator

    # Фильтр для поиска по pk раздела
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('section', 'author',)

    def perform_create(self, serializer):
        """ Сохраняет текущего пользователя в поле author урока """
        new_lesson = serializer.save()
        new_lesson.author = self.request.user
        new_lesson.save()


class TestViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, IsStaffOrReadOnly,)
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    pagination_class = TestPaginator

    # Фильтр для поиска по pk урока
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('lesson',)


class QuestionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, IsStaffOrReadOnly,)
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    pagination_class = QuestionPaginator

    # Фильтр для поиска по pk теста
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('test',)


class AnswerViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, IsStaffOrReadOnly,)
    queryset = Answer.objects.all()
    pagination_class = AnswerPaginator

    # Фильтр для поиска по pk вопроса
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('question',)

    def get_serializer_class(self):
        """
        Если текущий пользователь не является персоналом, то возвращает сериализатор без признака правильного ответа
        """
        if self.request.user.is_staff:
            return AnswerSerializer
        return AnswerShortSerializer


class ReportAPIView(APIView):
    """ Контроллер для получения отчета по успеваемости текущего пользователя """

    permission_classes = (IsAuthenticated, ReadOnly)

    def get(self, request):
        # Получение количества пройденных тестов
        completed_tests = UserAnswer.objects.filter(user_id=request.user.pk).values('answer__question__test').annotate(
            total=Count('answer__question__test')).count()

        # Получение количества всех ответов пользователя
        all_answers = len(request.user.answers.all())

        # Получение количества правильных ответов пользователя
        correct_answers = UserAnswer.objects.filter(user_id=request.user.pk, answer__is_correct=True).count()

        # Получение количества неправильных ответов пользователя
        incorrect_answers = all_answers - correct_answers

        # Получение доли правильных ответов от общего количества в процентах
        if all_answers == 0:
            correct_answers_percentage = 0
        else:
            correct_answers_percentage = correct_answers / all_answers * 100

        data = {
            'completed_tests': completed_tests,
            'all_answers': all_answers,
            'correct_answers': correct_answers,
            'incorrect_answers': incorrect_answers,
            'correct_answers_percentage': correct_answers_percentage,
        }
        serializer = ReportSerializer(data)

        return Response(serializer.data)


class StatisticsListAPIView(generics.ListAPIView):
    """
    Контроллер для получения статистики успеваемости по всем студентам.
    Только для персонала!
    """

    permission_classes = (IsAuthenticated, IsStaff, ReadOnly)
    serializer_class = Statistics
    pagination_class = StatisticPaginator

    # Фильтр для поиска по pk или email пользователя
    filter_backends = (SearchFilter,)
    search_fields = ('user_pk', 'user_email',)

    def get_queryset(self):
        """ Получает статистику по всем студентам """
        return get_statistics()
