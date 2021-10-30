from django.contrib import admin
from django.utils.html import format_html

from homework.models import Group, Student, Homework, HomeTask, TestAttempt


class GroupsAdmin(admin.ModelAdmin):
    list_display = ['name']


class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'num_targets')
    actions = []


class AttemptsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'homework', 'datetime', 'finished', 'log', 'passed', 'score')


class HomeworkAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'hometask', 'show_firm_url')

    def show_firm_url(self, obj):
        return format_html("<a href='{url}'>{url}</a>", url=obj.git_repository_url)


admin.site.register(Group, GroupsAdmin)
admin.site.register(Student)
admin.site.register(HomeTask)
admin.site.register(Homework, HomeworkAdmin)
admin.site.register(TestAttempt, AttemptsAdmin)
