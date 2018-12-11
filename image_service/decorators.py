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
import base64

from google.appengine.api import datastore_errors
import jwt

from models import authorization as auth_models
import config


def token_required(func):
    """Secures handlers with auth token taken from ndb"""
    def func_wrapper(self, *args, **kwargs):
        auth_token = self.request.headers.get('X-Auth-Token',
                                              self.request.get('token', ''))
        namespace = self.request.route_kwargs.get('namespace', '')
        try:
            token = base64.urlsafe_b64decode(str(auth_token))
        except TypeError:
            self.abort(412, 'Please update your token')
        try:
            token = auth_models.AuthToken.query(
                auth_models.AuthToken.token == token
            ).get()
        except datastore_errors.BadValueError:
            self.abort(401, 'Incorrect token')
        try:
            payload = jwt.decode(token.token, config.JWT_SECRET,
                                 algorithms=config.JWT_HASH_ALGORITHM)
        except (jwt.DecodeError, AttributeError):
            return self.abort(401)
        if payload['namespace'] != namespace:
            return self.abort(412, 'Token payload is incorrect.')
        return func(self, *args, **kwargs)
    return func_wrapper
