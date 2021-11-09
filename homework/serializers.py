from .models import Student, Homework, Group, HomeTask
from rest_framework import serializers


class StudentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Student
        fields = ['url', 'name', 'group', 'homeworks']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    students = StudentSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ['url', 'name', 'students']


class HometaskSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HomeTask
        fields = ['url', 'name']


class HomeworkSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Homework
        fields = ['url', 'git_repository_url', 'student', 'hometask']
