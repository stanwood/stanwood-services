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
from google.appengine.api import memcache
from google.appengine.ext import ndb


@pytest.mark.webtest
@pytest.mark.skip(reason='Online test')
def test_image_online(app, jwt_token, namespace):
    image_url = ('https://upload.wikimedia.org/wikipedia/commons/thumb/e/'
                 'e4/Small-city-symbol.svg/348px-Small-city-symbol.svg.png')
    response = app.get(
        '/{}/image?url={}'.format(namespace, image_url),
        headers={'X-Auth-Token': jwt_token})
    assert response.status_code == 302


@mock.patch('handlers.upload.storage.Image.upload_blob')
@mock.patch('handlers.upload.storage.Image.fetch_image')
def test_image_unauthorized(mock_fetch_image, mock_upload_blob, app):
    mock_upload_blob.return_value = 'storage.com'
    mock_fetch_image.return_value = 'filename', '.png', 'image/png'
    namespace_name = 'test_namespace'
    image_url = ('https://upload.wikimedia.org/wikipedia/commons/thumb/e/'
                 'e4/Small-city-symbol.svg/348px-Small-city-symbol.svg.png')
    response = app.get('/{}/image?url={}'.format(namespace_name, image_url),
                       expect_errors=True)
    assert response.status_code == 401


@mock.patch('handlers.storage.GoogleCloudStorage.bucket', new_callable=mock.PropertyMock)
@mock.patch('handlers.upload.storage.Image.upload_blob')
@mock.patch('handlers.upload.storage.Image.fetch_image')
def test_image_upload(mock_fetch_image, mock_upload_blob, mock_bucket, app,
                      jwt_token, namespace):
    from models import images as images_models

    upload_blob_response = 'storage.com', '/gs/path', 'image/png'
    mock_upload_blob.return_value = upload_blob_response
    mock_fetch_image.return_value = 'filename', '.png', 'image/png'
    namespace = 'piotr_test'
    image_url = ('https://upload.wikimedia.org/wikipedia/commons/thumb/e/'
                 'e4/Small-city-symbol.svg/348px-Small-city-symbol.svg.png')
    url = '/{}/image?url={}'.format(namespace, image_url)

    response = app.get(url,
                       expect_errors=True,
                       headers={'X-Auth-Token': jwt_token})

    assert response.status_code == 302

    image_key = ndb.Key(images_models.ImageUrl,
                        images_models.ImageUrl.hash_key(url))
    image = image_key.get()

    assert image.gcs_url == upload_blob_response[0]
    assert image.original_path == url


@mock.patch('handlers.storage.GoogleCloudStorage.bucket', new_callable=mock.PropertyMock)
@mock.patch('handlers.upload.storage.Image.upload_blob')
@mock.patch('handlers.upload.storage.Image.fetch_image')
def test_image_cache_cleared(mock_fetch_image, mock_upload_blob, mock_bucket,
                             app, jwt_token, namespace):
    from models import images as images_models

    upload_blob_response = 'storage.com', '/gs/path', 'image/png'
    mock_upload_blob.return_value = upload_blob_response
    mock_fetch_image.return_value = 'filename', '.png', 'image/png'

    image_url = ('https://upload.wikimedia.org/wikipedia/commons/thumb/e/'
                 'e4/Small-city-symbol.svg/348px-Small-city-symbol.svg.png')
    url = '/{}/image?url={}'.format(namespace, image_url)
    response = app.get(url,
                       headers={'X-Auth-Token': jwt_token})
    assert response.status_code == 302
    assert mock_upload_blob.call_count == 1

    ndb.get_context()
    image_key = ndb.Key(images_models.ImageUrl,
                        images_models.ImageUrl.hash_key(url))
    image = image_key.get()
    assert image.gcs_url == upload_blob_response[0]
    assert image.original_path == url
    memcache.delete(url)

    response = app.get(url,
                       headers={'X-Auth-Token': jwt_token})

    assert response.status_code == 302
    assert mock_upload_blob.call_count == 1


def test_image_missing_url(app, jwt_token, namespace):
    response = app.get('/{}/image'.format(namespace),
                       expect_errors=True,
                       headers={'X-Auth-Token': jwt_token})
    assert response.status_code == 400
