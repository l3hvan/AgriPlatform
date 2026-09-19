from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile


class SignupForm(UserCreationForm):
    email = forms.EmailField(
        required=True, max_length=254,
        widget=forms.EmailInput(attrs={'class': 'chart-select', 'style': 'width:100%;'})
    )
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES, initial='viewer',
        widget=forms.Select(attrs={'class': 'chart-select', 'style': 'width:100%;'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ['username', 'password1', 'password2']:
            self.fields[field].widget.attrs.update({'class': 'chart-select', 'style': 'width:100%;'})

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class GenericErrorLoginForm(AuthenticationForm):
    """Same error message whether the username is wrong, the password is wrong,
    or (later) the account is locked - never reveals which case it was."""
    error_messages = {
        'invalid_login': "Incorrect username or password.",
        'inactive': "Incorrect username or password.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ['username', 'password']:
            self.fields[field].widget.attrs.update({'class': 'chart-select', 'style': 'width:100%;'})