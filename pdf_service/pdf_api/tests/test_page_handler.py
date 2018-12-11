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
import mock
import pytest

from google.appengine.ext import ndb


@pytest.fixture
def mock_ndb_fetch():
    ctx = ndb.get_context()
    mock_response = mock.MagicMock(status_code=200, content='https://this.is/my.image.png')
    with mock.patch('models.documents.ndb.get_context') as mock_get_context:
        future = ndb.Future()
        future.set_result(mock_response)

        mock_urlfetch = mock.MagicMock()
        mock_urlfetch.return_value = future
        ctx.urlfetch = mock_urlfetch
        mock_get_context.return_value = ctx
        yield mock_get_context.return_value.urlfetch


def test_get_page_when_pages_downloaded(
        app, mock_urlfetch, mock_response, mock_split_response, mock_ndb_fetch, taskqueue
):
    mock_urlfetch.fetch.side_effect = [
        mock_response,
        mock_split_response,
    ]

    document = 'http://my.doc/123.pdf'
    page = '1'
    extension = 'png'
    response = app.get(
        '/pdf/v1/{document}/pages/{page}.{extension}'.format(document=document, page=page, extension=extension),
        status=302
    )

    assert response.location == 'https://this.is/my.image.png'

    assert mock_ndb_fetch.call_count == 1
    assert mock_ndb_fetch.call_args[0] == (
        'https://backend-dot-testbed-test.appspot.com/render',
        '{"document": "http://my.doc/123.pdf", "page": 1, "format": "png"}',
        'POST'
    )


def test_get_page_when_pages_not_fetched(
        app, mock_urlfetch, mock_response, mock_split_response, mock_ndb_fetch, taskqueue
):
    mock_response.headers = {'Content-Length': 5000001}
    mock_urlfetch.fetch.side_effect = [
        mock_response,
        mock_split_response,
    ]

    document = 'http://my.doc/123.pdf'
    page = '1'
    extension = 'png'
    response = app.get(
        '/pdf/v1/{document}/pages/{page}.{extension}'.format(document=document, page=page, extension=extension),
        status=202
    )

    assert response.json['message'] == 'PDF split process started. Please try in few minutes.'
