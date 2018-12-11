# PDF service

Google App Engine instance which allows to split and convert PDF files into separate images.

## Dependencies

- [Google Cloud SDK](https://cloud.google.com/sdk/)
- [Google App Engine Standard py2.7](https://cloud.google.com/appengine/docs/standard/python/)
- [Google App Engine Flexible py3.4](https://cloud.google.com/appengine/docs/flexible/python/)
- [Google Cloud Storage](https://cloud.google.com/storage/)

## Data flow

1. PDF url should be send using [pdf_api](/pdf_service/pdf_api) to the split endpoint
2. API splits the PDF file and returns number of split pages if PDF file size is less than 5MB. 
Otherwise it triggers background task.
3. Due to GAE Standard limitations *pdf_api* uses [pdf_backend](/pdf_service/pdf_backend) to convert PDF into images.


## Modules

* [pdf_api](/pdf_service/pdf_api)
* [pdf_backend](/pdf_service/pdf_backend)
