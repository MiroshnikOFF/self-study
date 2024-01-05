from django import forms

from users.forms import StyleFormMixin
from study.models import Section, Lesson, Test, Question, Answer


class SectionForm(StyleFormMixin, forms.ModelForm):

    class Meta:
        model = Section
        fields = ('name', 'description', 'preview',)


class LessonForm(StyleFormMixin, forms.ModelForm):

    class Meta:
        model = Lesson
        exclude = ('author',)


class TestForm(StyleFormMixin, forms.ModelForm):

    class Meta:
        model = Test
        fields = ('lesson', 'name', 'description',)


class QuestionForm(StyleFormMixin, forms.ModelForm):

    class Meta:
        model = Question
        fields = ('question',)


class AnswerForm(StyleFormMixin, forms.ModelForm):

    class Meta:
        model = Answer
        fields = ('answer', 'is_correct',)
