import re
from functools import partial

import jsonschema
import pytz
import requests
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin,
)
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from jsonfallback.fields import FallbackJSONField

from when import schema


def decamel(name):
    if name.lower() == name:
        return name
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


class Event(models.Model):
    """
    The Event class is the central class in when.events. It contains all
    data related to an event, and is pretty much a direct mirror of the
    when.events API. Fields are influenced by the schema.org Event model,
    but extended and modified to fit our purposes.
    All fields except the URL are nullable, since they will be empty when
    the URL is added in the first place.
    """

    name = models.CharField(max_length=200, null=True, verbose_name=_("Name"))
    short_name = models.SlugField(null=True, unique=True, verbose_name=_("Short name"))

    start_date = models.DateField(null=True, verbose_name=_("Start date"))
    end_date = models.DateField(null=True, verbose_name=_("End date"))
    cfp_deadline = models.DateTimeField(null=True, verbose_name=_("CfP deadline"))
    timezone = models.CharField(
        choices=[(tz, tz) for tz in pytz.common_timezones],
        max_length=30,
        default="UTC",
        verbose_name=_("Timezone"),
    )

    organizer = models.CharField(max_length=200, null=True, verbose_name=_("Organizer"))
    email = models.EmailField(null=True, verbose_name=_("Email"))
    is_accessible_for_free = models.BooleanField(
        default=False, verbose_name=_("Is this event free?")
    )
    languages = models.CharField(
        max_length=200, null=True, verbose_name=_("Languages")
    )  # Format: ,en,de,. Use 'language_list' property for access.
    maximum_attendee_capacity = models.PositiveIntegerField(
        null=True, verbose_name=_("Maximum attendee capacity")
    )
    location = models.CharField(max_length=200, null=True, verbose_name=_("Location"))
    coordinates = models.CharField(
        max_length=50, null=True, verbose_name=_("Coordinates")
    )
    description = models.TextField(null=True, verbose_name=_("Description"))
    color = models.CharField(max_length=6, null=True, verbose_name=_("Color"))

    urls = FallbackJSONField(null=True, default=dict)

    hashtag = models.CharField(max_length=50, null=True, verbose_name=_("Hashtag"))
    social_media_accounts = FallbackJSONField(null=True, default=dict)
    tooling = FallbackJSONField(null=True)

    tags = models.TextField(
        null=True
    )  # Contains topics, locations, …. Use tag_list to access it.

    # INTERNAL FIELDS #
    data_url = models.URLField()
    state = models.CharField(
        max_length=11,
        choices=(
            ("new", "new"),
            ("ok", "ok"),
            ("unreachable", "unreachable"),
            ("error", "error"),
        ),
        verbose_name=_("State"),
    )
    needs_review = models.BooleanField(default=True)
    was_reviewed = models.BooleanField(default=False)

    @property
    def language_list(self):
        return (self.lanugages or "").strip(",").split(",")

    @language_list.setter
    def language_list(self, value):
        self.languages = "," + ",".join(value) + ","

    @property
    def tag_list(self):
        return (self.tags or "").strip(",").split(",")

    @tag_list.setter
    def tag_list(self, value):
        self.tags = "," + ",".join(value) + ","

    def _update(self, data):
        creating = self.state == 'new'
        field_list = []
        for field, value in data.items():
            if field == 'version':
                continue
            local_name = decamel(field)
            if hasattr(self, local_name[:-1] + '_list'):
                local_name = local_name[:-1] + '_list'
            if not getattr(self, local_name) == value:
                setattr(self, local_name, value)
                field_list += field
        self.state = "ok"
        self.save()
        if creating:
            content = {'action': 'create'}
        else:
            content = {'action': 'update', 'fields': field_list}
        log = Log.objects.create(
            event=self if self.pk else None,
            state=self.state,
            content=content,
            timestamp=now(),
        )
        return log

    def _fail(self, error, state="error", content=None):
        log = Log.objects.create(
            event=self if self.pk else None,
            state=state,
            content={'content': content, 'error': error},
            timestamp=now(),
        )
        self.state = state
        self.save()
        return log

    def fetch(self):
        response = requests.get(self.data_url)
        fail = partial(self._fail, content=response.content.decode())

        try:
            response.raise_for_status()
        except Exception:
            return fail(response.status_code, state="unreachable")

        try:
            content = response.json()
        except Exception as e:
            return fail(str(e))

        if content.get("version") not in schema.VERSIONS:
            return fail(
                "Unsupported version. Supported versions are: "
                + ", ".join(schema.VERSIONS)
            )

        used_schema = schema.get_schema(content.get("version"))
        try:
            jsonschema.validate(content, used_schema, format_checker=jsonschema.draft7_format_checker)
        except Exception as e:
            return fail({
                'path': [p for p in e.path],
                'message': e.message,
            })

        return self._update(content)


class Log(models.Model):
    event = models.ForeignKey(to=Event, on_delete=models.CASCADE, related_name='logs')
    state = models.CharField(
        max_length=11,
        choices=(
            ("new", "new"),
            ("ok", "ok"),
            ("unreachable", "unreachable"),
            ("error", "error"),
        ),
        verbose_name=_("State"),
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    content = FallbackJSONField(null=True)


class UserManager(BaseUserManager):
    """The user manager class."""

    def create_user(self, password: str = None, **kwargs):
        user = self.model(**kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, password: str, **kwargs):
        user = self.create_user(password=password, **kwargs)
        user.is_staff = True
        user.is_superuser = True
        user.save(update_fields=["is_staff", "is_superuser"])
        return user


class User(PermissionsMixin, AbstractBaseUser):

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"

    objects = UserManager()

    name = models.CharField(
        max_length=120,
        verbose_name=_("Name"),
        help_text=_("Please enter the name you wish to be displayed publicly."),
    )
    email = models.EmailField(
        unique=True,
        verbose_name=_("E-Mail"),
        help_text=_(
            "Your email address will be used for password resets and notification about your event/submissions."
        ),
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    pw_reset_token = models.CharField(null=True, max_length=160)
    pw_reset_time = models.DateTimeField(null=True)
