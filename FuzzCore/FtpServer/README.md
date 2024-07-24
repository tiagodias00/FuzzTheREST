
## Docker

To start the server via docker, please run the following commands:
```sh
docker build -t ftpserver .
docker run -d -e OPENAPI_BASE_PATH=/v3 -p 80:8080 openapitools/openapi-petstore
```

