from rest_framework import serializers

from study.models import Section, Lesson, Test, Answer, Question


class LessonShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lesson
        fields = ('id', 'name',)


class TestShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ('id', 'name',)


class QuestionShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'question',)


class AnswerShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('id', 'answer',)


class SectionSerializer(serializers.ModelSerializer):
    lessons = LessonShortSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = ('id', 'name', 'description', 'preview', 'created', 'lessons',)


class LessonSerializer(serializers.ModelSerializer):
    tests = TestShortSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = ('id', 'section', 'name', 'content', 'preview', 'video_url', 'author', 'tests',)


class TestSerializer(serializers.ModelSerializer):
    questions = QuestionShortSerializer(many=True, read_only=True)

    class Meta:
        model = Test
        fields = ('id', 'lesson', 'name', 'description', 'questions',)


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerShortSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'test', 'question', 'answers',)


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'


class ReportSerializer(serializers.Serializer):
    """ Выводит отчет успеваемости текущего пользователя """

    completed_tests = serializers.IntegerField()
    all_answers = serializers.IntegerField()
    correct_answers = serializers.IntegerField()
    incorrect_answers = serializers.IntegerField()
    correct_answers_percentage = serializers.IntegerField()


class Statistics(serializers.Serializer):
    """ Выводит статистику успеваемости всех студентов """

    user_pk = serializers.IntegerField()
    user_email = serializers.CharField()
    test_count = serializers.IntegerField()
    answer_count = serializers.IntegerField()
    correct_answers_count = serializers.IntegerField()
    incorrect_answers_count = serializers.SerializerMethodField()
    correct_answers_percentage = serializers.SerializerMethodField()

    def get_incorrect_answers_count(self, instance):
        """ Получает количество неправильных ответов """

        return instance['answer_count'] - instance['correct_answers_count']

    def get_correct_answers_percentage(self, instance):
        """ Получает долю правильных ответов от всех ответов студента в процентах """

        return round(instance['correct_answers_count'] / instance['answer_count'] * 100)



