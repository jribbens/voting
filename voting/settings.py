"""voting settings."""

from django.conf import settings


NEWS_SERVER = getattr(settings, "VOTING_NEWS_SERVER", "")
RECENT_DAYS = getattr(settings, "VOTING_RECENT_DAYS", 45)
