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

from google.appengine.ext import ndb
import pytz
import webapp2

from handlers import storage
from models import images as images_models


class GCSImageCleanTask(storage.GoogleCloudStorage, webapp2.RequestHandler):
    """Clean up images"""
    TIME_DAYS = 30

    def post(self, namespace):
        image_list = self.bucket.list_blobs(prefix=namespace)
        for image in image_list:
            datetime_now = pytz.UTC.localize(datetime.datetime.utcnow())
            delta_days = (datetime_now - image.time_created).days
            if delta_days >= self.TIME_DAYS:
                image.delete()
                image_url = ndb.Key(images_models.ImageUrl,
                                    image.metadata['ndb_key'])
                if image_url:
                    image_url.delete()
