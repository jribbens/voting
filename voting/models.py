"""voting models."""

import re
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone

from .fields import EmailListField


def _validate_messageid(value):
    """Validate value as a Usenet Message-ID."""
    if len(value) > 250 or not re.match(r"""
            <
            [-0-9A-Za-z!#$%&'*+/=?^_`{|}~]+
            (?:\.[-0-9A-Za-z!#$%&'*+/=?^_`{|}~]+)*
            @
            (?:
                [-0-9A-Za-z!#$%&'*+/=?^_`{|}~]+
                (?:\.[-0-9A-Za-z!#$%&'*+/=?^_`{|}~]+)*
            |
                \[[!-=?-Z^-~]*\]
            )
            >$
            """, value, re.VERBOSE):
        raise ValidationError("Enter a valid Message-ID.", code="invalid")


class MessageIDField(models.CharField):
    """Field type to accept and validate Usenet Message-IDs."""
    default_validators = [_validate_messageid]
    description = "Usenet Message-ID"

    def __init__(self, *args, **kwargs):
        # max_length=250 to be compliant with RFC 5536 s3.1.3
        kwargs["max_length"] = kwargs.get("max_length", 250)
        super().__init__(*args, **kwargs)


class Votetaker(models.Model):
    """Votetaker model - effectively an extension to the django user."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True)
    role = models.CharField(
        max_length=128, blank=True,
        help_text="The votetaker's 'job title', if any.")
    public_email = models.EmailField(
        blank=True,
        help_text="If specified, this is the email address that will be"
        " displayed on public pages. Otherwise, the django User email"
        " address will be used.")
    contact = models.TextField(
        blank=True,
        help_text="Private contact details for the votetaker. These will"
        " never be displayed on any public pages.")
    pgpkey = models.TextField(
        "PGP Key", blank=True,
        help_text="The PGP public key block for the votetaker. If provided,"
        " it will be displayed on the public pages.")

    def __str__(self):
        return self.user.get_full_name()


class Statement(models.Model):
    """Statement model."""
    title = models.CharField(max_length=254)
    slug = models.SlugField(db_index=False)
    release_date = models.DateField()
    msgid = MessageIDField(
        "Message-ID",
        help_text="The Message-ID of the published statement.")
    statement = models.TextField(editable=False)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Return the canonical URL for this statement."""
        return reverse("voting:statement", kwargs={
            "release_date": self.release_date.strftime("%Y/%m/%d"),
            "slug": self.slug,
        })

    def get_raw_url(self):
        """Return the canonical URL for the raw version of this statement."""
        return reverse("voting:statement_raw", kwargs={
            "release_date": self.release_date.strftime("%Y/%m/%d"),
            "slug": self.slug,
        })

    class Meta:
        ordering = ("-release_date",)
        unique_together = ("release_date", "slug")


def _validate_shortname(value):
    """Validate value as an Election.shortname."""
    if not re.match(r"[a-z][a-z0-9]{2,7}$", value):
        raise ValidationError(
            "Enter a valid short name (between 3 and 8 lower-case letters and"
            " numbers, starting with a letter.", code="invalid")


class Election(models.Model):
    """Election model."""
    SETUP = "setup"
    ACTIVE = "active"
    COUNT = "count"
    RESULT = "result"
    ABANDONED = "abandoned"
    title = models.CharField(max_length=254)
    shortname = models.CharField(
        "Short name", max_length=8, null=True, unique=True,
        validators=[_validate_shortname],
        help_text="This is a unique short identifier for the vote."
        " It will be used as the username part of the email"
        " address for voters to request their ballot key.")
    votetaker = models.ForeignKey(Votetaker, null=True)
    secondary = models.ForeignKey(Votetaker, null=True, blank=True,
                                  related_name="secondary_election_set")
    votetype = models.CharField(
        "Vote type", max_length=64,
        choices=(
            ("Newsgroup", "Newsgroup"),
            ("Charter Change", "Charter Change"),
            ("Procedural", "Procedural"),
            ("Combined", "Combined"),
        ),
        help_text="This is just a helpful classification of what sort of"
        " election this is. Its value does not affect the operation of the"
        " election.")
    proposal = models.TextField(
        blank=True,
        help_text="This text is displayed to the voter when they are filling"
        " in their vote. It should match the rationale, summary of"
        " discussion, changes from the last RFD, and proposal, from the CFV.")
    cfv_date = models.DateField(
        "CFV date", blank=True, null=True, db_index=True,
        help_text="Votes received before this date"
        " (or if this date is not provided) will not be accepted.")
    cfv_end_date = models.DateField(
        "CFV end date", blank=True, null=True,
        help_text="Votes received after this date"
        " (or if this date is not provided) will not be accepted.")
    cfv_msgid = MessageIDField(
        "CFV Message-ID", blank=True,
        help_text="Fill this in with the Message-ID (including angle"
        " brackets) of the CFV once it appears.")
    cfv = models.TextField("CFV", editable=False)
    result_date = models.DateField(
        blank=True, null=True,
        help_text="Fill this in with the date the results posting appears.")
    result_msgid = MessageIDField(
        "Result Message-ID", blank=True,
        help_text="Fill this in with the Message-ID (including angle"
        " brackets) of the results posting once it appears.")
    result = models.TextField(editable=False)
    uk_vote = models.BooleanField(
        "uk.* vote", default=True,
        help_text="Un-tick this box if this election is not an official uk.*"
        " election whose CFV will be posted in uk.net.news.announce.")
    hidden = models.BooleanField(
        default=False,
        help_text="Tick this box to hide this vote completely from public"
        " pages (e.g. for testing).")
    status = models.CharField(
        max_length=10, default=SETUP, choices=(
            (SETUP, "Setting up"),
            (ACTIVE, "Voting in progress"),
            (COUNT, "Counting in progress"),
            (RESULT, "Result issued"),
            (ABANDONED, "Abandoned"),
        ),
        help_text=" It is vital to keep this status up-to-date. If the"
        " election is not in the 'Voting in progress' status then votes will"
        " not be accepted.")
    ballot_email = EmailListField(
        max_length=254, blank=True,
        help_text="If specified, this enables ballots-by-email. Ballot papers"
        " are automatically createed from the 'Proposal' field (which must"
        " contain the string $KEY$ for the voter's secret key). Completed"
        " votes are forwarded to all addresses in this comma-separated list.")

    class Meta:
        ordering = ("-cfv_date",)
        index_together = ("status", "result_date")

    def __str__(self):
        return self.title

    def get_result_url(self):
        """Return the URL for the result for this election."""
        return reverse("voting:result", kwargs={
            "key": self.shortname or self.id,
        })

    def get_raw_result_url(self):
        """Return the URL for the raw result for this election."""
        return reverse("voting:result_raw", kwargs={
            "key": self.shortname or self.id,
        })

    def accepting_votes(self):
        """Returns true if this election is currently accepting votes."""
        if (self.status != self.ACTIVE or not self.cfv_date or
                not self.cfv_end_date):
            return False
        today = timezone.now().date()
        return self.cfv_date <= today <= self.cfv_end_date

    def latest_date(self):
        """Returns the latest date associated with this election, or None."""
        return self.result_date or self.cfv_end_date or self.cfv_date


class Question(models.Model):
    """Question model."""
    YESNO = "yesno"
    STV = "stv"
    CONDORCET = "condorcet"
    FREEFORM = "freeform"
    election = models.ForeignKey(Election)
    question = models.CharField(
        max_length=254,
        help_text="The question the voter is answering.")
    method = models.CharField(
        max_length=16, choices=(
            (YESNO, "Yes/no"),
            (STV, "Single transferable vote"),
            (CONDORCET, "Condorcet"),
            (FREEFORM, "Free-form answer")
        ))
    details = models.TextField(
        blank=True,
        help_text="This text, if any, is displayed next to the question.")

    class Meta:
        order_with_respect_to = "election"

    def __str__(self):
        return self.question


class Choice(models.Model):
    """Choice model."""
    question = models.ForeignKey(Question)
    choice = models.CharField(max_length=254)

    def __str__(self):
        return self.choice


class Voter(models.Model):
    """Voter model."""
    key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    election = models.ForeignKey(Election, editable=False)
    email = models.EmailField(
        help_text="The address the ballot key was emailed to.")
    creation_date = models.DateTimeField(
        auto_now_add=True,
        help_text="The date/time this voter first requested a ballot key for"
        " this election.")
    vote_date = models.DateTimeField(
        blank=True, null=True,
        help_text="The date/time of the most recent vote submitted by this"
        " voter for this election.")
    name = models.CharField(
        max_length=128, blank=True,
        help_text="The voter's 'name', as supplied by them.")
    posting_address = models.CharField(
        max_length=128, blank=True,
        help_text="The voter's 'usual posting address', as supplied by them.")
    comments = models.TextField(
        blank=True,
        help_text="Any additional comments added by the voter.")
    accepted = models.BooleanField(
        default=False,
        help_text="Tick to accept the vote.")
    notes = models.TextField(
        blank=True,
        help_text="Private notes by the votetaker.")
    email_headers = models.TextField(
        help_text="The headers of the first email received requesting"
        " a ballot key.")

    class Meta:
        unique_together = ("election", "email")

    def __str__(self):
        return self.email


class VoterIPAddress(models.Model):
    """Model for the IP addresses seen in use by a voter."""
    voter = models.ForeignKey(Voter)
    creation_date = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(
        "IP address", unpack_ipv4=True, db_index=True)
    fingerprint = models.CharField(max_length=128, db_index=True)
    headers = models.TextField("HTTP headers")
    asn_info = models.CharField("AS info", max_length=250, db_index=True)
    browser_info = models.TextField()

    def __str__(self):
        return str(self.ip_address)


class Vote(models.Model):
    """Vote model."""
    voter = models.ForeignKey(Voter)
    choice = models.ForeignKey(Choice)

    def __str__(self):
        return str(self.choice)


class Email(models.Model):
    """Email model to record votes received by email."""
    voter = models.ForeignKey(Voter, related_name="vote_emails")
    received_date = models.DateTimeField(auto_now_add=True)
    email = models.TextField()
