"""voting URLs"""

from django.conf.urls import url
from django.views.generic.base import RedirectView

from . import views


# pylint: disable=invalid-name
app_name = "voting"
# pylint: enable=invalid-name


urlpatterns = [
    url(r"^$", views.home, name="home"),
    url(r"^votetakers$", views.votetakers, name="votetakers"),

    # Legacy URLs

    url(r"^who\.php$", RedirectView.as_view(
        pattern_name="voting:votetakers", permanent=True)),
]
