import json
import os

import jsonschema
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView

from when import schema
from when.events.models import Event, Log


class Docs(TemplateView):
    template_name = 'events/docs.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['schema'] = schema.get_schema('0.1.0')
        context['current_example'] = json.dumps(json.load(
            open(os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'example_event.json',
            ))
        ), indent=4)
        return context


class Validator(TemplateView):
    template_name = 'events/validator.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['received'] = getattr(self, 'received', None)
        return context

    def post(self, request):
        self.received = request.POST.get('data')
        try:
            data = json.loads(request.POST.get('data'))
            version = data.get('version')
        except Exception as e:
            messages.error(request, _('Could not parse data: ') + str(e))
            return super().get(request)
        if not version or version not in schema.VERSIONS:
            messages.error(request, _('Incorrect schema version supplied. Supported versions are: ') + ', '.join(schema.VERSIONS))
            return super().get(request)
        used_schema = schema.get_schema(data.get("version"))
        try:
            jsonschema.validate(data, used_schema, format_checker=jsonschema.draft7_format_checker)
            messages.success(request, _('Looking good!'))
        except Exception as e:
            message = e.message
            if e.path:
                message += ' (in ' + ', '.join(['"{}"'.format(p) for p in e.path]) + ')'
            messages.error(request, _('Invalid data: ') + message)
        return super().get(request)


class LogList(TemplateView):
    template_name = 'events/log.html'


class EventList(TemplateView):
    template_name = 'events/event_list.html'


class EventFeed(TemplateView):
    template_name = 'events/docs.html'


class StartPage(TemplateView):
    template_name = 'events/index.html'

    def post(self, request):
        url = request.POST.get('url').lower().strip()
        if not url.startswith('http'):
            messages.error(request, _('This URL is invalid. Please provide a HTTP or HTTPS URL.'))
            return super().get(request)
        event, created = Event.objects.get_or_create(data_url=url)
        if created:
            Log.objects.create(event=event, state='new')
        log = event.fetch()
        if event.state != 'ok':
            messages.error(request, _('There was an error when fetching the event.'))
        elif created:
            messages.success(request, _('The event was successfully created!'))
        else:
            messages.success(request, _('The event was successfully updated!'))
        return redirect('/logs#log-' + str(log.id))
