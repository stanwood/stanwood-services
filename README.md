# Stanwood services

Contains various services used in stanwood. 

Includes:
* [image-service](/image_service) - Stores and caches images using GCP. Allows to resize and crop images.
* [pdf-service](/pdf_service) - Splits PDF file with multiple pages into separate images.

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
