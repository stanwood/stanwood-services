import falcon

from handlers import github_proxy

app = falcon.API(media_type=falcon.MEDIA_JSON)


app.add_sink(github_proxy.MockHandler(), prefix="/v1/mock/(?P<github_path>.+)")
