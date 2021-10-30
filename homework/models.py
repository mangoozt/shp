import json

from django.db import models
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.html import escape
from django_q.tasks import async_task


class Group(models.Model):
    name = models.TextField(max_length=20)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return str(self.name)


class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    surname = models.TextField(max_length=500)
    name = models.TextField(max_length=500)
    group = models.ForeignKey(Group, related_name='students', on_delete=models.deletion.SET_NULL, default=1, null=True)

    def __str__(self):
        return str(self.name)


class HomeTask(models.Model):
    name = models.CharField(max_length=500)
    group = models.ManyToManyField(Group)
    max_score = models.IntegerField(blank=True, default=100)
    task_content = models.TextField(max_length=5000, blank=True)
    tests_directory = models.TextField(max_length=500, blank=True)
    tests_package = models.FileField(blank=True)
    test_cmd = models.TextField(blank=True)

    def __str__(self):
        return str(self.name)


class Homework(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    git_repository_url = models.TextField(max_length=500)
    student = models.ForeignKey(Student, related_name='homeworks', on_delete=models.deletion.SET_NULL, null=True)
    hometask = models.ForeignKey(HomeTask, on_delete=models.deletion.SET_NULL, null=True)

    class Meta:
        unique_together = ['student', 'hometask']

    def __str__(self):
        return str(self.hometask.name + '-' + self.student.name)


class TestAttempt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(max_length=500)
    homework = models.ForeignKey(Homework, related_name='attempts', on_delete=models.deletion.SET_NULL, null=True)
    datetime = models.DateTimeField()
    finished = models.DateTimeField(blank=True, null=True)
    log = models.TextField(max_length=5000, blank=True)
    passed = models.BooleanField(default=False)
    score = models.IntegerField()

    @property
    def nice_log(self):
        try:
            json_log = json.loads(self.log)
            text = ''
            i = 0
            for test in json_log['tests']:
                if "safe" in test and test["safe"] is True:
                    test_name = test['name']
                else:
                    test_name = '#' + str(i)
                    i += 1
                text += f"{test_name:20}: {'Passed' if test['passed'] else 'Failed'} \n"
                if "safe" in test and test["safe"] is True:
                    if "message" in test:
                        text += test["message"] + '\n'
            return escape(text)
        except:
            return "Can't parse log"


@receiver(post_save, sender=TestAttempt)
def queue_new_test(sender, instance: TestAttempt, **kwargs):
    if instance.finished is None:
        # tell everyone
        async_task('tasks.run_test', instance)
