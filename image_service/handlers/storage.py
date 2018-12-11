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
import io
import logging
import mimetypes
import StringIO
import urllib
import uuid
from os.path import splitext
from os.path import basename
from urlparse import urlparse

import google.cloud.storage
import PIL.Image
import webapp2
from google.appengine.api.app_identity import app_identity
from google.appengine.api import urlfetch
from webob.exc import HTTPServiceUnavailable


class Image(object):
    RESOLUTIONS = [4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]

    def __init__(self, bucket, hash_key):
        self.bucket = bucket
        self.hash_key = hash_key

    def __call__(self, folder_name, image_url, resize_width, crop_data):
        self.image_url = image_url
        image_data = self.fetch_image(folder_name, image_url)
        gcs_image = self.upload_blob(*image_data,
                                     resize_width=resize_width,
                                     crop_data=crop_data)
        return gcs_image

    @staticmethod
    def get_details(image_url):
        disassembled = urlparse(image_url)
        filename, extension = splitext(basename(disassembled.path))
        content_type = mimetypes.guess_type(image_url)[0]
        return filename, extension, content_type

    @classmethod
    def get_resolution(cls, width):
        return min(cls.RESOLUTIONS, key=lambda res: abs(res - int(width)))

    @staticmethod
    def crop_image(image, top, left, width, height):
        return image.crop((left, top, width, height))

    def upload_blob(self, folder_name, filename, extension, content_type,
                    content, resize_width=None, pubic=True, crop_data=None):
        file_path = ''.join([folder_name, '/', filename, extension])

        image_bytes = io.BytesIO(content)
        del content
        image = PIL.Image.open(image_bytes)

        if resize_width:
            width, height = image.size
            new_height = resize_width * height / width
            image = image.resize((resize_width, new_height), PIL.Image.ANTIALIAS)

        if crop_data:
            top, left, width, height = map(int, crop_data.split(','))
            image = self.crop_image(image, top, left, width, height)

        buf = StringIO.StringIO()
        mime_type = content_type.upper().split('/')[-1]

        if mime_type == 'JPG':
            mime_type = 'JPEG'

        image.save(buf, mime_type, quantity=100)
        width, height = image.size
        del image

        content = buf.getvalue()

        blob = self.bucket.blob(file_path)
        blob.metadata = {
            'original_url': self.image_url,
            'ndb_key': self.hash_key,
            'width': width,
            'height': height,
        }
        blob.upload_from_string(content, content_type)
        del content

        if pubic:
            blob.make_public()

        return str(blob.public_url), file_path, content_type

    def fetch_image(self, folder_name, image_url):
        filename, extension, content_type = self.get_details(image_url)
        image_url = image_url.replace(filename, urllib.quote(filename), 10)

        logging.info(image_url)

        fetched_image = urlfetch.fetch(image_url.replace(' ', '', 12))

        if fetched_image.status_code == 500:
            raise HTTPServiceUnavailable()

        content_type = fetched_image.headers.get('content-type', content_type)

        return (
            folder_name,
            filename + '-' + uuid.uuid4().hex,
            extension,
            content_type,
            fetched_image.content
        )


class GoogleCloudStorage(object):
    storage = google.cloud.storage.Client(app_identity.get_application_id())

    @webapp2.cached_property
    def bucket(self):
        return self.storage.get_bucket('{}.appspot.com'.format(
            app_identity.get_application_id(),
        ))
