"""voting_extras template library"""

from django import template
from django.utils.encoding import force_text
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter
def escape_all(value):
    """HTML entity-escape all characters in the string."""
    return mark_safe(
        "".join("&#{};".format(ord(c)) for c in force_text(value))
    )


@register.simple_tag
def mailto_link(value, text=None):
    """
    Turn an email address into a mailto link.
    The email address is obfuscated with HTML entities to try and prevent
    address harvesting.
    If a second argument is provided then it is used as the link text,
    otherwise the email address itself is used.
    """
    return mark_safe(
        '<a href="{0}">{1}</a>'.format(
            escape_all("mailto:" + value),
            conditional_escape(text) if text else escape_all(value)
        )
    )
