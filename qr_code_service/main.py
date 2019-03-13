import StringIO
import json
import logging

import falcon
import google.cloud.storage
import qrcode
from google.appengine.api import app_identity


class GoogleCloudStorage(object):
    storage = google.cloud.storage.Client(app_identity.get_application_id())

    @property
    def bucket(self):
        return self.storage.get_bucket('{}.appspot.com'.format(
            app_identity.get_application_id(),
        ))

    def upload_file(self, file_path, content, content_type):
        blob = self.bucket.blob(file_path)
        blob.upload_from_file(content, content_type=content_type)

        blob.make_public()

        return blob.public_url


class QrCodeGenerator(GoogleCloudStorage):

    @staticmethod
    def build_image(data, version=1):
        qr = qrcode.QRCode(
            version=version,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=8,
            border=1,
        )
        qr.add_data(data)
        qr.make(fit=True)

        return qr.make_image(fill_color="black", back_color="white")

    def on_get(self, req, resp):
        data = req.get_param('data', required=True)
        version = req.get_param('version', required=False, default=1)
        resp_format = req.get_param('format', required=False)

        image = self.build_image(data, version=int(version))
        logging.debug(image)

        buf = StringIO.StringIO()
        image.save(buf, 'jpeg')
        buf.seek(0)

        if resp_format == 'image':
            resp.body = buf.getvalue()
            resp.content_type = 'image/jpeg'
            return

        url = self.upload_file('qrcodes/{}/{}.jpeg'.format(version, data), buf, 'image/jpeg')

        if resp_format == 'json':
            resp.body = json.dumps(
                {
                    'url': url,
                    'content_type': 'jpeg'
                }
            )
            resp.content_type = 'application/json'
            resp.status = falcon.HTTP_200

        else:
            raise falcon.HTTPMovedPermanently(location=url)


app = falcon.API()
app.add_route('/generate', QrCodeGenerator())
