from django.db.models import QuerySet
from django.urls import reverse
from django.test import TestCase
from rest_framework import status

from study.filters import StatisticsFilter, TestFilter, LessonFilter, SectionFilter
from study.models import Section, Lesson, Test, Question, Answer, UserAnswer
from users.models import User


class StudyTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            email='simple@user.ru',
            is_active=True
        )
        self.user.set_password('0000')
        self.user.save()

        self.user_staff = User.objects.create(
            email='staff@user.ru',
            is_staff=True,
            is_superuser=True,
            is_active=True
        )
        self.user_staff.set_password('0000')
        self.user_staff.save()

        self.section = Section.objects.create(name='Section')
        self.lesson = Lesson.objects.create(name='Lesson', section=self.section, author=self.user)
        self.test = Test.objects.create(name='Test', lesson=self.lesson)
        self.question = Question.objects.create(question='Question', test=self.test)
        self.answer = Answer.objects.create(answer='Answer', question=self.question)

    def test_home_get(self):
        """ Тестирование получения главной страницы """
        response = self.client.get(reverse('study:home'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, template_name='study/home.html')

    def test_section_create(self):
        """ Тестирование создания раздела """
        data = {'name': 'New section'}
        # Не авторизованный пользователь
        response = self.client.get(reverse('study:section_create'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('study:section_create'))

        response = self.client.post(reverse('study:section_create'), data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('study:section_create'))

        # Авторизованный пользователь
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('study:section_create'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Авторизованный пользователь со статусом персонала
        self.client.force_login(user=self.user_staff)
        response = self.client.get(reverse('study:section_create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, template_name='study/section_form.html')

        response = self.client.post(reverse('study:section_create'), data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('study:sections'))
        self.assertTrue(Section.objects.filter(name=data['name']).exists())

    def test_section_list(self):
        """ Тестирование получения списка разделов """
        # Не авторизованный пользователь
        response = self.client.get(reverse('study:sections'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('study:sections'))

        # Авторизованный пользователь
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('study:sections'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, template_name='study/section_list.html')
        self.assertEqual(len(response.context['object_list']), Section.objects.all().count())
        self.assertEqual(response.context['object_list'][0], self.section)
        self.assertIn(member='filter', container=response.context)
        self.assertIsInstance(response.context['filter'], SectionFilter)

    def test_section_detail(self):
        """ Тестирование получения раздела """
        kwargs = {'pk': self.section.pk}
        # Не авторизованный пользователь
        response = self.client.get(reverse(viewname='study:section', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse(viewname='study:section',
                                                                                   kwargs=kwargs))
        # Авторизованный пользователь
        self.client.force_login(user=self.user)
        response = self.client.get(reverse(viewname='study:section', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, template_name='study/section_detail.html')
        self.assertEqual(response.context['object'], self.section)
        self.assertEqual(response.context['object'], Section.objects.get(pk=kwargs['pk']))
        self.assertIn(member='lessons', container=response.context)
        self.assertIsInstance(response.context['lessons'], QuerySet)
        self.assertEqual(list(response.context['lessons']), list(Lesson.objects.filter(section=self.section)))

    def test_section_update(self):
        """ Тестирование изменения раздела """
        kwargs = {'pk': self.section.pk}
        data = {'name': 'New section', 'description': 'New description'}
        # Не авторизованный пользователь
        response = self.client.get(reverse(viewname='study:section_update', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse(viewname='study:section_update',
                                                                                   kwargs=kwargs))
        response = self.client.put(reverse(viewname='study:section_update', kwargs=kwargs), data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse(viewname='study:section_update',
                                                                                   kwargs=kwargs))
        # Авторизованный пользователь
        self.client.force_login(user=self.user)
        response = self.client.get(reverse(viewname='study:section_update', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Авторизованный пользователь со статусом персонала
        self.client.force_login(user=self.user_staff)
        response = self.client.get(reverse(viewname='study:section_update', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, template_name='study/section_form.html')

        response = self.client.post(reverse(viewname='study:section_update', kwargs=kwargs), data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('study:sections'))
        self.assertTrue(Section.objects.filter(name=data['name']).exists())
        self.assertEqual(Section.objects.get(name=data['name']).description, data['description'])

    def test_section_delete(self):
        """ Тестирование удаления раздела """
        kwargs = {'pk': self.section.pk}
        # Не авторизованный пользователь
        response = self.client.get(reverse(viewname='study:section_delete', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse(viewname='study:section_delete',
                                                                                   kwargs=kwargs))
        # Авторизованный пользователь
        self.client.force_login(user=self.user)
        response = self.client.get(reverse(viewname='study:section_delete', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Авторизованный пользователь со статусом персонала
        self.client.force_login(user=self.user_staff)
        response = self.client.get(reverse(viewname='study:section_delete', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, template_name='study/section_confirm_delete.html')

        response = self.client.post(reverse(viewname='study:section_delete', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('study:sections'))
        self.assertFalse(Section.objects.filter(pk=kwargs['pk']).exists())

    def test_lesson_create(self):
        """ Тестирование создания урока """
        data = {'name': 'New lesson', 'section': self.section.pk}
        # Не авторизованный пользователь
        response = self.client.get(reverse('study:lesson_create'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('study:lesson_create'))

        response = self.client.post(reverse('study:lesson_create'), data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('study:lesson_create'))

        # Авторизованный пользователь
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('study:lesson_create'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Авторизованный пользователь со статусом персонала
        self.client.force_login(user=self.user_staff)
        response = self.client.get(reverse('study:lesson_create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, template_name='study/lesson_form.html')

        response = self.client.post(reverse('study:lesson_create'), data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('study:lessons'))
        self.assertTrue(Lesson.objects.filter(name=data['name']).exists())
        self.assertEqual(Lesson.objects.get(name=data['name']).author, self.user_staff)

    def test_lesson_list(self):
        """ Тестирование получения списка уроков """
        # Не авторизованный пользователь
        response = self.client.get(reverse('study:lessons'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('study:lessons'))

        # Авторизованный пользователь
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('study:lessons'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, template_name='study/lesson_list.html')
        self.assertEqual(len(response.context['object_list']), Lesson.objects.all().count())
        self.assertEqual(response.context['object_list'][0], self.lesson)
        self.assertIn(member='filter', container=response.context)
        self.assertIsInstance(response.context['filter'], LessonFilter)

    def test_lesson_detail(self):
        """ Тестирование получения урока """
        kwargs = {'pk': self.lesson.pk}
        # Не авторизованный пользователь
        response = self.client.get(reverse(viewname='study:lesson', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse(viewname='study:lesson',
                                                                                   kwargs=kwargs))
        # Авторизованный пользователь
        self.client.force_login(user=self.user)
        response = self.client.get(reverse(viewname='study:lesson', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, template_name='study/lesson_detail.html')
        self.assertEqual(response.context['object'], self.lesson)
        self.assertEqual(response.context['object'], Lesson.objects.get(pk=kwargs['pk']))
        self.assertIn(member='tests', container=response.context)
        self.assertIsInstance(response.context['tests'], QuerySet)
        self.assertEqual(list(response.context['tests']), list(Test.objects.filter(lesson=self.lesson)))

    def test_lesson_update(self):
        """ Тестирование изменения урока """
        kwargs = {'pk': self.lesson.pk}
        data = {'name': 'New lesson', 'section': self.section.pk, 'content': 'Some content'}
        # Не авторизованный пользователь
        response = self.client.get(reverse(viewname='study:lesson_update', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse(viewname='study:lesson_update',
                                                                                   kwargs=kwargs))
        response = self.client.put(reverse(viewname='study:lesson_update', kwargs=kwargs), data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse(viewname='study:lesson_update',
                                                                                   kwargs=kwargs))
        # Авторизованный пользователь
        self.client.force_login(user=self.user)
        response = self.client.get(reverse(viewname='study:lesson_update', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Авторизованный пользователь со статусом персонала
        self.client.force_login(user=self.user_staff)
        response = self.client.get(reverse(viewname='study:lesson_update', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, template_name='study/lesson_form.html')

        response = self.client.post(reverse(viewname='study:lesson_update', kwargs=kwargs), data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('study:lessons'))
        self.assertTrue(Lesson.objects.filter(name=data['name']).exists())
        self.assertEqual(Lesson.objects.get(name=data['name']).content, data['content'])

    def test_lesson_delete(self):
        """ Тестирование удаления урока """
        kwargs = {'pk': self.lesson.pk}
        # Не авторизованный пользователь
        response = self.client.get(reverse(viewname='study:lesson_delete', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse(viewname='study:lesson_delete',
                                                                                   kwargs=kwargs))
        # Авторизованный пользователь
        self.client.force_login(user=self.user)
        response = self.client.get(reverse(viewname='study:lesson_delete', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Авторизованный пользователь со статусом персонала
        self.client.force_login(user=self.user_staff)
        response = self.client.get(reverse(viewname='study:lesson_delete', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, template_name='study/lesson_confirm_delete.html')

        response = self.client.post(reverse(viewname='study:lesson_delete', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('study:lessons'))
        self.assertFalse(Lesson.objects.filter(pk=kwargs['pk']).exists())

    def test_test_create(self):
        """ Тестирование создания теста """
        data = {'name': 'New test', 'lesson': self.lesson.pk}
        # Не авторизованный пользователь
        response = self.client.get(reverse('study:test_create'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('study:test_create'))

        response = self.client.post(reverse('study:test_create'), data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('study:test_create'))

        # Авторизованный пользователь
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('study:test_create'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Авторизованный пользователь со статусом персонала
        self.client.force_login(user=self.user_staff)
        response = self.client.get(reverse('study:test_create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, template_name='study/test_form.html')

        response = self.client.post(reverse('study:test_create'), data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('study:tests'))
        self.assertTrue(Test.objects.filter(name=data['name']).exists())

    def test_test_list(self):
        """ Тестирование получения списка тестов """
        # Не авторизованный пользователь
        response = self.client.get(reverse('study:tests'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('study:tests'))

        # Авторизованный пользователь
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('study:tests'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Авторизованный пользователь со статусом персонала
        self.client.force_login(user=self.user_staff)
        response = self.client.get(reverse('study:tests'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, template_name='study/test_list.html')
        self.assertEqual(len(response.context['object_list']), Test.objects.all().count())
        self.assertEqual(response.context['object_list'][0], self.test)
        self.assertIn(member='filter', container=response.context)
        self.assertIsInstance(response.context['filter'], TestFilter)

    def test_test_detail(self):
        """ Тестирование получения теста """
        kwargs = {'pk': self.test.pk}
        # Не авторизованный пользователь
        response = self.client.get(reverse(viewname='study:test', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse(viewname='study:test',
                                                                                   kwargs=kwargs))
        # Авторизованный пользователь
        self.client.force_login(user=self.user)
        response = self.client.get(reverse(viewname='study:test', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, template_name='study/test_detail.html')
        self.assertEqual(response.context['object'], self.test)
        self.assertEqual(response.context['object'], Test.objects.get(pk=kwargs['pk']))

    def test_test_update(self):
        """ Тестирование изменения теста """
        kwargs = {'pk': self.test.pk}
        data = {'name': 'New test', 'description': 'Some description', 'lesson': self.lesson.pk}
        # Не авторизованный пользователь
        response = self.client.get(reverse(viewname='study:test_update', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse(viewname='study:test_update',
                                                                                   kwargs=kwargs))
        response = self.client.put(reverse(viewname='study:test_update', kwargs=kwargs), data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse(viewname='study:test_update',
                                                                                   kwargs=kwargs))
        # Авторизованный пользователь
        self.client.force_login(user=self.user)
        response = self.client.get(reverse(viewname='study:test_update', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Авторизованный пользователь со статусом персонала
        self.client.force_login(user=self.user_staff)
        response = self.client.get(reverse(viewname='study:test_update', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, template_name='study/test_form.html')
        self.assertIn(member='formset', container=response.context)
        self.assertEqual(list(response.context['formset'].queryset), list(Question.objects.filter(test=self.test)))
        self.assertIn(member='questions_pk', container=response.context)
        self.assertIsInstance(response.context['questions_pk'], list)

        response = self.client.post(reverse(viewname='study:test_update', kwargs=kwargs), data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse(viewname='study:test', kwargs=kwargs))
        self.assertTrue(Test.objects.filter(name=data['name']).exists())
        self.assertEqual(Test.objects.get(name=data['name']).description, data['description'])

    def test_test_delete(self):
        """ Тестирование удаления теста """
        kwargs = {'pk': self.test.pk}
        # Не авторизованный пользователь
        response = self.client.get(reverse(viewname='study:test_delete', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse(viewname='study:test_delete',
                                                                                   kwargs=kwargs))
        # Авторизованный пользователь
        self.client.force_login(user=self.user)
        response = self.client.get(reverse(viewname='study:test_delete', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Авторизованный пользователь со статусом персонала
        self.client.force_login(user=self.user_staff)
        response = self.client.get(reverse(viewname='study:test_delete', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, template_name='study/test_confirm_delete.html')

        response = self.client.post(reverse(viewname='study:test_delete', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('study:tests'))
        self.assertFalse(Test.objects.filter(pk=kwargs['pk']).exists())

    def test_question_update(self):
        """ Тестирование изменения вопроса """
        kwargs = {'pk': self.question.pk}
        data = {'question': 'New question', 'test': self.test.pk}
        # Не авторизованный пользователь
        response = self.client.get(reverse(viewname='study:question_update', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse(viewname='study:question_update',
                                                                                   kwargs=kwargs))
        response = self.client.put(reverse(viewname='study:question_update', kwargs=kwargs), data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse(viewname='study:question_update',
                                                                                   kwargs=kwargs))
        # Авторизованный пользователь
        self.client.force_login(user=self.user)
        response = self.client.get(reverse(viewname='study:question_update', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Авторизованный пользователь со статусом персонала
        self.client.force_login(user=self.user_staff)
        response = self.client.get(reverse(viewname='study:question_update', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, template_name='study/question_form.html')
        self.assertIn(member='formset', container=response.context)
        self.assertEqual(list(response.context['formset'].queryset), list(Answer.objects.filter(question=self.question)))

        response = self.client.post(reverse(viewname='study:question_update', kwargs=kwargs), data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse(viewname='study:test_update', kwargs={'pk': self.question.test.pk}))
        self.assertTrue(Question.objects.filter(question=data['question']).exists())

    def test_testing(self):
        """ Тестирование прохождения теста """
        kwargs = {'test_pk': self.test.pk, 'question_index': 1}
        data = {str(self.question.pk): [self.answer.pk]}
        # Не авторизованный пользователь
        response = self.client.get(
            reverse(viewname='study:testing', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse(viewname='study:testing',
                                                                                   kwargs=kwargs))
        # Авторизованный пользователь
        self.client.force_login(user=self.user)
        response = self.client.get(reverse(viewname='study:testing', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, template_name='study/testing.html')
        self.assertIn(member='question', container=response.context)
        self.assertIn(member='answers', container=response.context)
        question = response.context['question']
        answers = response.context['answers']
        self.assertIsInstance(question, Question)
        self.assertIsInstance(answers, QuerySet)

        response = self.client.post(reverse(viewname='study:testing', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, template_name='study/testing.html')
        self.assertIn(member='question', container=response.context)
        self.assertIn(member='answers', container=response.context)
        self.assertIn(member='required', container=response.context)
        question = response.context['question']
        answers = response.context['answers']
        self.assertIsInstance(question, Question)
        self.assertIsInstance(answers, QuerySet)
        self.assertTrue(response.context['required'])

        response = self.client.post(reverse(viewname='study:testing', kwargs=kwargs), data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertTrue(UserAnswer.objects.filter(user=self.user, answer=self.answer).exists())

    def test_next_question(self):
        """ Тестирование получения следующего ответа """
        kwargs = {'test_pk': self.test.pk, 'question_index': 1}
        report_kwargs = {'test_pk': self.test.pk}
        # Не авторизованный пользователь
        response = self.client.get(reverse(viewname='study:next_question', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse(viewname='study:next_question',
                                                                                   kwargs=kwargs))
        # Авторизованный пользователь
        self.client.force_login(user=self.user)
        response = self.client.get(reverse(viewname='study:next_question', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        if Question.objects.all().first().pk > 1:
            self.assertEqual(response.status_code, status.HTTP_302_FOUND)
            kwargs['question_index'] += 1
            self.assertRedirects(response, reverse(viewname='study:testing', kwargs=kwargs))
        else:
            self.assertRedirects(response, reverse(viewname='study:report', kwargs=report_kwargs))

        Question.objects.create(question='One more question', test=self.test)
        response = self.client.get(reverse(viewname='study:next_question', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        kwargs['question_index'] += 1
        self.assertRedirects(response, reverse(viewname='study:testing', kwargs=kwargs))

    def test_report(self):
        """ Тестирование получения отчета успеваемости студента """
        kwargs = {'test_pk': self.test.pk}
        # Не авторизованный пользователь
        response = self.client.get(reverse(viewname='study:report', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse(viewname='study:report',
                                                                                   kwargs=kwargs))
        # Авторизованный пользователь
        self.client.force_login(user=self.user)
        response = self.client.get(reverse(viewname='study:report', kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, template_name='study/report.html')
        self.assertIn(member='lesson_pk', container=response.context)
        self.assertIn(member='test_pk', container=response.context)
        self.assertIn(member='questions_count', container=response.context)
        self.assertIn(member='correct_answers_count', container=response.context)
        self.assertIn(member='questions_with_correct_answer', container=response.context)
        self.assertEqual(response.context['lesson_pk'], self.lesson.pk)
        self.assertEqual(response.context['test_pk'], self.test.pk)
        self.assertEqual(response.context['questions_count'], self.test.questions.all().count())
        correct_answers_count = UserAnswer.objects.filter(user_id=self.user.pk, answer__is_correct=True,
                                                          answer__question__test__id=self.test.pk).count()
        self.assertEqual(response.context['correct_answers_count'], correct_answers_count)
        self.assertIsInstance(response.context['questions_with_correct_answer'], QuerySet)

    def test_statistics(self):
        """ Тестирование получения статистики """
        # Не авторизованный пользователь
        response = self.client.get(reverse('study:statistics'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:login') + '?next=' + reverse('study:statistics'))

        # Авторизованный пользователь
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('study:statistics'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('admin:login') + '?next=' + reverse('study:statistics'))

        # Авторизованный пользователь со статусом персонала
        self.client.force_login(user=self.user_staff)
        response = self.client.get(reverse('study:statistics'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, template_name='study/statistics.html')
        self.assertIn(member='context', container=response.context)
        self.assertIn(member='filter', container=response.context)
        self.assertIsInstance(response.context['context'], list)
        self.assertIsInstance(response.context['filter'], StatisticsFilter)
