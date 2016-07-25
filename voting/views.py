"""voting views."""

# pylint: disable=too-many-ancestors

import datetime
import email

from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import DetailView, ListView

from .models import Election, Statement, Votetaker


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


class StatementList(ListView):
    """List the statements."""
    model = Statement


class StatementView(DetailView):
    """View a statement."""
    model = Statement

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        try:
            return queryset.get(
                release_date=datetime.datetime.strptime(
                    self.kwargs["release_date"], "%Y/%m/%d").date(),
                slug=self.kwargs["slug"],
            )
        except Statement.DoesNotExist:
            raise Http404("Statement not found")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        message = email.message_from_string(self.object.statement)
        context["message"] = message
        context["body"] = message.get_payload()
        return context


def statement_raw(request, release_date=None, slug=None):
    """Return the raw text of a statement."""
    # pylint: disable=unused-argument
    return HttpResponse(
        get_object_or_404(
            Statement,
            release_date=datetime.datetime.strptime(
                release_date, "%Y/%m/%d").date(),
            slug=slug
            ).statement,
        content_type="text/plain; charset=utf-8"
    )


def statement_by_msgid(request, msgid=None):
    """Return a redirect to the proper URL for a statement."""
    # pylint: disable=unused-argument
    msgid = "<" + msgid + ">"
    return redirect(
        get_object_or_404(Statement, msgid=msgid).get_absolute_url(),
        permanent=True
    )


class ResultList(ListView):
    """List the election results."""
    model = Election
    template_name = "voting/result_list.html"

    def get_queryset(self):
        queryset = Election.objects.filter(status=Election.RESULT).exclude(
            hidden=True).order_by("-result_date")
        if "non-uk" in self.request.GET:
            queryset = queryset.exclude(uk_vote=True)
        else:
            queryset = queryset.exclude(uk_vote=False)
        if "votetaker" in self.request.GET:
            queryset = queryset.filter(
                votetaker__user__username=self.request.GET["votetaker"])
        queryset = queryset.defer("proposal", "cfv")
        queryset = queryset.select_related("votetaker", "votetaker__user")
        return queryset


class ResultView(DetailView):
    """View an election result."""
    model = Election
    template_name = "voting/result_detail.html"

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        queryset = queryset.filter(status=Election.RESULT)
        try:
            if self.kwargs["key"].isdigit():
                return queryset.get(id=int(self.kwargs["key"]))
            return queryset.get(shortname=self.kwargs["key"])
        except Election.DoesNotExist:
            raise Http404("Election result not found")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        message = email.message_from_string(self.object.result)
        context["message"] = message
        context["body"] = message.get_payload()
        return context


def result_by_msgid(request, msgid=None):
    """Return a redirect to the proper URL for a result."""
    # pylint: disable=unused-argument
    msgid = "<" + msgid + ">"
    return redirect(
        get_object_or_404(Election, status=Election.RESULT,
                          result_msgid=msgid).get_result_url(),
        permanent=True
    )


def result_raw(request, key=None):
    """Return the raw text of a statement."""
    # pylint: disable=unused-argument
    if key.isdigit():
        result = get_object_or_404(Election, status=Election.RESULT,
                                   id=key).result
    else:
        result = get_object_or_404(Election, status=Election.RESULT,
                                   shortname=key).result
    return HttpResponse(result, content_type="text/plain; charset=utf-8")


def missing(request):
    """View the list of missing files."""
    cutoff = (datetime.datetime.now() - datetime.timedelta(days=20)).date()
    results = Election.objects.exclude(hidden=True).exclude(
        result_date__gte=cutoff).filter(
            result="", status=Election.RESULT).order_by("-result_date")
    cfvs = Election.objects.exclude(hidden=True).exclude(
        cfv_date__gte=cutoff).filter(
            cfv="", status__in=(Election.ACTIVE, Election.COUNT,
                                Election.RESULT)).order_by(
                                    "-cfv_date", "-result_date")
    return render(
        request, "voting/missing.html", {
            "results": results,
            "cfvs": cfvs,
        }
    )


def status(request):
    """View the list of currently-active CFVs."""
    today = timezone.now().date()
    count = Election.objects.exclude(hidden=True).filter(
        Q(status=Election.COUNT) | Q(
            status=Election.ACTIVE, cfv_end_date__lt=today)
        ).order_by("-cfv_end_date")
    active = Election.objects.exclude(hidden=True).filter(
        status=Election.ACTIVE, cfv_end_date__gte=today
        ).order_by("-cfv_end_date")
    setup = Election.objects.exclude(hidden=True).filter(status=Election.SETUP)
    return render(
        request, "voting/status.html", {
            "count": count,
            "active": active,
            "setup": setup,
        }
    )


def pgpkeys(request):
    """View the list of votetakers' PGP keys."""
    return render(
        request, "voting/pgpkeys.html", {
            "votetakers": Votetaker.objects.filter(
                user__is_active=True).exclude(pgpkey=""),
        }
    )
