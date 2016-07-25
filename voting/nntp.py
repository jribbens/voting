"""nntp interface"""

import nntplib
from urllib.parse import urlparse

from django.core.exceptions import ImproperlyConfigured

from . import settings


def connect(url=None):
    """Return an NNTP connection to the news server."""
    # pylint: disable=redefined-variable-type
    url = urlparse(url or settings.NEWS_SERVER)
    if url.scheme == "nntp":
        conn = nntplib.NNTP(url.hostname, url.port or 119)
    elif url.scheme == "nntps":
        conn = nntplib.NNTP(url.hostname, url.port or 119)
        conn.starttls()
    elif url.scheme == "snews":
        conn = nntplib.NNTP_SSL(url.hostname, url.port or 563)
    else:
        raise ImproperlyConfigured(
            "VOTING_NEWS_SERVER must be an nntp:, nntps: or snews: URL")
    if url.username:
        conn.login(url.username, url.password)
    return conn
