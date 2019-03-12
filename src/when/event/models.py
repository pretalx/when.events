import pytz
from django.db import models


class Event(models.Model):
    """
    The event class is the central class in when.events. It contains all
    data related to an event, and is pretty much a direct mirror of the
    when.events API. Fields are influenced by the schema.org Event model,
    but extended and modified to fit our purposes.
    """

    name = models.CharField(max_length=200, null=True)
    short_name = models.SlugField(null=True, unique=True)
    url = models.URLField()

    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    cfp_deadline = models.DateTimeField(null=True)
    timezone = models.CharField(
        choices=[(tz, tz) for tz in pytz.common_timezones], max_length=30, default="UTC"
    )

    organizer = models.CharField(max_length=200, null=True)
    email = models.EmailField(null=True)
    is_accessible_for_free = models.BooleanField(default=False)
    languages = models.CharField(max_length=200, null=True)
    maximum_attendee_capacity = models.PositiveIntegerField(null=True)
    location = models.CharField(max_length=200, null=True)  # TODO: find better model
    description = models.TextField(null=True)
    color = models.CharField(max_length=6, null=True)

    home_url = models.URLField(null=True)
    ticket_url = models.URLField(null=True)
    program_url = models.URLField(null=True)
    cfp_url = models.URLField(null=True)
    coc_url = models.URLField(null=True)
    recording_url = models.URLField(null=True)
    logo_url = models.URLField(null=True)

    hashtag = models.CharField(max_length=50, null=True)
    social_media_accounts = models.TextField(null=True)

    tags = models.TextField(null=True)  # Contains topics, locations, …

    last_updated = models.DateTimeField(null=True)
    state = models.CharField(
        choices=(
            ("new", "new"),
            ("ok", "ok"),
            ("unreachable", "unreachable"),
            ("error", "error"),
        )
    )
