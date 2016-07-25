"""Import voting elections from a CSV file."""

import csv
import datetime

from django.core.management.base import BaseCommand

from ...models import Election, Votetaker


USERS = {
    1: "rfelton",
    2: "rirvine",
    3: "mmladenovic",
    4: "jribbens",
    5: "cdickson",
    6: "bsalter",
    7: "aford",
    8: "bjones",
    9: "sbeckwith",
    10: "rellery",
    11: "singlis",
    12: "ibowen",
    13: "ichard",
    14: "malexander",
    15: "afleming",
    16: "ijackson",
    17: "rashton",
    18: "mgoodge",
    19: "mmockford",
    20: "dmahon",
    21: "jhill",
    22: "aholden",
    23: "pscragg",
    25: "gdrabble",
    24: "dhillam",
}


def date(value):
    """Return the parsed date, or None."""
    if value and value != "\\N":
        return datetime.datetime.strptime(value, "%Y-%m-%d").date()
    return None


def votetaker(value):
    """Return a Votetaker, or None."""
    value = USERS.get(int(value), None)
    if value:
        return Votetaker.objects.filter(user__username=value).first()
    return None


class Command(BaseCommand):
    """Import voting elections from a CSV file."""
    help = "Import voting elections from a CSV file."

    def add_arguments(self, parser):
        parser.add_argument("filename")

    def handle(self, **options):
        imported = 0
        with open(options["filename"], encoding="ascii", newline="") as csvfile:
            for row in csv.reader(csvfile):
                title = row[1]
                shortname = row[13] or None
                if Election.objects.filter(
                        shortname=shortname, title=title):
                    continue
                status = {
                    "CFV in construction": Election.SETUP,
                    "Voting in progress": Election.ACTIVE,
                    "Counting in progress": Election.COUNT,
                    "Result issued": Election.RESULT,
                    "Abandoned": Election.ABANDONED,
                }.get(row[11], "")
                Election(
                    title=title,
                    shortname=shortname,
                    votetaker=votetaker(row[2]),
                    secondary=None,
                    votetype=row[3],
                    proposal="",
                    cfv_date=date(row[5]),
                    cfv_end_date=date(row[6]),
                    cfv_msgid=row[7],
                    cfv="",
                    result_date=date(row[8]),
                    result_msgid=row[9],
                    result="",
                    uk_vote=(row[10] == "Y"),
                    hidden=(row[15] == "Y"),
                    status=status,
                ).save()
                imported += 1
            # pylint: disable=no-member
            self.stdout.write(self.style.SUCCESS(
                "Imported {} election(s)".format(imported)
            ))
            # pylint: enable=no-member
