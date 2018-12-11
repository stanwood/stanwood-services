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
import datetime

import webapp2

from google.appengine.ext import ndb


class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, list):
            return map(lambda x: self.default(x), obj)
        if isinstance(obj, dict):
            return {key: self.default(value) for key, value in obj.iteritems()}
        if isinstance(obj, ndb.Model):
            return self.default(obj._to_dict())
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        if isinstance(obj, unicode) or isinstance(obj, str):
            return obj
        if isinstance(obj, ndb.Key):
            return obj.urlsafe()
        return super(JsonEncoder, self).default(obj)


class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        self.response.headers.add_header('Access-Control-Allow-Origin', '*')
        self.response.headers.add_header(
            'Access-Control-Allow-Headers',
            'Origin, Content-Type, Accept, X-Auth-Token'
        )
        webapp2.RequestHandler.dispatch(self)

    def json_response(self, data, status=200):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.status_int = status
        self.response.write(json.dumps(data, cls=JsonEncoder))
