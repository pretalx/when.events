import json
import os

VERSIONS = ['0.1.0']


def get_schema(version):
    return json.load(os.path.join(os.path.basename(__file__), 'schema-' + str(version) + '.json'))
