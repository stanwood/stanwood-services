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
import datetime

import freezegun
import mock
import pytz


@freezegun.freeze_time('2017-5-11')
@mock.patch('handlers.queues.gcs_image_cleanup.storage.GoogleCloudStorage.bucket',
            new_callable=mock.PropertyMock)
def test_cleanup_images(mock_bucket, app, jwt_token, image_url, namespace):
    mock_image_to_delete = mock.MagicMock()
    mock_image_to_delete.time_created = pytz.UTC.localize(
        datetime.datetime(2017, 3, 10)
    )
    mock_image_to_delete.delete.return_value = True
    mock_image_to_delete.public_url = image_url.gcs_url
    mock_image_to_delete.metadata = {'ndb_key': image_url.key.id()}
    mock_image_not_delete = mock.MagicMock()
    mock_image_not_delete.time_created = pytz.UTC.localize(
        datetime.datetime(2017, 5, 10)
    )
    mock_image_not_delete.delete.return_value = True
    mock_list = mock.MagicMock()
    mock_list.list_blobs.return_value = [mock_image_to_delete,
                                         mock_image_not_delete]
    mock_bucket.return_value = mock_list

    url = '/_ah/queues/cleanup/{}/images'.format(namespace)
    response = app.post(url)
    assert response.status_code == 200
    assert mock_image_to_delete.delete.called is True
    assert mock_image_not_delete.delete.called is False

    image_url = image_url.key.get()
    assert image_url is None


def test_cron_cleanup_images(app, jwt_token, taskqueue, namespace):
    cron_response = app.get('/_ah/cron/cleanup-images')
    assert cron_response.status_code == 200

    tasks = taskqueue.GetTasks('gcsimages')
    assert len(tasks) == 1
    assert namespace in tasks[0]['url']
