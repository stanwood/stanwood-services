import base64
from jose import jwt
import json
import logging
import time

import falcon
import requests

import config


class MockHandler:
    @property
    def _token(self):

        now = int(time.time())

        token = jwt.encode(
            {"iat": now, "exp": now + 10 * 60, "iss": int(config.GITHUB_APP_ID)},
            config.GITHUB_PRIVATE_KEY,
            algorithm="RS256",
        )

        response = requests.post(
            "https://api.github.com/app/installations/{}/access_tokens".format(
                config.GITHUB_INSTALLATION_ID
            ),
            headers={
                "Accept": "application/vnd.github.machine-man-preview+json",
                "Authorization": "Bearer {}".format(token),
            },
        )
        response = json.loads(response.content)

        return response["token"]

    def _fetch(self, *args, **kwargs):

        try:
            headers = kwargs["headers"]
        except KeyError:
            headers = kwargs["headers"] = {}

        headers.update(
            {
                "Accept": "application/vnd.github.machine-man-preview+json",
                "Authorization": "token {}".format(self._token),
            }
        )

        response = requests.get(*args, **kwargs)
        response = json.loads(response.content)

        if "errors" in response:
            logging.error(response)
            raise falcon.HTTPInternalServerError()

        return response

    def __call__(self, req, resp, github_path):
        api_response = self._fetch(
            f"https://api.github.com/repos/{github_path}?{req.query_string}"
        )
        try:
            response = base64.b64decode(api_response["content"])
        except KeyError:
            resp.media = {"error": "Wrong path"}
            return

        resp.body = response
