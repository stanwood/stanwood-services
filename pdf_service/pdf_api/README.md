# PDF API

Allows to trigger PDF splitter and converter via REST API.

*split and convert PDF* - Once pdf is sent to `/pdf/v1/<quoted_pdf_url>` API starts splitting and converting pdf file into separate images.
If PDF is bigger than 5MB API returns `202 HTTP` status code and starts PDF processor in background.

## Dependencies

- [Google Cloud SDK](https://cloud.google.com/sdk/)
- [Google App Engine Standard py2.7](https://cloud.google.com/appengine/docs/standard/python/)
- [Google Cloud Storage](https://cloud.google.com/storage/)


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

### Update environment variables in `app.yaml`
```yaml
env_variables:
  IMAGE_SERVICE_NAMESPACE: "<service_namespace>"
  IMAGE_SERVICE_TOKEN: "<service_token>"
```

### Deploy API application
`$ appcfg.py update app.yaml -A <project_name> -V <version>`

### Deploy task queues
`$ appcfg.py update_queues .`

### Deploy cron jobs
`$ appcfg.py update_cron .`


## Example usage

### Split PDF with multiple pages into separate images

```
curl https://<project_name>.appspot.com/pdf/v1/<quoted_pdf_url>
```

### Split PDF with multiple pages into separate images enforcing async operation

```
curl https://<project_name>.appspot.com/pdf/v1/<quoted_pdf_url>?async=1
```

### Get first page of PDF as image

```bash
curl -L "https://<project_name>.appspot.com/pdf/v1/<quoted_pdf_url>/pages/1.<image_extension:png,jpg,...>"
```

### Get first page of PDF as image and resize it

```bash
curl -L "https://<project_name>.appspot.com/pdf/v1/<quoted_pdf_url>/pages/1.<image_extension:png,jpg,...>?width=1024"
```

### Get first page of PDF as image and crop it

```bash
curl -L "https://<project_name>.appspot.com/pdf/v1/<quoted_pdf_url>/pages/1.<image_extension:png,jpg,...>?crop=200,200,400,400"
```