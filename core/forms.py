from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from .models import Task
from .models import Review
from .models import Report

class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        allowed_roles = [choice for choice in User.ROLE_CHOICES if choice[0] != 'admin']
        self.fields['role'] = forms.ChoiceField(choices=allowed_roles, label="Выберите роль")

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password1', 'password2']

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'title', 'image', 'description',
            'expectations_volunteer', 'expectations_sponsor',
            'volunteers_required', 'contacts', 'category',
        ]

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

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['target_user', 'reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 4}),
        }