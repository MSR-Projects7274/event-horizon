from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import redirect, render

from events.models import Booking

from .forms import ProfileForm, RegistrationForm


def register(request):
    """Register a new user."""

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            return redirect('login')

    else:
        form = RegistrationForm()

    return render(
        request,
        'registration/register.html',
        {'form': form}
    )


@login_required
def profile(request):
    """Display the user's profile and bookings."""

    bookings = Booking.objects.filter(
        user=request.user
    ).select_related(
        'event',
        'event__category'
    ).order_by(
        'event__date',
        'event__time'
    )

    return render(
        request,
        'profiles/profile.html',
        {
            'bookings': bookings,
            'profile_user': request.user,
        }
    )


@login_required
def edit_profile(request):
    """Allow the user to update their account details."""

    if request.method == 'POST':
        form = ProfileForm(
            request.POST,
            instance=request.user
        )

        if form.is_valid():
            form.save()

            return redirect('profile')

    else:
        form = ProfileForm(
            instance=request.user
        )

    return render(
        request,
        'profiles/edit_profile.html',
        {
            'form': form,
        }
    )


@login_required
def change_password(request):
    """Allow the user to change their password."""

    if request.method == 'POST':
        form = PasswordChangeForm(
            request.user,
            request.POST
        )

        if form.is_valid():
            user = form.save()

            update_session_auth_hash(
                request,
                user
            )

            return redirect('profile')

    else:
        form = PasswordChangeForm(request.user)

    return render(
        request,
        'profiles/change_password.html',
        {
            'form': form,
        }
    )
