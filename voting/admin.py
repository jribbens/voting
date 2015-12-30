"""voting admin."""

from django.contrib import admin

from .models import Choice, Election, Statement, Question, Voter, Votetaker


@admin.register(Votetaker)
class VotetakerAdmin(admin.ModelAdmin):
    """Votetaker admin class."""


@admin.register(Statement)
class StatementAdmin(admin.ModelAdmin):
    """Statement admin class."""
    date_hierarchy = "release_date"
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
    list_display = ("cfv_date", "status", "shortname", "title")
    list_display_links = ("shortname", "title")
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

    def has_change_permission(self, request, obj=None):
        return (obj is None or
                request.user.has_perm("voting.change_choice") or
                obj.votetaker == request.user or obj.secondary == request.user)

    def has_delete_permission(self, request, obj=None):
        return (obj is None or
                request.user.has_perm("voting.delete_choice") or
                obj.votetaker == request.user)


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
