"""voting settings."""

from django.conf import settings


SECRET_LENGTH = getattr(settings, "VOTING_SECRET_LENGTH", 8)
NEWS_SERVER = getattr(settings, "VOTING_NEWS_SERVER", "")
