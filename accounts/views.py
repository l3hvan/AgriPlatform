import logging
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import SignupForm
from .models import UserProfile

logger = logging.getLogger(__name__)

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user, role=form.cleaned_data['role'])
            logger.info(f"New account created: {user.username}")
            return redirect('login')
        else:
            logger.warning(f"Signup validation failed for IP {request.META.get('REMOTE_ADDR')}")
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form, 'active': 'signup'})


def axes_lockout_response(request, credentials, *args, **kwargs):
    """Called by django-axes when an account is locked out. Shows the exact
    same generic message as a normal wrong-password failure, so a locked-out
    account is indistinguishable from a simple typo - never reveals lockout."""
    messages.error(request, "Incorrect username or password.")
    return redirect('login')