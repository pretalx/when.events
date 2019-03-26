import json
import os

VERSIONS = ['0.1.0']


def get_schema(version):
    with open(os.path.join(os.path.dirname(__file__), 'schema-' + str(version) + '.json')) as f:
        return json.load(f)
