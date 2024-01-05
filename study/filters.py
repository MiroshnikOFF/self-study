from django_filters import FilterSet, CharFilter, NumberFilter

from study.models import Section, Lesson, Test


class SectionFilter(FilterSet):
    """ Фильтрует категории по названию без учета регистра """

    name = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Section
        fields = ('name',)


class LessonFilter(FilterSet):
    """ Фильтрует уроки по названию без учета регистра """

    name = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Lesson
        fields = ('name',)


class TestFilter(FilterSet):
    """ Фильтрует тесты по названию без учета регистра """

    name = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Test
        fields = ('name',)


class StatisticsFilter(FilterSet):
    """
    Фильтрует статистику по email студента без учета регистра
    и по количеству пройденных тестов не менее указанного
    """

    user_email = CharFilter(lookup_expr='icontains', label='Email студента содержит')
    test_count = NumberFilter(lookup_expr='gte', label='Количество пройденных тестов не менее')

    class Meta:
        fields = ('user_email', 'test_count',)
