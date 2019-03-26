import json
import requests

import pytest

from when.events.models import Event

class MockResponse:

    def __init__(self, json_content, status_code=200, url=None):
        self.status_code = status_code
        self.url = url
        self._content = json_content

    def json(self):
        return self._content

    @property
    def content(self):
        return json.dumps(self._content).encode()

    def raise_for_status(self):
        if self.status_code != 200:
            raise Exception


@pytest.mark.django_db
def test_base_event(monkeypatch):
    with open('example_event.json') as f:
        example_content = json.load(f)

    def mock_get(url):
        return MockResponse(example_content, url=url)

    monkeypatch.setattr(requests, 'get', mock_get)

    event = Event.objects.create(data_url='http://localhost')
    event.fetch()
    assert event.state == 'ok', event.last_response


@pytest.mark.django_db
def test_base_event_failure(monkeypatch):
    with open('example_event.json') as f:
        example_content = json.load(f)

    example_content.pop('name')

    def mock_get(url):
        return MockResponse(example_content, url=url)

    monkeypatch.setattr(requests, 'get', mock_get)

    event = Event.objects.create(data_url='http://localhost')
    assert not event.fetch()
    assert event.state == 'error'
