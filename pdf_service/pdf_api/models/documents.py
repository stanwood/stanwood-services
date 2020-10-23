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
import logging

from google.appengine.api import taskqueue
from google.appengine.api import urlfetch
from google.appengine.ext import deferred
from google.appengine.ext import ndb
import stanwood.ndb

class Document(ndb.Model):

    DEADLINE = 60

    @property
    def pages(self):
        return Page.query(
            ancestor=self.key,
        )

    @classmethod
    def split_document(cls, app_id, service, doc_id, timeout, key_urlsafe):
        logging.debug(doc_id)
        response = urlfetch.fetch(
            'https://{service_name}-dot-{app_id}.appspot.com/split'.format(
                service_name=service,
                app_id=app_id
            ),
            json.dumps({
                'document': doc_id,
            }),
            'POST',
            deadline=timeout,
        )

        if response.status_code != 200:
            logging.critical('PDF backend returned status code: {}'.format(str(response.status_code)))
            raise Exception(response.content)  # TODO

        logging.debug(response.content)

        response = json.loads(response.content)
        response = ndb.put_multi([
            Page(
                id=page,
                parent=ndb.Key(Document, doc_id),
            )
            for page in xrange(1, len(response) + 1)  # TODO enumerate real pages?
        ])

        return response

    @ndb.tasklet
    def split(self, app_id, async=False):
        """
        Splits pdfs into single pages.
        If PDF is bigger than 500000 bytes then it runs async task to split the file.

        :param app_id: GAE application id.
        :param async: Flag to enforce async option.
        """

        lock = stanwood.ndb.Lock(self.key.urlsafe())
        event = stanwood.ndb.Event(self.key.urlsafe())

        try:
            yield lock.acquire(timeout=0)   # we don't want to release it!
        except stanwood.ndb.TimeoutError:
            yield event.wait()
            return
            # pages = yield self.pages.fetch_async(keys_only=True)
            # raise ndb.Return(pages)

        yield event.set()
        resp = urlfetch.fetch(self.key.id(), method='HEAD', deadline=60, follow_redirects=True)

        if int(resp.headers.get('Content-Length', 0)) > 5000000:
            async = True

        if async:
            try:
                deferred.defer(
                    Document.split_document, app_id, 'backend', self.key.id(), self.DEADLINE * 10, self.key.urlsafe(),
                    _name='tasks-' + self.key.urlsafe()
                )
            except (taskqueue.TombstonedTaskError, taskqueue.TaskAlreadyExistsError):
                logging.error('Task duplicated: {}'.format(self.key.urlsafe()))
                pass

            yield event.set()
            return
        else:
            response = self.split_document(app_id, 'backend', self.key.id(), self.DEADLINE, self.key.urlsafe())
            yield event.set()
            raise ndb.Return(response)


class Page(ndb.Model):

    DEADLINE = 60

    jpg = ndb.StringProperty(indexed=False)
    pdf = ndb.StringProperty(indexed=False)
    png = ndb.StringProperty(indexed=False)

    def __getitem__(self, key):
        return getattr(self, key)

    @ndb.transactional
    def __setitem__(self, key, value):

        page = self.key.get()
        setattr(page, key, value)
        page.put()

    @property
    def document(self):
        return self.key.parent()

    @property
    def number(self):
        return self.key.id()

    @ndb.tasklet
    def render(self, format, app_id):

        response = self[format]

        if response:
            raise ndb.Return(response)

        key = '{}:{}'.format(
            self.key.urlsafe(),
            format,
        )
        lock = stanwood.ndb.Lock(key)
        event = stanwood.ndb.Event(key)

        try:
            yield lock.acquire(timeout=0)   # we don't want to release it!
        except stanwood.ndb.TimeoutError:
            yield event.wait()
            page = yield self.key.get_async(use_cache=False)
            raise ndb.Return(page[format])

        response = yield ndb.get_context().urlfetch(
            'https://backend-dot-{app_id}.appspot.com/render'.format(app_id=app_id),
            json.dumps({
                'document': self.document.id(),
                'format': format,
                'page': self.number,
            }),
            'POST',
            deadline=self.DEADLINE,
        )

        if response.status_code != 200:
            raise Exception(response.content)   # TODO

        response = response.content
        response = response.replace('%2F', '/')  # TODO lame

        self[format] = response

        yield event.set()
        raise ndb.Return(response)
