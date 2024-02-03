# polls/admin.py
from django.contrib import admin
from .models import Survey, Question, Choice, UserAnswer


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 3


class SurveyAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]


admin.site.register(Survey, SurveyAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(UserAnswer)
