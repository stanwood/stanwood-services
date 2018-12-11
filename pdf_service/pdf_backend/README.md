# PDF backend

Splits PDF file into separate images.

## Dependencies

- [Google Cloud SDK](https://cloud.google.com/sdk/)
- [Google App Engine Flexible py3.4](https://cloud.google.com/appengine/docs/flexible/python/)


## Project setup

### Install dependencies
`$ pip install requirements.txt`

## Project deployment

## Update environment variables in `app.yaml`
```yaml
env_variables:
  GOOGLE_CLOUD_PROJECT: "<google_cloud_project>"
```

### Deploy application
`$ gcloud app deploy --project <project_name> --version <version>`
