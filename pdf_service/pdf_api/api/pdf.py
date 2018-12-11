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

from google.appengine.api import (
    app_identity,
    taskqueue,
)
from google.appengine.ext import ndb
import webapp2
import webob.exc

import stanwood.services

import config
from models.documents import (
    Document,
    Page,
)


class PagesHandler(webapp2.RequestHandler):

    @ndb.toplevel
    def get(self, document):
        """
        Splits PDF file to single PDF files.

        If PDF is bigger than 500000 bytes it is running async task to pre-split pdf.

        :param document: Document url.
        :param async: Enforce async splitting.
        :return: Pages count, if PDF is already splitted or splitted using sync option. Otherwise it returns 202 http
            status code with message that task was triggered and is processed.
        """

        async = self.request.get('async', False)

        document = urllib.unquote_plus(document)
        document = Document(
            id=document,
        )

        pages = yield document.pages.fetch_async(keys_only=True)
        app_id = app_identity.get_application_id()

        self.response.content_type = 'application/json'
        if not pages:
            pages = yield document.split(app_id=app_id, async=async)

            if not pages:
                self.response.status_code = 202
                self.response.json = {
                    'message': 'PDF split process started. Please try in few minutes.'
                }
                return

        self.response.json = {
            'pages': len(pages),
        }


class PageHandler(webapp2.RequestHandler):

    image_service = stanwood.services.ImageService(
        config.IMAGE_SERVICE_NAMESPACE,
        config.IMAGE_SERVICE_TOKEN,
    )

    @webapp2.cached_property
    def transformation(self):

        kwargs = {}

        try:
            kwargs['width'] = int(self.request.GET['width'])
        except KeyError:
            pass

        try:
            kwargs['crop'] = self.request.GET['crop']
        except KeyError:
            pass

        return kwargs

    @ndb.toplevel
    def get(self, document, page, format):

        document = urllib.unquote_plus(document)
        document = Document(
            id=document,
        )

        pages = yield document.pages.fetch_async(keys_only=True)

        if not pages:
            app_id = app_identity.get_application_id()
            pages = yield document.split(app_id)
            if not pages:
                self.response.content_type = 'application/json'
                self.response.status_code = 202
                self.response.json = {
                    'message': 'PDF split process started. Please try in few minutes.'
                }
                return

        page = ndb.Key(
            Document,
            document.key.id(),
            Page,
            int(page),
        )
        page = yield page.get_async()

        if not page:
            raise webob.exc.HTTPNotFound()
        app_id = app_identity.get_application_id()
        page = yield page.render(format, app_id)

        if self.transformation:
            page = self.image_service.Image(page)
            page = yield page.transform(**self.transformation)

        self.redirect(page.encode('utf8'))

    @ndb.toplevel
    def post(self, document, page, format):

        try:
            request = self.request.json
        except ValueError:
            request = {}

        taskqueue.add(
            queue_name='documents',
            payload=json.dumps({
                'callback': request.pop('callback', None),
                'path': self.request.path_qs,
                'request': request,
            }),
        )


class LegacyHandler(webapp2.RequestHandler):

    image_service = stanwood.services.ImageService(
        config.IMAGE_SERVICE_NAMESPACE,
        config.IMAGE_SERVICE_TOKEN,
    )

    @webapp2.cached_property
    def format(self):
        try:
            return self.request.GET['format']   # TODO list of types
        except KeyError:
            return 'pdf'

    @webapp2.cached_property
    def page(self):
        try:
            return int(self.request.GET['page'])
        except KeyError:
            return 1

    @webapp2.cached_property
    def transformation(self):

        kwargs = {}

        try:
            kwargs['width'] = int(self.request.GET['width'])
        except KeyError:
            pass

        try:
            kwargs['crop'] = self.request.GET['crop']
        except KeyError:
            pass

        return kwargs

    @ndb.toplevel
    def get(self, document):
        # TODO crop, width
        self.redirect(
            '/pdf/v1/{document}/pages/{page}.{format}{query}'.format(
                document=document,
                page=self.page,
                format=self.format,
                query='?' + urllib.urlencode(self.transformation) if self.transformation else '',
            ),
            # TODO permanent
        )
