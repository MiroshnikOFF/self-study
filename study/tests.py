from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from study.models import Section, Lesson, Test, Question, Answer, UserAnswer
from users.models import User


class StudyTestCase(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(
            email='test@test.ru',
            is_staff=True,
            is_superuser=True,
            is_active=True
        )
        self.user.set_password('0000')
        self.user.save()
        self.access_token = str(AccessToken.for_user(self.user))
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        self.section = Section.objects.create(name='Section 1')
        self.lesson = Lesson.objects.create(name='Lesson 1', section=self.section, author=self.user)
        self.test = Test.objects.create(name='Test 1', lesson=self.lesson)
        self.question = Question.objects.create(question='What is it?', test=self.test)
        self.answer = Answer.objects.create(answer='It is a test', question=self.question)
        self.user_answer = UserAnswer.objects.create(user=self.user, answer=self.answer)

    def test_section_create(self) -> None:
        """ Тестирование создания раздела """
        data = {'name': 'New section'}
        response = self.client.post('/api/v1/study/sections/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['name'], data['name'])
        self.assertTrue(Section.objects.filter(id=response.json()['id']).exists())

    def test_section_list(self):
        """ Тестирование получения списка разделов """
        sections = list(Section.objects.all())
        response = self.client.get('/api/v1/study/sections/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], len(sections))
        self.assertEqual(response.json()['results'][0]['id'], sections[0].pk)

    def test_section_retrieve(self):
        """ Тестирование получения раздела """
        response = self.client.get(f'/api/v1/study/sections/{self.section.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['id'], self.section.pk)
        self.assertEqual(response.json()['name'], self.section.name)

    def test_section_update(self):
        """ Тестирование изменения раздела """
        data = {'name': 'New section', 'description': 'Some description'}
        response = self.client.put(f'/api/v1/study/sections/{self.section.pk}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['name'], data['name'])
        self.assertEqual(response.json()['description'], data['description'])

    def test_section_delete(self):
        """ Тестирование удаления раздела """
        response = self.client.delete(f'/api/v1/study/sections/{self.section.pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Section.objects.filter(pk=self.section.pk).exists())

    def test_lesson_create(self) -> None:
        """ Тестирование создания урока """
        data = {'name': 'New lesson', 'section': self.section.pk}
        response = self.client.post('/api/v1/study/lessons/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['name'], data['name'])
        self.assertEqual(response.json()['author'], self.user.pk)
        self.assertTrue(Lesson.objects.filter(id=response.json()['id']).exists())

    def test_lesson_list(self):
        """ Тестирование получения списка уроков """
        lessons = list(Section.objects.all())
        response = self.client.get('/api/v1/study/lessons/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], len(lessons))
        self.assertEqual(len(response.json()['results']), len(lessons))

    def test_lesson_retrieve(self):
        """ Тестирование получения урока """
        response = self.client.get(f'/api/v1/study/lessons/{self.lesson.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['id'], self.lesson.pk)
        self.assertEqual(response.json()['name'], self.lesson.name)

    def test_lesson_update(self):
        """ Тестирование изменения урока """
        data = {'name': 'New lesson', 'section': self.section.pk}
        response = self.client.put(f'/api/v1/study/lessons/{self.lesson.pk}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['name'], data['name'])
        self.assertEqual(response.json()['author'], self.user.pk)

    def test_lesson_delete(self):
        """ Тестирование удаления урока """
        response = self.client.delete(f'/api/v1/study/lessons/{self.lesson.pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(pk=self.section.pk).exists())

    def test_test_create(self) -> None:
        """ Тестирование создания теста """
        data = {'name': 'New test', 'lesson': self.lesson.pk}
        response = self.client.post('/api/v1/study/tests/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['name'], data['name'])
        self.assertTrue(Test.objects.filter(id=response.json()['id']).exists())

    def test_test_list(self):
        """ Тестирование получения списка тестов """
        tests = list(Test.objects.all())
        response = self.client.get('/api/v1/study/tests/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], len(tests))
        self.assertEqual(len(response.json()['results']), len(tests))

    def test_test_retrieve(self):
        """ Тестирование получения теста """
        response = self.client.get(f'/api/v1/study/tests/{self.test.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['id'], self.test.pk)
        self.assertEqual(response.json()['name'], self.test.name)

    def test_test_update(self):
        """ Тестирование изменения теста """
        data = {'name': 'New test', 'lesson': self.lesson.pk}
        response = self.client.put(f'/api/v1/study/tests/{self.test.pk}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['name'], data['name'])

    def test_test_delete(self):
        """ Тестирование удаления теста """
        response = self.client.delete(f'/api/v1/study/tests/{self.test.pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Test.objects.filter(pk=self.section.pk).exists())

    def test_question_create(self) -> None:
        """ Тестирование создания вопроса """
        data = {'question': 'How much is it?', 'test': self.test.pk}
        response = self.client.post('/api/v1/study/questions/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['question'], data['question'])
        self.assertTrue(Question.objects.filter(id=response.json()['id']).exists())

    def test_question_list(self):
        """ Тестирование получения списка вопросов """
        questions = list(Question.objects.all())
        response = self.client.get('/api/v1/study/questions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], len(questions))
        self.assertEqual(len(response.json()['results']), len(questions))

    def test_question_retrieve(self):
        """ Тестирование получения вопроса """
        response = self.client.get(f'/api/v1/study/questions/{self.question.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['id'], self.question.pk)
        self.assertEqual(response.json()['question'], self.question.question)

    def test_question_update(self):
        """ Тестирование изменения вопроса """
        data = {'question': 'How much does it cost?', 'test': self.test.pk}
        response = self.client.put(f'/api/v1/study/questions/{self.question.pk}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['question'], data['question'])

    def test_question_delete(self):
        """ Тестирование удаления вопроса """
        response = self.client.delete(f'/api/v1/study/questions/{self.question.pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Question.objects.filter(pk=self.section.pk).exists())

    def test_answer_create(self) -> None:
        """ Тестирование создания ворианта ответа """
        data = {'answer': 'Test answer', 'question': self.question.pk}
        response = self.client.post('/api/v1/study/answers/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['answer'], data['answer'])
        self.assertTrue(Answer.objects.filter(id=response.json()['id']).exists())

    def test_answer_list(self):
        """ Тестирование получения списка вариантов ответов """
        answers = list(Answer.objects.all())
        response = self.client.get('/api/v1/study/answers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], len(answers))
        self.assertEqual(len(response.json()['results']), len(answers))

    def test_answer_retrieve(self):
        """ Тестирование получения варианта ответа """
        response = self.client.get(f'/api/v1/study/answers/{self.answer.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['id'], self.answer.pk)
        self.assertEqual(response.json()['answer'], self.answer.answer)

    def test_answer_update(self):
        """ Тестирование изменения варианта ответа """
        data = {'answer': 'New answer', 'question': self.question.pk}
        response = self.client.put(f'/api/v1/study/answers/{self.answer.pk}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['answer'], data['answer'])

    def test_answer_delete(self):
        """ Тестирование удаления варианта ответа """
        response = self.client.delete(f'/api/v1/study/answers/{self.answer.pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Answer.objects.filter(pk=self.answer.pk).exists())

    def test_report(self):
        """ Тестирование получения отчета успеваемости студента """
        response = self.client.get('/api/v1/study/report/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['completed_tests'], 1)
        self.assertEqual(response.json()['all_answers'], 1)
        self.assertEqual(response.json()['correct_answers'], 0)
        self.assertEqual(response.json()['incorrect_answers'], 1)
        self.assertEqual(response.json()['correct_answers_percentage'], 0)

        correct_answer = Answer.objects.create(answer='Correct answer', question=self.question, is_correct=True)
        UserAnswer.objects.create(user=self.user, answer=correct_answer)
        response = self.client.get('/api/v1/study/report/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['all_answers'], 2)
        self.assertEqual(response.json()['correct_answers'], 1)
        self.assertEqual(response.json()['correct_answers_percentage'], 50)

        new_test = Test.objects.create(name='New test', lesson=self.lesson)
        new_question = Question.objects.create(question='New question', test=new_test)
        new_answer = Answer.objects.create(answer='New answer', question=new_question, is_correct=True)
        UserAnswer.objects.create(user=self.user, answer=new_answer)
        response = self.client.get('/api/v1/study/report/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['completed_tests'], 2)
        self.assertEqual(response.json()['all_answers'], 3)
        self.assertEqual(response.json()['correct_answers'], 2)
        self.assertEqual(response.json()['correct_answers_percentage'], 66)

    def test_statistics(self):
        response = self.client.get('/api/v1/study/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], User.objects.all().count())

        new_user = User.objects.create(email='new@user.ru')
        UserAnswer.objects.create(user=new_user, answer=self.answer)
        response = self.client.get('/api/v1/study/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], User.objects.all().count())



