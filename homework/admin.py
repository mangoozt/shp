from django.contrib import admin
from django.utils.html import format_html

from homework.models import Group, Student, Homework, HomeTask, TestAttempt


@admin.action(description='Add tests')
def create_tests(modeladmin, request, queryset):
    for hw in queryset:
        if len(hw.git_repository_url) != 0 and not hw.git_repository_url.isspace():
            if len(hw.attempts.filter(finished__isnull=True)) == 0:
                new_attempt = TestAttempt(homework=hw)
                new_attempt.save()


class GroupsAdmin(admin.ModelAdmin):
    list_display = ['name']


class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'num_targets')
    actions = []


class AttemptsAdmin(admin.ModelAdmin):
    list_display = ('id', 'homework', 'datetime', 'finished', 'log', 'passed', 'score')


class HomeworkAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'hometask', 'show_firm_url')
    actions = [create_tests]

    def show_firm_url(self, obj):
        return format_html("<a href='{url}'>{url}</a>", url=obj.git_repository_url)


admin.site.register(Group, GroupsAdmin)
admin.site.register(Student)
admin.site.register(HomeTask)
admin.site.register(Homework, HomeworkAdmin)
admin.site.register(TestAttempt, AttemptsAdmin)
