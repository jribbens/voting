"""voting views."""

from django.shortcuts import render

from .models import Votetaker


def home(request):
    """Display the home page."""
    return render(request, "voting/home.html", {})


def votetakers(request):
    """List the votetakers."""
    return render(
        request, "voting/votetakers.html", {
            "active_votetakers":
                Votetaker.objects.filter(user__is_active=True),
            "retired_votetakers":
                Votetaker.objects.filter(user__is_active=False),
        }
    )
