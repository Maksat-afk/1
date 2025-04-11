from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from .models import Task
from .models import Review

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, label="Выберите роль")

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password1', 'password2']

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'image', 'description', 'volunteers_required',
                  'expectations_volunteer', 'expectations_sponsor', 'contacts']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['target', 'rating', 'comment']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        if user.role == 'volunteer':
            tasks = user.accepted_tasks.all()
            fund_ids = tasks.values_list('fund', flat=True)
            sponsor_ids = tasks.values_list('sponsors__id', flat=True)
            self.fields['target'].queryset = User.objects.filter(id__in=list(fund_ids) + list(sponsor_ids)).exclude(id=user.id)

        elif user.role == 'fund':
            tasks = user.fund_tasks.all()
            volunteer_ids = tasks.values_list('volunteers__id', flat=True)
            sponsor_ids = tasks.values_list('sponsors__id', flat=True)
            self.fields['target'].queryset = User.objects.filter(id__in=list(volunteer_ids) + list(sponsor_ids)).exclude(id=user.id)

        elif user.role == 'sponsor':
            tasks = user.supported_tasks.all()
            fund_ids = tasks.values_list('fund', flat=True)
            volunteer_ids = tasks.values_list('volunteers__id', flat=True)
            self.fields['target'].queryset = User.objects.filter(id__in=list(fund_ids) + list(volunteer_ids)).exclude(id=user.id)
