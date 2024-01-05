from django.db.models import Count
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, DetailView, CreateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse_lazy, reverse
from django.forms import inlineformset_factory

from study.services import get_statistics
from study.filters import SectionFilter, LessonFilter, TestFilter, StatisticsFilter
from study.forms import SectionForm, LessonForm, TestForm, QuestionForm, AnswerForm
from study.models import Section, Lesson, Test, Question, Answer, UserAnswer


class HomeTemplateView(TemplateView):
    """ Контроллер для главной страницы """

    template_name = 'study/home.html'

    def get_context_data(self, **kwargs):
        """ Получает статистику успеваемости текущего пользователя для вывода на главной странице """

        context_data = super().get_context_data()
        user = self.request.user

        if user.is_authenticated:
            # Количество всех ответов
            all_answers_counter = len(user.answers.all())

            # Количество правильных ответов
            correct_answers_counter = UserAnswer.objects.filter(user_id=user.pk, answer__is_correct=True).count()

            # Количество неправильных ответов
            incorrect_answers_counter = all_answers_counter - correct_answers_counter

            # Доля правильных ответов от всех ответов пользователя в процентах
            if all_answers_counter == 0:
                correct_answers_percentage = 0
            else:
                correct_answers_percentage = correct_answers_counter / all_answers_counter * 100

            # Количество пройденных тестов
            completed_tests = UserAnswer.objects.filter(user_id=user.pk).values('answer__question__test').annotate(
                total=Count('answer__question__test')).count()

            context_data['completed_tests'] = completed_tests
            context_data['incorrect_answers'] = incorrect_answers_counter
            context_data['correct_answers'] = correct_answers_counter
            context_data['correct_answers_percentage'] = round(correct_answers_percentage)

        return context_data


class SectionCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'study.add_section'
    model = Section
    form_class = SectionForm
    success_url = reverse_lazy('study:sections')


class SectionListView(LoginRequiredMixin, ListView):
    model = Section

    def get_queryset(self):
        """ Фильтрует queryset """

        queryset = super().get_queryset()
        filtered_data = SectionFilter(self.request.GET, queryset=queryset)
        return filtered_data.qs

    def get_context_data(self, *args, **kwargs):
        """ Добавляет filter_set в context_data """

        context_data = super().get_context_data(*args, **kwargs)
        filtered_data = SectionFilter(self.request.GET, queryset=self.queryset)
        context_data['filter'] = filtered_data
        return context_data


class SectionDetailView(LoginRequiredMixin, DetailView):
    model = Section

    def get_context_data(self, **kwargs):
        """ Добавляет queryset всех уроков раздела в context_data """

        context_data = super().get_context_data(**kwargs)
        context_data['lessons'] = Lesson.objects.filter(section_id=kwargs['object'].pk)
        return context_data


class SectionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'study.change_section'
    model = Section
    form_class = SectionForm
    success_url = reverse_lazy('study:sections')


class SectionDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'study.delete_section'
    model = Section
    success_url = reverse_lazy('study:sections')


class LessonCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'study.add_lesson'
    model = Lesson
    form_class = LessonForm
    success_url = reverse_lazy('study:lessons')

    def form_valid(self, form):
        """ Добавляет текущего пользователя в поле author урока """

        self.object = form.save()
        self.object.author = self.request.user
        self.object.save()
        return super().form_valid(form)


class LessonListView(LoginRequiredMixin, ListView):
    model = Lesson

    def get_queryset(self):
        """ Фильтрует queryset """

        queryset = super().get_queryset()
        filtered_data = LessonFilter(self.request.GET, queryset=queryset)
        return filtered_data.qs

    def get_context_data(self, *args, **kwargs):
        """ Добавляет filter_set в context_data """

        context_data = super().get_context_data(*args, **kwargs)
        filtered_data = LessonFilter(self.request.GET, queryset=self.queryset)
        context_data['filter'] = filtered_data
        return context_data


class LessonDetailView(LoginRequiredMixin, DetailView):
    model = Lesson

    def get_context_data(self, **kwargs):
        """ Добавляет queryset всех тестов урока в context_data """

        context_data = super().get_context_data(**kwargs)
        context_data['tests'] = Test.objects.filter(lesson_id=kwargs['object'].pk)
        return context_data


class LessonUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'study.change_lesson'
    model = Lesson
    form_class = LessonForm
    success_url = reverse_lazy('study:lessons')


class LessonDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'study.delete_lesson'
    model = Lesson
    success_url = reverse_lazy('study:lessons')


class TestCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'study.add_test'
    model = Test
    form_class = TestForm
    success_url = reverse_lazy('study:tests')


class TestListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'study.view.test'
    model = Test

    def get_queryset(self):
        """ Фильтрует queryset """

        queryset = super().get_queryset()
        filtered_data = TestFilter(self.request.GET, queryset=queryset)
        return filtered_data.qs

    def get_context_data(self, *args, **kwargs):
        """ Добавляет filter_set в context_data """

        context_data = super().get_context_data(*args, **kwargs)
        filtered_data = TestFilter(self.request.GET, queryset=self.queryset)
        context_data['filter'] = filtered_data
        return context_data


class TestDetailView(LoginRequiredMixin, DetailView):
    model = Test


class TestUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'study.change_test'
    model = Test
    form_class = TestForm

    def get_success_url(self):
        """ Перенаправляет на страницу информации о тесте """

        return reverse('study:test', args=[self.object.pk])

    def get_context_data(self, **kwargs):
        """ Добавляет formset и список pk всех вопросов текущего теста """

        context_data = super().get_context_data(**kwargs)
        QuestionFormset = inlineformset_factory(Test, Question, form=QuestionForm, extra=10)
        if self.request.method == 'POST':
            formset = QuestionFormset(self.request.POST, instance=self.object)
        else:
            formset = QuestionFormset(instance=self.object)

        questions_pk = [obj.pk for obj in formset.queryset]

        context_data['formset'] = formset
        context_data['questions_pk'] = questions_pk
        return context_data

    def form_valid(self, form):
        """ Сохраняет данные из formset """

        context_data = self.get_context_data()
        formset = context_data['formset']
        self.object = form.save()
        if formset.is_valid():
            formset.instance = self.object
            formset.save()
        return super().form_valid(form)


class TestDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'study.delete_test'
    model = Test
    success_url = reverse_lazy('study:tests')


class QuestionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'study.change.question'
    model = Question
    form_class = QuestionForm

    def get_success_url(self):
        """ Перенаправляет на страницу редактирования теста текущего урока """

        return reverse('study:test_update', args=[self.object.test.pk])

    def get_context_data(self, **kwargs):
        """ Добавляет formset всех ответов текущего вопроса """

        context_data = super().get_context_data(**kwargs)
        AnswerFormset = inlineformset_factory(Question, Answer, form=AnswerForm, extra=6)
        if self.request.method == 'POST':
            formset = AnswerFormset(self.request.POST, instance=self.object)
        else:
            formset = AnswerFormset(instance=self.object)

        context_data['formset'] = formset
        return context_data

    def form_valid(self, form):
        """ Сохраняет данные из formset """

        context_data = self.get_context_data()
        formset = context_data['formset']
        self.object = form.save()
        if formset.is_valid():
            formset.instance = self.object
            formset.save()
        return super().form_valid(form)


@login_required
def testing(request, test_pk: int, question_index: int):
    """ Контроллер для проведения тестирования """

    # Получает объекта текущего вопроса по question_index
    if question_index < Question.objects.filter(test_id=test_pk).order_by('pk').first().pk:
        current_question = Question.objects.filter(test_id=test_pk).order_by('pk').first()
        question_index = current_question.pk
    else:
        current_question = Question.objects.filter(test_id=test_pk, pk__gte=question_index).order_by('pk').first()

    # Если текущий пользователь уже отвечал на текущий вопрос, то перезаписывает его в БД
    if UserAnswer.objects.filter(user_id=request.user.pk, answer__question__id=current_question.pk).exists():
        UserAnswer.objects.filter(user_id=request.user.pk, answer__question__id=current_question.pk).delete()

    # Получает queryset вариантов ответа на текущий вопрос
    answers = Answer.objects.filter(question_id=current_question.pk).order_by('?')

    if request.method == 'POST':
        # Если пользователь не выбрал ни один из вариантов ответа,
        # то повторно рендерит страницу с required в context_data
        if not request.POST.get(str(current_question.pk)):
            context_data = {'question': current_question, 'answers': answers, 'required': True}
            return render(request, 'study/testing.html', context_data)
        else:
            # Вносит ответ пользователя в БД
            answer_pk = request.POST.get(str(current_question.pk))
            UserAnswer.objects.create(user_id=request.user.pk, answer_id=answer_pk)
        # Перенаправляет на контроллер next_question_view
        return redirect('study:next_question', test_pk=test_pk, question_index=question_index)
    context_data = {'question': current_question, 'answers': answers}
    return render(request, 'study/testing.html', context_data)


@login_required
def next_question_view(request, test_pk: int, question_index: int):
    # Если вопрос не является последним в тесте, то добавляет + 1 к question_index
    # и перенаправляет обратно на testing с новым question_index
    if question_index < Question.objects.filter(test_id=test_pk).order_by('pk').last().pk:
        next_question_index = question_index + 1
        return redirect('study:testing', test_pk=test_pk, question_index=next_question_index)
    else:
        # Перенаправляет на страницу отчета о пройденном тесте
        return redirect('study:report', test_pk=test_pk)


@login_required
def report(request, test_pk):
    """ Контроллер для получения отчета о пройденном тесте """

    test = Test.objects.get(pk=test_pk)
    lesson_pk = test.lesson.pk

    # Количество всех вопросов в тесте
    all_questions = test.questions.all().count()

    # Получение вопросов теста и ответов пользователя на пройденный тест
    questions_with_correct_answer = UserAnswer.objects.filter(
        user_id=request.user.pk,
        answer__question__test__id=test_pk
    ).values_list('answer__question__question', 'answer__answer', 'answer__is_correct')

    # Подсчет правильных ответов пользователя на пройденный тест
    correct_answers_count = UserAnswer.objects.filter(
        user_id=request.user.pk,
        answer__is_correct=True, answer__question__test__id=test_pk
    ).count()

    context_data = {
        'lesson_pk': lesson_pk,
        'test_pk': test_pk,
        'answers_count': all_questions,
        'correct_answers_count': correct_answers_count,
        'questions_with_correct_answer': questions_with_correct_answer,
    }
    return render(request, 'study/report.html', context_data)


@login_required
@staff_member_required
def statistics(request):
    """
    Контроллер для получения статистики успеваемости всех студентов.
    Только для персонала!
    """
    # Получает queryset статистики
    queryset = get_statistics()

    # Фильтрует queryset
    filtered_data = StatisticsFilter(request.GET, queryset=queryset)

    # Преобразует queryset в list и добавляет долю правильных ответов в процентах к каждому студенту
    context_list = list(filtered_data.qs)
    for obj in context_list:
        correct_answers_percentage = round(obj['correct_answers_count'] / obj['answer_count'] * 100)
        obj['correct_answers_percentage'] = correct_answers_percentage

    context_data = {'context': context_list, 'filter': filtered_data}
    return render(request, 'study/statistics.html', context_data)
