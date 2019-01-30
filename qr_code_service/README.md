# Stanwood QR code generator

Service which generates QR code for given data.

## Dependencies

* [Google App Engine Standard py27](https://cloud.google.com/appengine/docs/python/)
* [falcon](https://falconframework.org/)
* [qrcode](https://pypi.org/project/qrcode/)

## Installation

```bash
$ pip install -r requirements.txt -t ext
$ appcfg update app.yaml -A <PROJECT_ID> -V <PROJECT_VERSION>
```

## Usage

Get QR code url as url field in JSON response with lowest size
```bash
curl -X GET "https://your-app-id.appspot.com/generate?data=https%3A%2F%2Fstanwood.io&format=json&version=1
```

Get QR code url as location in redirect response with highest size
```bash
curl -X GET "https://your-app-id.appspot.com/generate?data=https%3A%2F%2Fstanwood.io&version=40
```

Get QR code direct image
```bash
curl -X GET "https://your-app-id.appspot.com/generate?data=https%3A%2F%2Fstanwood.io&format=image
```
## Note

The `version` parameter is an integer from 1 to 40 that controls the size of the QR Code (the smallest, version 1, is a 21x21 matrix). 