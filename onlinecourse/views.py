from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.views import generic import logging
from .models import Course, Enrollment, Question, Choice, Submission

logger = logging.getLogger(__name__)
# --- existing views above ---

def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    enrollment = Enrollment.objects.get(user=user, course=course)
    submission = Submission.objects.create(enrollment=enrollment)
    choices = extract_answers(request)
    submission.choices.set(Choice.objects.filter(id__in=choices))
    submission_id = submission.id
    return HttpResponseRedirect(reverse(viewname='onlinecourse:exam_result',
                                        args=(course_id, submission_id,)))
def extract_answers(request):
    submitted_answers = []
    for key in request.POST:
        if key.startswith('choice'):
            value = request.POST[key]
            choice_id = int(value)
            submitted_answers.append(choice_id)
    return submitted_answers

def show_exam_result(request, course_id, submission_id):
    context = {}
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    choices = submission.choices.all()

    total_score = 0
    questions = course.question_set.all()

    for question in questions:
        correct_choices = question.choice_set.filter(is_correct=True)
        selected_choices = choices.filter(question=question)

        if set(correct_choices) == set(selected_choices):
            total_score += question.grade

    context['course'] = course
    context['grade'] = total_score
    context['choices'] = choices

    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)