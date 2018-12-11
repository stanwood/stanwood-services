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
import os
import subprocess
import tempfile

import google.cloud.storage
import google.cloud.exceptions
import tornado.httpclient
import tornado.ioloop
import tornado.process
import tornado.web
import tornado.gen


BUCKET = '{}.appspot.com'.format(
    os.environ['GOOGLE_CLOUD_PROJECT'],
)

tornado.httpclient.AsyncHTTPClient.configure(
    None,
    max_body_size=512*1024*1024,
)


class IndexHandler(tornado.web.RequestHandler):

    def get(self):
        self.write('Hello World!')


class RenderHandler(tornado.web.RequestHandler):

    DEVICE = {
        'jpg': 'jpeg',
        'png': 'png48',
    }
    TYPES = {
        'jpg': 'image/jpg',
        'png': 'image/png',
    }

    @tornado.gen.coroutine
    def post(self):

        # TODO type check

        request = json.loads(self.request.body)

        bucket = google.cloud.storage.Client().bucket(BUCKET)

        document = request['document']
        document = document.split('://', 1)[1]

        page = os.path.join(
            document,
            '{}.pdf'.format(request['page']),
        )
        page = bucket.blob(page)

        try:
            page = page.download_as_string()
        except google.cloud.exceptions.NotFound:
            self.abort(404)

        process = tornado.process.Subprocess(
            [
                'gs',
                '-q',
                '-sDEVICE={}'.format(self.DEVICE[request['format']]),
                '-sOutputFile=-',
                '-r300',
                '-_',
            ],
            stdin=tornado.process.Subprocess.STREAM,
            stdout=tornado.process.Subprocess.STREAM,
            stderr=subprocess.DEVNULL,
        )
        yield process.stdin.write(page)
        process.stdin.close()

        response = yield process.stdout.read_until_close()

        page = os.path.join(
            document,
            '{}.{}'.format(request['page'], request['format']),
        )
        page = bucket.blob(page)
        page.upload_from_string(
            response,
            content_type=self.TYPES[request['format']],
            predefined_acl='publicRead',
        )

        self.write(page.public_url)


class SplitHandler(tornado.web.RequestHandler):

    @tornado.gen.coroutine
    def post(self):
        request = json.loads(self.request.body)

        response = tornado.httpclient.AsyncHTTPClient()
        response = yield response.fetch(
            request['document'],
            request_timeout=60,
        )

        bucket = google.cloud.storage.Client().bucket(BUCKET)
        pages = []

        with tempfile.TemporaryDirectory() as dir:

            process = tornado.process.Subprocess(
                [
                    'pdftk',
                    '-',
                    'burst',
                    'output',
                    dir + '/' + '%d.pdf',
                ],
                stdin=tornado.process.Subprocess.STREAM,
                stdout=tornado.process.Subprocess.STREAM,
                stderr=subprocess.DEVNULL,
            )
            process.stdin.max_buffer_size = 512*1024*1024
            yield process.stdin.write(response.body)
            process.stdin.close()

            response = yield process.stdout.read_until_close()

            for root, dirs, files in os.walk(dir):

                files = (
                    page
                    for page in files
                    if page.endswith('.pdf')
                )

                for page in files:
                    blob = request['document']
                    blob = blob.split('://', 1)[1]
                    blob = blob + '/{}'.format(page)
                    blob = bucket.blob(blob)
                    blob.upload_from_filename(
                        os.path.join(dir, page),
                        content_type='application/pdf',
                        predefined_acl='publicRead',
                    )

                    pages.append(blob.public_url)

        self.write(json.dumps(pages))


if __name__ == '__main__':

    app = tornado.web.Application([
        (r'/', IndexHandler),
        (r'/render', RenderHandler),
        (r'/split', SplitHandler),
    ])
    app.listen(8080)

    tornado.ioloop.IOLoop.current().start()
