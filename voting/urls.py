"""voting URLs"""

import datetime

from django.urls import path, register_converter
from django.views.generic.base import RedirectView, TemplateView

from . import views


app_name = "voting"


class DateConverter:
    """Path converter to accept a YYYY/MM/DD date."""
    regex = r'[0-9]{4}/[0-9]{2}/[0-9]{2}'

    def to_python(self, value):
        """Convert the string to a date"""
        return datetime.datetime.strptime(value, "%Y/%m/%d").date()

    def to_url(self, value):
        """Convert a date to a string"""
        return value.strftime("%Y/%m/%d")


register_converter(DateConverter, "date")


urlpatterns = [
    path("", views.home, name="home"),
    path("votetakers", views.votetakers, name="votetakers"),
    path("statements/", views.StatementList.as_view(), name="statements"),
    path("statements/<date:release_date>/<slug:slug>",
         views.StatementView.as_view(), name="statement"),
    path("statements/<date:release_date>/<slug:slug>/raw",
         views.statement_raw, name="statement_raw"),
    path("results/", views.ResultList.as_view(), name="results"),
    path("results/<slug:key>", views.ResultView.as_view(), name="result"),
    path("results/<slug:key>/raw", views.result_raw, name="result_raw"),
    path("missing", views.missing, name="missing"),
    path("status", views.status, name="status"),
    path("guidelines", TemplateView.as_view(
        template_name="voting/guidelines.html"), name="guidelines"),
    path("pgpkeys", views.pgpkeys, name="pgpkeys"),
    path("resources", TemplateView.as_view(
        template_name="voting/resources.html"), name="resources"),

    # Redirects from legacy URLs

    path("who.php", RedirectView.as_view(
        pattern_name="voting:votetakers", permanent=True)),
    path("statement.php", RedirectView.as_view(
        pattern_name="voting:statements", permanent=True)),
    path("statements/<str:msgid>", views.statement_by_msgid),
    path("results/<str:msgid>", views.result_by_msgid),
    path("results.php", RedirectView.as_view(
        pattern_name="voting:results", permanent=True)),
    path("missing.php", RedirectView.as_view(
        pattern_name="voting:missing", permanent=True)),
    path("status.php", RedirectView.as_view(
        pattern_name="voting:status", permanent=True)),
    path("guidelines.html", RedirectView.as_view(
        pattern_name="voting:guidelines", permanent=True)),
    path("pgpkeys.html", RedirectView.as_view(
        pattern_name="voting:pgpkeys", permanent=True)),
    path("resources.html", RedirectView.as_view(
        pattern_name="voting:resources", permanent=True)),
]
