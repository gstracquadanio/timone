# timone
![](https://github.com/gstracquadanio/timone/workflows/Test%20package/badge.svg)
![](https://github.com/gstracquadanio/timone/workflows/Release%20package/badge.svg)
[![PyPI version](https://badge.fury.io/py/timone.svg)](https://badge.fury.io/py/timone)

Current version: 0.3.1

`timone` is a lightweight object router to store Git LFS objects on different storage backend, including AWS S3 compatible storage services.

## Install

```
$ pip install timone
```

## Configuration

`timone` can be configured by passing settings through environment variables, following the 12 factor principles.

### Basic settings
* **TIMONE_LOG_LEVEL**: Python logging level (default: INFO).
* **TIMONE_ENDPOINT_URL**: URL to reach service.
* **TIMONE_TOKEN_SECRET**: secret for token based authentication.
* **TIMONE_STORAGE**: storage driver to use (default: DumbStorageDriver).<br/>
 Currently supporting `S3StorageDriver`, for AWS S3 services, or `DumbStorageDriver`, for testing purposes.
* **TIMONE_OBJECT_EXPIRESIN**: object availability in seconds (default: 3600).

### S3StorageDriver settings

* **TIMONE_STORAGE_S3_URL**: S3 endpoint URL.
* **TIMONE_STORAGE_S3_REGION**: S3 region.
* **TIMONE_STORAGE_S3_BUCKET**: S3 bucket name.
* **TIMONE_STORAGE_S3_KEY**: S3 access key.
* **TIMONE_STORAGE_S3_SECRET**: S3 access secret.
* **TIMONE_STORAGE_S3_MAX_FILE**: max file size for direct upload in Mb (default: 1000).

## Authentication and authorization
`timone` implements a simple token-based authentication system based on JWT, which streamlines authentication and authorization.

You can create tokens to access `timone` using `pyjwt`. For example, you can run the following command to create a token for user _bob_:

```
$ pyjwt --key=mykey encode user=bob
```
where `key` is the `TIMONE_TOKEN_SECRET`.

## Deployment

`timone` is a WSGI application, thus it requires a WSGI HTTP Server, like `gunicorn`, to run.

You can run a `timone` instance using `gunicorn` as follows:

``` 
$ gunicorn 'timone.wsgi:run()'
```

## Configuring GIT LFS
You can use `timone` to track files for the repository `foo/bar` as follows:

```
git config -f .lfsconfig remote.origin.lfsurl https://<timone_url>/foo/bar/info/lfs
```

where _<timone_url>_ is the `timone` endpoint URL.

When pushing for the first time, Git will ask LFS credentials; here, you should use your username and token provided by the service administrator.

## Issues
Please post an issue to report a bug or request new features.

## Authors

* Giovanni Stracquadanio,  dr.stracquadanio@gmail.com
