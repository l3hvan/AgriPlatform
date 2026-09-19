import logging
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