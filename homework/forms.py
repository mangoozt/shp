from django import forms

from homework.models import Group, HomeTask


class UploadStudentsGroupCsv(forms.Form):
    group = forms.ModelChoiceField(queryset=Group.objects.order_by('-pk'), required=True)
    hometask = forms.ModelChoiceField(queryset=HomeTask.objects.order_by('-pk'), required=True)
    file = forms.FileField()


class StudentSearchForm(forms.Form):
    name = forms.CharField(label='Фамилия', max_length=100, required=True,
                           widget=forms.TextInput(attrs={'autocomplete': 'off'}))
