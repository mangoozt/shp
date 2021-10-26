from django.contrib import admin

from homework.models import Group, Student, Homework, HomeTask


class GroupsAdmin(admin.ModelAdmin):
    list_display = ['name']


class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'num_targets')
    actions = []


class ScenariosSetAdmin(admin.ModelAdmin):
    list_display = ('n_targets', 'n_cases', 'metafile')


class CompareAdmin(admin.ModelAdmin):
    list_display = ('obj1', 'obj2', 'n_targets')


admin.site.register(Group, GroupsAdmin)
admin.site.register(Student)
admin.site.register(HomeTask)
admin.site.register(Homework)
