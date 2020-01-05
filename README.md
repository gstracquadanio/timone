# timone
![](https://github.com/gstracquadanio/timone/workflows/Test%20package/badge.svg)
![](https://github.com/gstracquadanio/timone/workflows/Publish%20package/badge.svg)

Current version: 0.0.3

`timone` is a lightweight object router to store Git LFS objects on different storage backend, including S3 compatible systems.

`timone` implements a simple token-based authentication system based on JWT, which streamlines authentication and authorization.

## Install
`timone` requires `python>=3.7` and can be installed as follows:
```
$ pip install timone
```

## Configuration

`timone` adheres to the 12 factor principles to manage settings.


```
# timone service parameters
TIMONE_ENDPOINT_URL=http://127.0.0.3:8000
TIMONE_TOKEN_SECRET=mykey
TIMONE_STORAGE=S3Storage
TIMONE_OBJECT_EXPIRESIN=3600

# timone storage parameters for s3-like storage
TIMONE_STORAGE_S3_URL=https://s3.wasabisys.com
TIMONE_STORAGE_S3_REGION=eu-central-1
TIMONE_STORAGE_S3_BUCKET=bucket-xyz
TIMONE_STORAGE_S3_KEY=xxxx
TIMONE_STORAGE_S3_SECRET=yyy
```

## Deployment

`timone` is a WSGI application, thus it requires a WSGI HTTP Server, like `gunicorn`, to run.

You can run your `timone` instance using `gunicorn` as follows:

``` 
$ gunicorn 'timone.wsgi:run()'
```

You can then create token to access the service using `pyjwt`. For example, you can run the following command to create a token for user _bob_:

```
$ pyjwt --key=mykey encode user=bob
```
where `key` is the `TIMONE_TOKEN_SECRET`.

## Authors

* Giovanni Stracquadanio, dr.stracquadanio@gmail.com
