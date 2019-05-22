''' Module definig task to perform '''
from __future__ import absolute_import, unicode_literals
from datetime import datetime, timedelta, time
from celery import task
from scheduler.celery import app
from scheduler.mailer import Mailer


@app.task(name="notify_professors")
def notify_professors():
    """
    Search for lessons in incoming week
    then notify professors with emails if needed
    """
    from scheduler.models import Professor, Lesson
    mail = Mailer()
    today = datetime.now()
    next_week = today + timedelta(7)
    period_start = datetime.combine(today, time())
    period_end = datetime.combine(next_week, time())
    incomig_lessons = []
    for lesson in Lesson.objects.filter(start_time__range=(period_start, period_end)):
        incomig_lessons.append(lesson)
    for professor in Professor.objects.all():
        professor_lessons = []
        for lesson in incomig_lessons:
            if lesson.professor == professor:
                professor_lessons.append(lesson)
        if(professor_lessons and professor.email):
            mail.send_messages(subject='Lesson notification', template='email.html',\
            	context={'lessons': professor_lessons}, to_emails=[professor.email])
