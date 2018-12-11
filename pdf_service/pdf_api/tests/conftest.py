# The MIT License (MIT)
# 
# Copyright (c) 2018 stanwood GmbH
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# GAE setup
import dev_appserver

dev_appserver.fix_sys_path()
import appengine_config
from stanwood.pytest.conftest import *

import json
import urllib

import webtest
import pytest
import mock


@pytest.fixture
def testbed():
    from google.appengine.ext import testbed

    tb = testbed.Testbed()
    tb.activate()
    tb.init_app_identity_stub()
    tb.init_datastore_v3_stub()
    tb.init_memcache_stub()
    tb.init_urlfetch_stub()
    tb.init_app_identity_stub()
    tb.init_search_stub()

    base_dir = os.path.abspath((os.path.dirname(__file__)))

    tb.init_taskqueue_stub(root_path=os.path.join(base_dir, '..'))
    tb.MEMCACHE_SERVICE_NAME = testbed.MEMCACHE_SERVICE_NAME
    tb.TASKQUEUE_SERVICE_NAME = testbed.TASKQUEUE_SERVICE_NAME

    yield tb

    tb.deactivate()


@pytest.fixture
def taskqueue(testbed):

    yield testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)


@pytest.fixture
def app(testbed):
    import os
    os.environ['IMAGE_SERVICE_NAMESPACE'] = 'IMAGE_SERVICE_NAMESPACE'
    os.environ['IMAGE_SERVICE_TOKEN'] = 'IMAGE_SERVICE_TOKEN'
    from api import app
    return webtest.TestApp(app)


@pytest.fixture()
def mock_response():
    return mock.MagicMock(status_code=200, content='123456')


@pytest.fixture()
def mock_split_response(mock_response):
    mock_response.content = json.dumps(
        [1, 2, 3, 4]
    )
    yield mock_response


@pytest.fixture
def mock_urlfetch(mock_response):
    with mock.patch('models.documents.urlfetch') as mock_urlfetch:
        mock_urlfetch.fetch.return_value = mock_response
        yield mock_urlfetch
