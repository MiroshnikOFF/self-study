from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import authenticate
from rest_framework import status

from study.forms import SectionForm
from study.models import Section, Lesson, Test, Question, Answer, UserAnswer
from study.views.ssr_views import SectionCreateView
from users.models import User


# class EmailBackend(ModelBackend):
#     def authenticate(self, request, email=None, password=None, **kwargs):
#         # try:
#         #     user = User.objects.get(email=email)
#         # except User.DoesNotExist:
#         #     return None
#         # else:
#         #     # if user.check_password(password):
#         print(555)
#         return 555


class StudyTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            email='test@test.ru',
            is_staff=True,
            is_superuser=True,
            is_active=True
        )
        self.user.set_password('0000')
        self.user.save()

        self.section = Section.objects.create(name='Section')
        self.lesson = Lesson.objects.create(name='Lesson', section=self.section, author=self.user)
        self.test = Test.objects.create(name='Test', lesson=self.lesson)
        self.question = Question.objects.create(question='Question', test=self.test)
        # self.answer = Answer.objects.create(answer='It is a test', question=self.question)
        # self.user_answer = UserAnswer.objects.create(user=self.user, answer=self.answer)

    def test_home_get(self):
        """ Тестирование получения главной страницы """
        # user = authenticate(request=self.client, username=self.user.email, password='0000')
        response = self.client.get(reverse('study:home'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, template_name='study/home.html')

    def test_section_create(self):
        """ Тестирование создания раздела """
        self.client.login(user=self.user)

        response = self.client.get(reverse('study:section_create'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('study:section_create'))

        data = {'name': 'New section'}
        response = self.client.post(reverse('study:section_create'), data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('study:section_create'))

    def test_section_list(self):
        """ Тестирование получения списка разделов """
        response = self.client.get(reverse('study:sections'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('study:sections'))

    def test_section_detail(self):
        """ Тестирование получения раздела """
        response = self.client.get(reverse(viewname='study:section', kwargs={'pk': self.section.pk}))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse(viewname='study:section',
                                                                                   kwargs={'pk': self.section.pk}))

    def test_section_update(self):
        """ Тестирование изменения раздела """
        response = self.client.get(reverse(viewname='study:section_update', kwargs={'pk': self.section.pk}))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse(viewname='study:section_update',
                                                                                   kwargs={'pk': self.section.pk}))
        data = {'name': 'New section'}
        response = self.client.put(reverse(viewname='study:section_update', kwargs={'pk': self.section.pk}), data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse(viewname='study:section_update',
                                                                                   kwargs={'pk': self.section.pk}))

    def test_section_delete(self):
        """ Тестирование удаления раздела """
        response = self.client.get(reverse(viewname='study:section_delete', kwargs={'pk': self.section.pk}))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse(viewname='study:section_delete',
                                                                                   kwargs={'pk': self.section.pk}))

    def test_lesson_create(self):
        """ Тестирование создания урока """
        response = self.client.get(reverse('study:lesson_create'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('study:lesson_create'))

        data = {'name': 'New lesson'}
        response = self.client.post(reverse('study:lesson_create'), data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('study:lesson_create'))

    def test_lesson_list(self):
        """ Тестирование получения списка уроков """
        response = self.client.get(reverse('study:lessons'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('study:lessons'))

    def test_lesson_detail(self):
        """ Тестирование получения урока """
        response = self.client.get(reverse(viewname='study:lesson', kwargs={'pk': self.lesson.pk}))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse(viewname='study:lesson',
                                                                                   kwargs={'pk': self.lesson.pk}))

    def test_lesson_update(self):
        """ Тестирование изменения урока """
        response = self.client.get(reverse(viewname='study:lesson_update', kwargs={'pk': self.lesson.pk}))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse(viewname='study:lesson_update',
                                                                                   kwargs={'pk': self.lesson.pk}))
        data = {'name': 'New lesson'}
        response = self.client.put(reverse(viewname='study:lesson_update', kwargs={'pk': self.lesson.pk}), data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse(viewname='study:lesson_update',
                                                                                   kwargs={'pk': self.lesson.pk}))

    def test_lesson_delete(self):
        """ Тестирование удаления урока """
        response = self.client.get(reverse(viewname='study:lesson_delete', kwargs={'pk': self.lesson.pk}))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse(viewname='study:lesson_delete',
                                                                                   kwargs={'pk': self.lesson.pk}))

    def test_test_create(self):
        """ Тестирование создания теста """
        response = self.client.get(reverse('study:test_create'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('study:test_create'))

        data = {'name': 'New test'}
        response = self.client.post(reverse('study:test_create'), data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('study:test_create'))

    def test_test_list(self):
        """ Тестирование получения списка тестов """
        response = self.client.get(reverse('study:tests'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('study:tests'))

    def test_test_detail(self):
        """ Тестирование получения теста """
        response = self.client.get(reverse(viewname='study:test', kwargs={'pk': self.test.pk}))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse(viewname='study:test',
                                                                                   kwargs={'pk': self.test.pk}))

    def test_test_update(self):
        """ Тестирование изменения теста """
        response = self.client.get(reverse(viewname='study:test_update', kwargs={'pk': self.test.pk}))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse(viewname='study:test_update',
                                                                                   kwargs={'pk': self.test.pk}))
        data = {'name': 'New test'}
        response = self.client.put(reverse(viewname='study:test_update', kwargs={'pk': self.test.pk}), data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse(viewname='study:test_update',
                                                                                   kwargs={'pk': self.test.pk}))

    def test_test_delete(self):
        """ Тестирование удаления теста """
        response = self.client.get(reverse(viewname='study:test_delete', kwargs={'pk': self.test.pk}))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse(viewname='study:test_delete',
                                                                                   kwargs={'pk': self.test.pk}))

    def test_question_update(self):
        """ Тестирование изменения вопроса """
        response = self.client.get(reverse(viewname='study:question_update', kwargs={'pk': self.question.pk}))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse(viewname='study:question_update',
                                                                                   kwargs={'pk': self.question.pk}))
        data = {'question': 'New question'}
        response = self.client.put(reverse(viewname='study:question_update', kwargs={'pk': self.question.pk}), data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse(viewname='study:question_update',
                                                                                   kwargs={'pk': self.question.pk}))

    def test_testing(self):
        """ Тестирование прохождения теста """
        response = self.client.get(
            reverse(viewname='study:testing', kwargs={'test_pk': self.test.pk, 'question_index': 1}))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse(viewname='study:testing',
                                                                                   kwargs={'test_pk': self.test.pk,
                                                                                           'question_index': 1}))

    def test_next_question(self):
        """ Тестирование получения следующего ответа """
        response = self.client.get(
            reverse(viewname='study:next_question', kwargs={'test_pk': self.test.pk, 'question_index': 1}))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse(viewname='study:next_question',
                                                                                   kwargs={'test_pk': self.test.pk,
                                                                                           'question_index': 1}))

    def test_report(self):
        """ Тестирование получения отчета успеваемости студента """
        response = self.client.get(reverse(viewname='study:report', kwargs={'test_pk': self.test.pk}))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse(viewname='study:report',
                                                                                   kwargs={'test_pk': self.test.pk}))

    def test_statistics(self):
        """ Тестирование получения статистики """
        response = self.client.get(reverse('study:statistics'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('study:statistics', ))

# class SectionCreateViewTest(TestCase):
#     def setUp(self):
#         self.user = User.objects.create(
#             email='test@test.ru',
#             is_staff=True,
#             is_superuser=True,
#             is_active=True
#         )
#         self.url = reverse('study:section_create')
#         self.client.login(user=self.user)
#
#     def test_section_create_view_with_permission(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'study/section_create.html')
#
#         # Проверяем, что форма рендерится корректно
#         self.assertIsInstance(response.context['form'], SectionForm)
#
#         # Проверяем, что при отправке правильных данных создается новый раздел
#         data = {'name': 'Test Section'}
#         response = self.client.post(self.url, data)
#         self.assertEqual(response.status_code, 302)
#
#         section = Section.objects.get(name='Test Section')
#         self.assertEqual(section.name, 'Test Section')
#
#     def test_section_create_view_without_permission(self):
#         # Удаляем необходимое разрешение у пользователя
#         self.user.user_permissions.remove('study.add_section')
#
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 403)
#         self.assertRaises(PermissionDenied, self.client.post, self.url, {'name': 'Test Section'})

# class SectionCreateViewTest(TestCase):
#     def setUp(self):
#         self.user = User.objects.create(
#             email='test@test.ru',
#             is_staff=True,
#             is_superuser=True,
#             is_active=True
#         )
#         self.user.set_password('0000')
#         self.user.save()
#
#         self.client.login(email=self.user.email, password=self.user.password)
#
#     def test_section_create(self):
#         # Создаем объект формы, передавая нужные данные
#         form_data = {
#             'name': 'Test Section',
#             'description': 'Test Description'
#         }
#         form = SectionForm(data=form_data)
#
#         # Посылаем POST запрос на указанный URL
#         response = self.client.post(reverse('study:section_create'), data=form_data)
#
#         # # Проверяем, что произошел редирект на указанный URL
#         # self.assertRedirects(response, reverse('study:sections'))
#     #
#         # Проверяем, что созданная секция соответствует отправленным данным
#         section = Section.objects.filter(name='Test Section')
#         print(section)
#         # self.assertEqual(section.description, 'Test Description')
