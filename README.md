# Stanwood services

Contains various services used in stanwood. 

Includes:
* [html2pdf-service](/html2pdf_service) - Converts html to pdf
* [image-service](/image_service) - Stores and caches images using GCP. Allows to resize and crop images.
* [pdf-service](/pdf_service) - Splits PDF file with multiple pages into separate images.
* [qr-code-service](/qr_code_service) - generates QR code for given data.
* [mock-api-service](/mock_api_serivce) - Simple service for mocking API responses based on GitHub repository. 

## Usage

### PDF service


#### Split PDF with multiple pages into separate images

```
curl https://<project_name>.appspot.com/pdf/v1/<quoted_pdf_url>
```


#### Get first page of PDF as image

```bash
curl -L "https://<project_name>.appspot.com/pdf/v1/<quoted_pdf_url>/pages/1.<image_extension:png,jpg,...>"
```

### Image service

#### Create bucket and token for it

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

#### Store and cache image with auth header

```bash
curl -L "https://<project_name>.appspot.com/image?url=<image_url>" -H "X-Auth-Token: <token>" > "<image_name>"
```


#### Resize image

```bash
curl -L "https://<project_name>.appspot.com/image?url=<image_url>&width=1024" -H "X-Auth-Token: <token>" > "<image_name>"
```

#### Crop image

```bash
curl -L "https://<project_name>.appspot.com/image?url=<image_url>&crop=200,200,400,400" -H "X-Auth-Token: <token>" > "<image_name>"
```

### QR code service

#### Get QR code url as url field in JSON response with lowest size
```bash
curl -X GET "https://your-app-id.appspot.com/generate?data=https%3A%2F%2Fstanwood.io&format=json&version=1
```

#### Get QR code url as location in redirect response with highest size
```bash
curl -X GET "https://your-app-id.appspot.com/generate?data=https%3A%2F%2Fstanwood.io&version=40
```

#### Get QR code direct image
```bash
curl -X GET "https://your-app-id.appspot.com/generate?data=https%3A%2F%2Fstanwood.io&format=image
```
Note

* The `version` parameter is an integer from 1 to 40 that controls the size of the QR Code (the smallest, version 1, is a 21x21 matrix). 


### Mock API service


#### Get file content by sending GET request from default branch (usually master)

```bash
$ curl -X GET \
    "https://<PROJECT_ID>.appspot.com/v1/mock/<ORGANIZATION_NAME>/<REPO_NAME>/contents/<PATH_TO_FILE>"
```

#### Get file content by sending GET request from selected branch/tag/commit
```bash
$ curl -X GET \
    "https://<PROJECT_ID>.appspot.com/v1/mock/<ORGANIZATION_NAME>/<REPO_NAME>/contents/<PATH_TO_FILE>?ref=<REF_NAME>"
```


#### Get file content by sending mock request (any HTTP method)

```bash
$ curl -X GET/POST/DELETE/PUT/PATCH/... \
    --data '{"happy": true}' \
    -H "Content-Type: application/json" \
    "https://<PROJECT_ID>.appspot.com/v1/mock/<ORGANIZATION_NAME>/<REPO_NAME>/contents/<PATH_TO_FILE>"
```
