from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from rest_framework import viewsets, mixins, generics, filters
import pandas as pd

from homework.forms import UploadStudentsGroupCsv, StudentSearchForm
from homework.models import Student, Homework, Group, HomeTask, TestAttempt
from homework.serializers import StudentSerializer, GroupSerializer, HomeworkSerializer, HometaskSerializer
from rest_framework import permissions


def bulk_students_upload(request):
    if request.method == 'POST':
        form = UploadStudentsGroupCsv(request.POST, request.FILES)
        if form.is_valid():
            df = pd.read_csv(form.cleaned_data['file'])
            for i in range(len(df)):
                student = Student()
                student.group = form.cleaned_data['group']
                student.name = df['name'][i]
                student.save()
                homework = Homework()
                homework.student = student
                homework.git_repository_url = df['git'][i]
                homework.hometask = form.cleaned_data['hometask']
                homework.save()
            return render(request, 'bare_form.html', {'form': form})
    else:
        form = UploadStudentsGroupCsv()
        return render(request, 'bare_form.html', {'form': form})


def search_view(request):
    if request.method == 'POST':
        form = StudentSearchForm(request.POST, request.FILES)
        if form.is_valid():
            students = Student.objects.filter(name__icontains=form.cleaned_data['name'])
            if len(students) > 1:
                form.add_error('name', 'Уточните запрос')
            elif len(students) > 0:
                return HttpResponseRedirect(reverse('student_page', kwargs={"student_id": students[0].id}))
            else:
                form.add_error('name', 'Not found')
    else:
        form = StudentSearchForm(request.POST, request.FILES)

    return render(request, 'search_form.html', {'form': form})


def student_page(request, student_id=None):
    if student_id is not None:
        student = get_object_or_404(Student, id=student_id)
        return render(request, 'student_page.html', {'student': student})
    return HttpResponseRedirect(reverse('main'))


def homework_page(request, homework_id=None):
    if homework_id is not None:
        homework = get_object_or_404(Homework, id=homework_id)
        return render(request, 'homework_page.html', {'homework': homework})
    return HttpResponseRedirect(reverse('main'))


def groups_list_page(request):
    if request.user.is_superuser:
        groups = Group.objects.all().order_by('name')
        return render(request, 'groups_list.html', {'groups': groups})
    else:
        return HttpResponseRedirect(reverse('main'))


def group_page(request, group_id):
    if request.user.is_superuser:
        group = get_object_or_404(Group, id=group_id)
        from django.db.models import Count, Case, When
        students = group.students.all().order_by('name').annotate(passed=Count(Case(When(homeworks__attempts__passed=True, then=1))))

        total_passed = students.filter(passed__gt=0).count()
        return render(request, 'students_list.html',
                      {'group': group, 'students': students, 'total_passed': total_passed})
    else:
        return HttpResponseRedirect(reverse('main'))


class StudentViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Student.objects.all().order_by('-pk')
    serializer_class = StudentSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]


class HometaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = HomeTask.objects.all().order_by('-pk')
    serializer_class = HometaskSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.DjangoModelPermissions]


class HomeworkVeiwSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Homework.objects.all()
    serializer_class = HomeworkSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]


class NoEmptyQuerySearchFilter(filters.SearchFilter):
    """
    Filter that only allows users to see their own objects.
    """

    def filter_queryset(self, request, queryset, view):
        if 'search' in request.query_params and len(request.query_params['search']) > 0:
            return super(NoEmptyQuerySearchFilter, self).filter_queryset(request, queryset, view)
        else:
            return queryset.none()


class UserListView(generics.ListAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    filter_backends = [NoEmptyQuerySearchFilter]
    search_fields = ['name']


def new_test(request, homework_id=None):
    hw = get_object_or_404(Homework, id=homework_id)
    if len(hw.git_repository_url) != 0 and not hw.git_repository_url.isspace():
        if len(hw.attempts.filter(finished__isnull=True)) == 0:
            new_attempt = TestAttempt(homework=hw)
            new_attempt.save()

    return HttpResponseRedirect(reverse('homework_page', kwargs={"homework_id": hw.id}))
