from __future__ import absolute_import, unicode_literals
from celery import task
from scheduler.celery import app
from celery.task.schedules import crontab
from celery import task
from scheduler.mailer import Mailer
from datetime import datetime, timedelta, time

@task(name="notify_professors")
def notify_professors():
	from scheduler.models import Professor, Lesson
	mail = Mailer()
	today = datetime.now()
	next_week = today + timedelta(7)
	period_start = datetime.combine(today, time())
	period_end = datetime.combine(next_week, time())
	incomig_lessons = []
	for l in Lesson.objects.filter(start_time__range=(period_start, period_end)):
		incomig_lessons.append(l)
	for p in Professor.objects.all():
		professor_lessons = []
		for l in incomig_lessons:
			if l.professor == p:
				professor_lessons.append(l)
		if(professor_lessons and p.email):
			mail.send_messages(subject='mailll',
               	template='email.html',
               	context={'lessons': professor_lessons},
              	to_emails=[p.email])
