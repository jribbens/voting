"""voting admin."""

import datetime

from django.contrib import admin
from django.db.models import Q
from django.utils import timezone

from .models import Choice, Election, Statement, Question, Voter, Votetaker
from .settings import RECENT_DAYS


@admin.register(Votetaker)
class VotetakerAdmin(admin.ModelAdmin):
    """Votetaker admin class."""
    list_display = ("username", "full_name", "role", "active")
    list_display_links = ("username",)
    list_filter = ("user__is_active",)

    def full_name(self, obj):
        """Return the votetaker's full name."""
        # pylint: disable=no-self-use
        return obj.user.get_full_name()
    full_name.short_description = "Name"

    def username(self, obj):
        """Return the votetaker's username."""
        # pylint: disable=no-self-use
        return obj.user.username

    def active(self, obj):
        """Return whether or not the votetaker is active."""
        # pylint: disable=no-self-use
        return obj.user.is_active
    active.boolean = True



@admin.register(Statement)
class StatementAdmin(admin.ModelAdmin):
    """Statement admin class."""
    date_hierarchy = "release_date"
    list_display = ("release_date", "title")
    list_display_links = ("title",)
    prepopulated_fields = {"slug": ("title",)}


class ChoiceInline(admin.TabularInline):
    """Choice inline admin class."""
    model = Choice


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Question admin class."""
    inlines = (ChoiceInline,)


@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    """Election admin class."""
    date_hierarchy = "cfv_date"
    list_display = ("cfv_date", "shortname", "title")
    list_display_links = ("title",)
    list_filter = ("status", "hidden", "uk_vote")
    radio_fields = {"status": admin.HORIZONTAL}
    search_fields = ("shortname", "title", "proposal")
    fieldsets = (
        ("Election information", {
            "fields": (
                "title",
                "shortname",
                "votetype",
                "uk_vote",
                ),
            }
        ),
        ("Administration", {
            "fields": (
                "status",
                ("votetaker", "secondary"),
                "hidden",
                ),
            }
        ),
        ("CFV", {
            "fields": (
                "cfv_date",
                "cfv_end_date",
                "cfv_msgid",
                ),
            }
        ),
        ("Result", {
            "fields": (
                "result_date",
                "result_msgid",
                ),
            }
        ),
        (None, {
            "fields": (
                "proposal",
                ),
            }
        ),
    )

    def has_module_permission(self, request):
        if not (request.user.is_active and
                Votetaker.objects.filter(user=request.user).exists()):
            return False
        return True

    def has_add_permission(self, request):
        if not (request.user.is_active and
                Votetaker.objects.filter(user=request.user).exists()):
            return False
        return True

    def has_change_permission(self, request, obj=None):
        if not (request.user.is_active and
                Votetaker.objects.filter(user=request.user).exists()):
            return False
        if obj is None or request.user.has_perm("voting.change_election"):
            return True
        if not (obj.votetaker.user == request.user or
                (obj.secondary and obj.secondary.user == request.user)):
            return False
        recent = (timezone.now() - datetime.timedelta(days=RECENT_DAYS)).date()
        if (obj.status != Election.RESULT or
                (obj.latest_date() or recent) > recent):
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        if not (request.user.is_active and
                Votetaker.objects.filter(user=request.user).exists()):
            return False
        if obj is None or request.user.has_perm("voting.delete_election"):
            return True
        if obj.votetaker.user != request.user:
            return False
        recent = (timezone.now() - datetime.timedelta(days=RECENT_DAYS)).date()
        return bool(obj.status != Election.RESULT or
                (obj.latest_date() or recent) > recent)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if (request.user.has_perm("voting.change_election") or
                request.user.has_perm("voting.delete_election")):
            return qs
        recent = (timezone.now() - datetime.timedelta(days=RECENT_DAYS)).date()
        qs = qs.filter(Q(votetaker__user=request.user) |
                       Q(secondary__user=request.user))
        qs = qs.exclude(status=Election.RESULT, cfv_date__lte=recent,
                        cfv_end_date__lte=recent, result_date__lte=recent)
        return qs


@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):
    """Voter admin class."""
    fields = (
        "email", "name", "posting_address", "accepted", "notes",
        "creation_date", "vote_date", "comments", "email_headers"
    )
    readonly_fields = (
        "email", "creation_date", "vote_date", "comments", "email_headers"
    )
