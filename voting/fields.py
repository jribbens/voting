"""voting field types"""

from django.core.validators import EmailValidator
from django.db.models import CharField


class EmailList(list):
    """A list of email addresses."""

    def __str__(self):
        return ", ".join(self)


class EmailListValidator(EmailValidator):
    """Validate a list of email addresses."""

    def __call__(self, value):
        for email in value:
            if email.strip():
                super().__call__(email)


class EmailListField(CharField):
    """A field that is a comma-separated list of email addresses."""
    description = "Comma-separated list of email addresses."
    default_validators = [EmailListValidator()]

    def from_db_value(self, value, expression, connection, context):
        """Converts a value as returned by the database to a Python object."""
        # pylint: disable=unused-argument
        return self.to_python(value)

    def to_python(self, value):
        if value is None or isinstance(value, EmailList):
            return value
        return EmailList(email.strip() for email in value.split(",")
                         if email.strip())

    def get_prep_value(self, value):
        return ",".join(email.strip() for email in value if email.strip())
