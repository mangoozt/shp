"""portal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'groups', views.GroupViewSet)
router.register(r'student', views.StudentViewSet)
router.register(r'homework', views.HomeworkVeiwSet)
router.register(r'hometask', views.HometaskViewSet)

urlpatterns = [
    path('api', include(router.urls)),
    path('', views.search_view, name='main'),
    path('students', views.UserListView.as_view()),
    path('student/<uuid:student_id>', views.student_page, name='student_page'),
    path('homework/<uuid:homework_id>', views.homework_page, name='homework_page'),
    path('homework/<uuid:homework_id>/test', views.new_test, name='new_test'),
    path('groups', views.groups_list_page, name='groups_list'),
    path('groups/<uuid:group_id>', views.group_page, name='group_page'),
    path('bulk_students_upload', views.bulk_students_upload),
    path('api-auth/', include('rest_framework.urls'))
]
