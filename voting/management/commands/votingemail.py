"""Receive a vote-related email, store and process it."""

from email import message_from_bytes
from email.utils import formataddr, parseaddr
import os
import re
import sys
from uuid import UUID

from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand
from django.core.validators import EmailValidator
from django.utils import timezone

from ...models import Election, Voter


class Command(BaseCommand):
    """Receive a vote-related email, store and process it."""
    help = """Receive a vote-related email, store and process it."""

    def add_arguments(self, parser):
        parser.add_argument(
            "--type", choices=("request", "vote", "bounce"),
            required=True, help="The type of email received",
        )
        parser.add_argument(
            "--sender", required=True, help="The sender of the email",
        )
        parser.add_argument(
            "--election", required=True,
            help="The election the email relates to",
        )

    def handle(self, **options):
        # pylint: disable=no-member
        raw_msg = sys.stdin.buffer.read()
        # pylint: enable=no-member
        election = Election.objects.filter(
            shortname__iexact=options["election"]).first()
        if not election:
            self.stdout.write("Sorry, that election could not be found.\n")
            sys.exit(os.EX_NOUSER)
        if not election.ballot_email:
            self.stdout.write(
                "Sorry, that election is not using ballots-by-email.\n")
            sys.exit(os.EX_NOUSER)
        if options["type"] == "request":
            self.handle_request(election, options["sender"], raw_msg)
        elif options["type"] == "vote":
            self.handle_vote(election, options["sender"], raw_msg)
        elif options["type"] == "bounce":
            self.handle_bounce(election, options["sender"], raw_msg)

    def handle_request(self, election, sender, raw_msg):
        """Handle an email requesting a ballot paper."""
        today = timezone.now().date()
        if (election.status != Election.ACTIVE or
                not election.cfv_date or not election.cfv_end_date or
                not election.cfv_date <= today <= election.cfv_end_date):
            self.stdout.write(
                "Sorry, that election is not currently accepting votes.\n")
            sys.exit(os.EX_NOUSER)
        msg = message_from_bytes(raw_msg)
        recipient = ""
        if msg["subject"]:
            for word in msg["subject"].split():
                try:
                    EmailValidator()(word)
                    recipient = word
                    break
                except ValidationError:
                    pass
        if msg["reply-to"] and not recipient:
            recipient = parseaddr(msg["reply-to"])[1]
        if msg["from"] and not recipient:
            recipient = parseaddr(msg["from"])[1]
        recipient = recipient or sender
        voter = Voter.objects.get_or_create(
            election=election,
            email__iexact=recipient,
            defaults={
                "email": recipient,
                "email_headers": msg.as_string().split("\n\n", 1)[0],
            }
        )[0]
        EmailMessage(
            subject="Ballot paper for election: " + election.title,
            body=(election.proposal.replace("$KEY$", str(voter.key)).
                  replace("$FROM$", recipient).
                  replace("\r", "")),
            from_email=("UKVoting Autoresponder <{}@bounce.ukvoting.org.uk>".
                        format(election.shortname)),
            to=(recipient,),
            reply_to=("{}@vote.ukvoting.org.uk".format(election.shortname),),
        ).send()

    def handle_vote(self, election, sender, raw_msg):
        """Handle an email containing a filled ballot paper."""
        today = timezone.now().date()
        if (election.status != Election.ACTIVE or
                not election.cfv_date or not election.cfv_end_date or
                not election.cfv_date <= today <= election.cfv_end_date):
            self.stdout.write(
                "Sorry, that election is not currently accepting votes.\n")
            sys.exit(os.EX_NOUSER)
        msg = message_from_bytes(raw_msg)
        voter = None
        for secret in re.findall(
                rb"[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}",
                raw_msg):
            voter = Voter.objects.filter(
                election=election, key=UUID(secret.decode("ascii"))).first()
            if voter:
                break
        if not voter:
            self.stdout.write(
                "Sorry, but we could not find your voter key in your email.\n")
            sys.exit(os.EX_DATAERR)
        EmailMessage(
            subject="Voting paper for election: " + election.title,
            body="Sender: {}\nVoting key: {}\nVoter: {}".format(
                sender, voter.key, voter.email),
            from_email=formataddr((msg["from"] or "None",
                                   "bounce@ukvoting.org.uk")),
            to=election.ballot_email,
            attachments=(
                (None, msg, "message/rfc822"),
            ),
        ).send()
        voter.vote_date = timezone.now()
        voter.save()

    def handle_bounce(self, election, sender, raw_msg):
        """Handle an email bouncing a ballot paper."""
        pass
