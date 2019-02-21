# Stanwood mock API service

Simple Mock API Service using GitHub service as content delivery 

## Dependencies

* Python 3.7+
* Falcon framework
* Google App Engine Standard (py37)  (optional)
* GitHub API

## Setup & Deploy (GAE)
1. Go to GitHub [developer settings](https://github.com/settings/apps) console and and create GitHub App
2. Add required data (name, permissions (read repo), etc..)
3. Generate a Private Key (copy it and keep it safe) you will need it _app.yaml_ config
4. Go to the Install App tab in your Github application and install app to the repository where you will keep content
4. Add environment variables to _app.yaml_
5. Deploy to GAE
```bash
$ gcloud app deploy app.yaml  --project <PROJECT_ID> --version <VERSION_ID>
```

## Usage

### Get file content by sending GET request from default branch (usually master)

```bash
$ curl -X GET \
    "https://<PROJECT_ID>.appspot.com/v1/mock/<ORGANIZATION_NAME>/<REPO_NAME>/contents/<PATH_TO_FILE>"
```

### Get file content by sending GET request from selected branch/tag/commit
```bash
$ curl -X GET \
    "https://<PROJECT_ID>.appspot.com/v1/mock/<ORGANIZATION_NAME>/<REPO_NAME>/contents/<PATH_TO_FILE>?ref=<REF_NAME>"
```


### Get file content by sending mock request (any HTTP method)

```bash
$ curl -X GET/POST/DELETE/PUT/PATCH/... \
    --data '{"happy": true}' \
    -H "Content-Type: application/json" \
    "https://<PROJECT_ID>.appspot.com/v1/mock/<ORGANIZATION_NAME>/<REPO_NAME>/contents/<PATH_TO_FILE>"
```


## Code Style / formatting

Please use [black](https://github.com/ambv/black).