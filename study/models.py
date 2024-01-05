from django.db import models

from config import settings

NULLABLE = {'null': True, 'blank': True}


class Section(models.Model):
    name = models.CharField(max_length=150, verbose_name='название')
    description = models.TextField(**NULLABLE, verbose_name='описание')
    preview = models.ImageField(upload_to='study/', **NULLABLE, verbose_name='превью')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'раздел'
        verbose_name_plural = 'разделы'
        ordering = ('pk',)


class Lesson(models.Model):
    name = models.CharField(max_length=150, verbose_name='название')
    content = models.TextField(**NULLABLE, verbose_name='контент')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='lessons', verbose_name='раздел')
    preview = models.ImageField(upload_to='study/', **NULLABLE, verbose_name='превью')
    video_url = models.URLField(verbose_name='Видео', **NULLABLE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, **NULLABLE, related_name='lessons',
                               verbose_name='автор')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'урок'
        verbose_name_plural = 'уроки'
        ordering = ('pk',)


class Test(models.Model):
    name = models.CharField(max_length=150, **NULLABLE, verbose_name='название')
    description = models.TextField(**NULLABLE, verbose_name='описание')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='tests', verbose_name='урок')

    def __str__(self):
        return f'{self.pk}. {self.name}'

    class Meta:
        verbose_name = 'тест'
        verbose_name_plural = 'тесты'
        ordering = ('pk',)


class Question(models.Model):
    question = models.TextField(verbose_name='Вопрос')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions', verbose_name='тест')

    def __str__(self):
        return f'{self.pk}. {self.question}'

    class Meta:
        verbose_name = 'вопрос'
        verbose_name_plural = 'вопросы'
        ordering = ('pk',)


class Answer(models.Model):
    answer = models.TextField(verbose_name='ответ')
    is_correct = models.BooleanField(default=False, verbose_name='признак правильного ответа')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name='вопрос')

    def __str__(self):
        return f'{self.pk}. {self.answer}'

    class Meta:
        verbose_name = 'ответ'
        verbose_name_plural = 'ответы'
        ordering = ('pk',)


class UserAnswer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='answers',
                             verbose_name='пользователь')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='users', verbose_name='ответ')

    def __str__(self):
        return f'{self.user} - {self.answer}'

    class Meta:
        verbose_name = 'ответ пользователя'
        verbose_name_plural = 'ответы пользователей'
        ordering = ('pk',)
