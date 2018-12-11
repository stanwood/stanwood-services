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
import json

from google.appengine.api import app_identity
from google.appengine.ext import ndb
import webapp2


class DocumentsQueueHandler(webapp2.RequestHandler):

    @ndb.toplevel
    def post(self):

        retries = self.request.headers['X-AppEngine-TaskRetryCount']
        retries = int(retries)

        ctx = ndb.get_context()
        task = json.loads(self.request.body)

        response = yield ctx.urlfetch(
            'https://{HOST}{document}'.format(
                HOST=app_identity.get_default_version_hostname(),
                document=task['path'],
            ),
            follow_redirects=False,
            deadline=45,
        )

        if response.status_code / 400 and retries < 3:
            logging.error(response.content)
            self.abort(response.status_code)

        if task['callback']:

            request = task['request']
            request.update({
                'location': response.headers['location'],
            })

            response = yield ctx.urlfetch(
                task['callback'],
                method='POST',
                payload=json.dumps(request),
                headers={
                    'Content-Type': 'application/json',
                },
            )

            if response.status_code / 400 and retries < 6:
                logging.error(response.content)
                self.abort(503)
