"""voting settings."""

from django.conf import settings


SECRET_LENGTH = getattr(settings, "VOTING_SECRET_LENGTH", 8)
