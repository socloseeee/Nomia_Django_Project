# polls/views.py
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from .models import Survey, Question, Choice, UserAnswer


def survey_detail(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)
    questions = Question.objects.filter(survey=survey)
    user_id = 1  # В реальном проекте можно использовать аутентификацию

    if request.method == 'POST':
        for question in questions:
            choice_id = request.POST.get(f'question_{question.id}')
            if choice_id:
                UserAnswer.objects.create(user_id=user_id, survey=survey, question=question, choice_id=choice_id)

        return HttpResponseRedirect('/thank-you/')

    return render(request, 'polls/survey_detail.html', {'survey': survey, 'questions': questions})


def thank_you(request):
    return render(request, 'polls/thank_you.html')
