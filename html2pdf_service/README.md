# HTML2PDF service

Allows conversion of html document to pdf.

## Project setup
Install dependencies:
`pip install -r requirements-test.txt`

## Deployment
Any docker container service. For example [Google Run](https://cloud.google.com/run/docs/quickstarts/build-and-deploy)

### Submit build
Replace `PROJECT-ID` with your Google Cloud project.

`gcloud builds submit --tag gcr.io/PROJECT-ID/html2pdf --project=PROJECT-ID`

### Deploy
Replace `PROJECT-ID` with your Google Cloud project.

`gcloud beta run deploy --image gcr.io/PROJECT-ID/html2pdf --platform managed --project=PROJECT-ID` 


