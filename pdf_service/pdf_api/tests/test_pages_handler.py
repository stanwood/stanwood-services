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
import json
import urllib

import mock
import pytest


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


def test_get_pages(app, mock_urlfetch, mock_response, mock_split_response):
    mock_urlfetch.fetch.side_effect = [
        mock_response,
        mock_split_response,
    ]
    document_url = 'https://this.is.my.file/name.pdf?123=213'

    response = app.get('/pdf/v1/{}'.format(urllib.quote_plus(document_url)))

    assert response.json['pages'] == len(json.loads(mock_split_response.content))
    assert mock_urlfetch.fetch.call_count == 2
    assert json.loads(mock_urlfetch.fetch.call_args[0][1])['document'] == document_url


def test_get_pages_unquoted_url(app, mock_urlfetch, mock_response, mock_split_response):
    mock_urlfetch.fetch.side_effect = [
        mock_response,
        mock_split_response,
    ]
    document_url = 'https://this.is.my.file/name.pdf?12=das'

    response = app.get('/pdf/v1/{}'.format(document_url))

    assert response.json['pages'] == len(json.loads(mock_split_response.content))
    assert json.loads(mock_urlfetch.fetch.call_args[0][1])['document'] != document_url


def test_get_pages_not_http(app, mock_urlfetch, mock_response, mock_split_response):
    mock_urlfetch.fetch.side_effect = [
        mock_response,
        mock_split_response,
    ]
    document_url = 'this.is.my.file/name.pdf?12=das'

    app.get('/pdf/v1/{}'.format(urllib.quote_plus(document_url)), status=404)


def test_get_pages_async_by_content_size(app, mock_urlfetch, mock_response, mock_split_response, taskqueue):
    mock_response.headers = {'Content-Length': 5000001}
    mock_urlfetch.fetch.side_effect = [
        mock_response,
        mock_split_response,
    ]
    document_url = 'https://this.is.my.file/name.pdf?123=213'

    response = app.get('/pdf/v1/{}'.format(urllib.quote_plus(document_url)))

    assert response.json['message'] == 'PDF split process started. Please try in few minutes.'

    assert len(taskqueue.GetTasks('default')) == 1
    assert taskqueue.GetTasks('default')[0]['url']


def test_get_pages_async(app, mock_urlfetch, mock_response, mock_split_response, taskqueue):
    mock_urlfetch.fetch.side_effect = [
        mock_response,
        mock_split_response,
    ]
    document_url = 'https://this.is.my.file/name.pdf?123=213'

    response = app.get('/pdf/v1/{}?async=1'.format(urllib.quote_plus(document_url)))

    assert response.json['message'] == 'PDF split process started. Please try in few minutes.'

    assert len(taskqueue.GetTasks('default')) == 1
    assert taskqueue.GetTasks('default')[0]['url']
