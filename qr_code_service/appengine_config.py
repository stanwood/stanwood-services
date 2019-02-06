import os
from google.appengine.ext import vendor

# Third-party libraries are stored in "ext", vendoring will make
# sure that they are importable by the application.
vendor.add(os.path.join(os.path.dirname(__file__), 'ext'))

import requests
from requests_toolbelt.adapters import appengine
appengine.monkeypatch()