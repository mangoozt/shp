from django.db import models
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
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


class TestAttempt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(max_length=500)
    homework = models.ForeignKey(Homework, related_name='attempts', on_delete=models.deletion.SET_NULL, null=True)
    datetime = models.DateTimeField()
    finished = models.DateTimeField(null=True)
    log = models.TextField(max_length=5000)
    passed = models.BooleanField(default=False)
    score = models.IntegerField()


@receiver(post_save, sender=TestAttempt)
def queue_new_test(sender, instance: TestAttempt, **kwargs):
    if instance.finished is None:
        # tell everyone
        async_task('tasks.run_test', instance)
