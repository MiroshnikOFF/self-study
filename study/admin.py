from django.contrib import admin

from study.models import Section, Lesson, Test, Question, Answer, UserAnswer


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'created', 'preview',)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'section', 'preview', 'video_url', 'author',)
    list_filter = ('section',)


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'lesson',)
    list_filter = ('lesson',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'question', 'test')
    list_filter = ('test',)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('pk', 'answer', 'is_correct', 'question',)
    list_filter = ('question',)


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'answer',)
    list_filter = ('user',)
