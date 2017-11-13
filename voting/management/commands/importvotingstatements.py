"""Import voting statements from a CSV file."""

import csv
import datetime

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from ...models import Statement


class Command(BaseCommand):
    """Import voting statements from a CSV file."""
    help = "Import voting statements from a CSV file."

    def add_arguments(self, parser):
        parser.add_argument("filename")

    def handle(self, **options):
        imported = 0
        with open(options["filename"], encoding="ascii",
                  newline="") as csvfile:
            for row in csv.reader(csvfile):
                title, release_date, msgid = row[1:]
                release_date = datetime.datetime.strptime(
                    release_date, "%Y-%m-%d").date()
                if Statement.objects.filter(
                        release_date=release_date, title=title):
                    continue
                Statement(
                    title=title,
                    slug=slugify(title),
                    release_date=release_date,
                    msgid=msgid,
                    statement="",
                ).save()
                imported += 1
            # pylint: disable=no-member
            self.stdout.write(self.style.SUCCESS(
                "Imported {} statement(s)".format(imported)
            ))
            # pylint: enable=no-member
