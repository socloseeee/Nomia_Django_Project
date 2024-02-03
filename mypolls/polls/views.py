# polls/views.py
from django.db import connection
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

def survey_results(request, survey_id):
    # Получаем общее количество участников опроса
    total_participants_query = '''
        SELECT COUNT(DISTINCT user_id) 
        FROM polls_useranswer 
        WHERE survey_id = %s
    '''
    with connection.cursor() as cursor:
        cursor.execute(total_participants_query, [survey_id])
        total_participants = cursor.fetchone()[0] or 0

    # Получаем статистику для каждого вопроса
    question_statistics_query = '''
        SELECT
            q.id AS question_id,
            q.text AS question_text,
            ROUND(CAST(COUNT(DISTINCT ua.user_id) AS 'REAL') / %s * 100, 2) AS participants_count,
            RANK() OVER (ORDER BY COUNT(DISTINCT ua.user_id) DESC) AS question_rank,
            c.id AS choice_id,
            c.text AS choice_text,
            COUNT(ua.user_id) AS choice_count,
            (COUNT(ua.user_id) * 100.0 / %s) AS choice_percentage
        FROM polls_question q
        LEFT JOIN polls_choice c ON q.id = c.question_id
        LEFT JOIN polls_useranswer ua ON q.id = ua.question_id AND c.id = ua.choice_id
        WHERE q.survey_id = %s
        GROUP BY q.id, c.id
    '''
    with connection.cursor() as cursor:
        cursor.execute('''SELECT COUNT(t.user_id) FROM (SELECT user_id FROM polls_useranswer GROUP BY user_id) AS t''')
        all_users = float(cursor.fetchone()[0])
        cursor.execute(question_statistics_query, [all_users, total_participants, survey_id])
        question_statistics = cursor.fetchall()

    # Сгруппируем статистику по вопросам
    grouped_question_statistics = {}
    for row in question_statistics:
        question_id, question_text, participants_count, question_rank, choice_id, choice_text, choice_count, choice_percentage = row
        if question_id not in grouped_question_statistics:
            grouped_question_statistics[question_id] = {
                'question_text': question_text,
                'participants_count': participants_count,
                'question_rank': question_rank,
                'choices': [],
            }
        grouped_question_statistics[question_id]['choices'].append({
            'choice_id': choice_id,
            'choice_text': choice_text,
            'choice_count': choice_count,
            'choice_percentage': choice_percentage,
        })

    return render(request, 'polls/survey_results.html', {
        'survey_id': survey_id,
        'total_participants': total_participants,
        'grouped_question_statistics': grouped_question_statistics.values(),
    })



def thank_you(request):
    return render(request, 'polls/thank_you.html')
