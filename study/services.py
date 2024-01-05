from django.db.models import F, Count, Q

from study.models import UserAnswer


def get_statistics():
    """ Получает queryset статистики успеваемости всех студентов """

    return UserAnswer.objects.select_related('answer__question__test', 'user').values(
            user_pk=F('user__id'),
            user_email=F('user__email'),
        ).annotate(
            test_count=Count('answer__question__test__id', distinct=True),
            answer_count=Count('answer_id', distinct=True),
            correct_answers_count=Count('answer_id', filter=Q(answer__is_correct=True), distinct=True),
        ).order_by('user__id')
