#!/usr/bin/env python
import os

import re
import yaml


def render_yaml(file_name):
    with open(file_name) as src:
        app = yaml.load(src.read())

    for key in app['env_variables']:
        try:
            app['env_variables'][key] = os.environ[key]
        except KeyError:
            pass

    app = yaml.dump(app, default_flow_style=False)
    app = re.sub(r'\n([a-z])', r'\n\n\1', app)
    with open(file_name, 'w') as config_file:
        config_file.write(app)


if '__main__' == __name__:

    # TODO: Update list of yaml files to be populated
    for file_name in ('image_service/app.yaml', 'pdf_service/pdf_api/app.yaml', 'pdf_service/pdf_backend/app.yaml'):
        render_yaml(file_name)
