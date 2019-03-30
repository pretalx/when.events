import json
import os

from django.views.generic import TemplateView

from when.schema import get_schema


class Docs(TemplateView):
    template_name = 'events/docs.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['schema'] = get_schema('0.1.0')
        context['current_example'] = json.dumps(json.load(
            open(os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'example_event.json',
            ))
        ), indent=4)
        return context


class LogList(TemplateView):
    template_name = 'events/log.html'


class EventList(TemplateView):
    template_name = 'events/event_list.html'


class EventFeed(TemplateView):
    template_name = 'events/docs.html'


class StartPage(TemplateView):
    template_name = 'events/index.html'
