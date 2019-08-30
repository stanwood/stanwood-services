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
import logging

from google.appengine.api import memcache
from google.appengine.ext import ndb
import webapp2

from models import images as images_models
from handlers import storage
import decorators


class Image(storage.GoogleCloudStorage, webapp2.RequestHandler):
    CACHE_SECONDS = 60 * 60 * 24

    def dispatch(self):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = (
            'content-type,X-Auth-Token'
        )
        return super(Image, self).dispatch()

    @decorators.token_required
    def get(self, namespace):
        url = self.request.get('url')
        crop_data = self.request.get('crop')
        width = self.request.get('width', '')
        trim_whitespaces = self.request.get('trim_whitespaces')

        if not url:
            error_message = 'Missing parameter: url'
            logging.warning(error_message)
            self.abort(400, error_message)
        if width:
            width = storage.Image.get_resolution(width)

        memcache_key = '{}:{}:{}'.format(url, width, crop_data)
        cached_url = memcache.get(memcache_key, namespace=namespace)
        if cached_url:
            logging.info('Taken from cache {}'.format(memcache_key))
            gcs_image_url = cached_url
        else:
            hash_key = images_models.ImageUrl.hash_key(self.request.path_qs)
            image_url_key = ndb.Key(images_models.ImageUrl, hash_key)
            image_url = image_url_key.get()

            if image_url:
                gcs_image_url = image_url.gcs_url
            else:
                get_resize_url = storage.Image(
                    self.bucket,
                    hash_key=hash_key
                )

                gcs_image_url, gcs_path, content_type = get_resize_url(
                    namespace,
                    url,
                    width,
                    crop_data,
                    trim_whitespaces,
                )
                images_models.ImageUrl(
                    key=image_url_key,
                    gcs_url=gcs_image_url,
                    original_path=self.request.path_qs,
                    gcs_path=gcs_path,
                ).put()
            memcache.set(memcache_key, gcs_image_url, namespace=namespace, time=self.CACHE_SECONDS)

        self.redirect(str(gcs_image_url))
