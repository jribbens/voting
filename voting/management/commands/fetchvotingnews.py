"""Import voting statements, cfvs and results from the NNTP server."""

import nntplib
import os

from django.core.management.base import BaseCommand

from ...models import Election, Statement
from ... import nntp


class Command(BaseCommand):
    """Import voting statements, cfvs and results from the NNTP server."""
    help = "Import voting statements, cfvs and results from the NNTP server."

    def handle(self, *args, **options):
        conn = None
        for statement in Statement.objects.filter(statement=""):
            conn = conn or nntp.connect()
            statement.statement = self.fetch_article(conn, statement.msgid)
            if statement.statement:
                statement.save()
        for election in Election.objects.filter(cfv="").exclude(cfv_msgid=""):
            conn = conn or nntp.connect()
            election.cfv = self.fetch_article(conn, election.cfv_msgid)
            if election.cfv:
                election.save()
        for election in Election.objects.filter(result="").exclude(
                result_msgid=""):
            conn = conn or nntp.connect()
            election.result = self.fetch_article(conn, election.result_msgid)
            if election.result:
                election.save()

    def fetch_article(self, conn, msgid):
        """Fetch an article. Returns the article content, or ""."""
        try:
            with open(os.path.join(os.path.dirname(__file__),
                                   "..", "..", "..", "old-articles",
                                   msgid[1:-1] + ".txt"),
                      encoding="iso-8859-1") as articlef:
                return articlef.read()
        except FileNotFoundError:
            pass
        try:
            response, info = conn.article(msgid)
            if response.startswith("220"):
                return b"\n".join(info.lines).decode("iso-8859-1")
            raise nntplib.NNTPError(response)
        except nntplib.NNTPError as exc:
            if not exc.response.startswith("430"):
                self.stdout.write(self.style.NOTICE(
                    "Failed to fetch article {}: {!r}".format(
                        msgid, response)))
            return ""
