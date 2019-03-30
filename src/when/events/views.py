import json
import os

from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from jsonschema import validate

from when import schema


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

    def post(self, request):
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
            validate(data, used_schema)
            messages.success(request, _('Looking good!'))
        except Exception as e:
            messages.error(request, _('Invalid data: ') + e.message)
        return super().get(request)


class LogList(TemplateView):
    template_name = 'events/log.html'


class EventList(TemplateView):
    template_name = 'events/event_list.html'


class EventFeed(TemplateView):
    template_name = 'events/docs.html'


class StartPage(TemplateView):
    template_name = 'events/index.html'
