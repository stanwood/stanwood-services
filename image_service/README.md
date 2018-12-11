# Stanwood Image Service

Stores images in Google Cloud Storage and caches the urls.

*Resize* - Takes `width` query parameter and resize image to the width close to one of values:
 `[4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]`

*Crop* - Takes `crop` query parameter and crop image with given pattern: 
`crop=top,left,right,bottom`


## Dependencies

- [Google Cloud SDK](https://cloud.google.com/sdk/)
- [Google App Engine Standard py2.7](https://cloud.google.com/appengine/docs/standard/python/)
- [Python 2.7](https://www.python.org/downloads/release/python-2715/)
- [Google Cloud Store](https://cloud.google.com/storage/)


## Project setup

### Install dependencies
```bash
$ pip install -r requirements.txt -t ext/
$ pip install -r requirements-test.txt
```

### Run tests
`$ pytest -v tests/`

### Setup local server
`$ dev_appserver.py .`

## Project deployment

## Update environment variables in `app.yaml`
```yaml
env_variables:
    JWT_SECRET: "XXX..."
```

### Deploy API application
`$ appcfg.py update app.yaml -A <project_name> -V <version>`

### Deploy task queues
`$ appcfg.py update_queues .`

### Deploy cron jobs
`$ appcfg.py update_cron .`


## Example usage

### Create bucket and token for it

I recommend to open it in browser with logged in GCP account.
```
curl https://<project_name>.appspot.com/<namespace>/tokens 
```

Response:
```python
{
    'namespace': '<namespace>',
    'token': 'XXXXXXXXXXXXX'
}
```

### Store and cache image with auth header

```bash
curl -L "https://<project_name>.appspot.com/image?url=<image_url>" -H "X-Auth-Token: <token>" > "<image_name>"
```

### Store and cache image with token in query_param

```bash
curl -L "https://<project_name>.appspot.com/image?url=<image_url>&token=<token>" > "<image_name>"
```

### Resize image

```bash
curl -L "https://<project_name>.appspot.com/image?url=<image_url>&width=1024" -H "X-Auth-Token: <token>" > "<image_name>"
```

### Crop image

```bash
curl -L "https://<project_name>.appspot.com/image?url=<image_url>&crop=200,200,400,400" -H "X-Auth-Token: <token>" > "<image_name>"
```
