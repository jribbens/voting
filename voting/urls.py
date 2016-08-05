"""voting URLs"""

from django.conf.urls import url
from django.views.generic.base import RedirectView, TemplateView

from . import views


# pylint: disable=invalid-name
app_name = "voting"
# pylint: enable=invalid-name


urlpatterns = [
    url(r"^$", views.home, name="home"),
    url(r"^votetakers$", views.votetakers, name="votetakers"),
    url(r"^statements/$", views.StatementList.as_view(), name="statements"),
    url(r"^statements/(?P<release_date>[0-9]{4}/[0-9]{2}/[0-9]{2})"
        r"/(?P<slug>[^/]*)$", views.StatementView.as_view(), name="statement"),
    url(r"^statements/(?P<release_date>[0-9]{4}/[0-9]{2}/[0-9]{2})"
        r"/(?P<slug>[^/]*)/raw$", views.statement_raw, name="statement_raw"),
    url(r"^results/$", views.ResultList.as_view(), name="results"),
    url(r"^results/(?P<key>[0-9a-zA-Z]+)$", views.ResultView.as_view(),
        name="result"),
    url(r"^results/(?P<key>[0-9a-zA-Z]+)/raw$", views.result_raw,
        name="result_raw"),
    url(r"^missing$", views.missing, name="missing"),
    url(r"^status$", views.status, name="status"),
    url(r"^guidelines$", TemplateView.as_view(
        template_name="voting/guidelines.html"), name="guidelines"),
    url(r"^pgpkeys$", views.pgpkeys, name="pgpkeys"),
    url(r"^resources$", TemplateView.as_view(
        template_name="voting/resources.html"), name="resources"),

    # Redirects from legacy URLs

    url(r"^who\.php$", RedirectView.as_view(
        pattern_name="voting:votetakers", permanent=True)),
    url(r"^statement\.php$", RedirectView.as_view(
        pattern_name="voting:statements", permanent=True)),
    url(r"^statements/(?P<msgid>[^@]+@.*)\.txt$", views.statement_by_msgid),
    url(r"^results/(?P<msgid>[^@]+@.*)\.txt$", views.result_by_msgid),
    url(r"^results\.php$", RedirectView.as_view(
        pattern_name="voting:results", permanent=True)),
    url(r"^missing\.php$", RedirectView.as_view(
        pattern_name="voting:missing", permanent=True)),
    url(r"^status\.php$", RedirectView.as_view(
        pattern_name="voting:status", permanent=True)),
    url(r"^guidelines\.html$", RedirectView.as_view(
        pattern_name="voting:guidelines", permanent=True)),
    url(r"^pgpkeys\.html$", RedirectView.as_view(
        pattern_name="voting:pgpkeys", permanent=True)),
    url(r"^resources\.html$", RedirectView.as_view(
        pattern_name="voting:resources", permanent=True)),
]
