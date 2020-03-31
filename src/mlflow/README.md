## Testing Notes
1. build
``Shell
    docker build -t mlflow:latest --build-arg BUCKET=haas-dev-bucket-ussyc6snzrn0 .
``
2. Ryn
```shell
    AWS_ACCESS_KEY_ID=$(aws --profile default configure get aws_access_key_id)

    AWS_SECRET_ACCESS_KEY=$(aws --profile default configure get aws_secret_access_key)

    docker run -it --rm -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY -e bucket=haas-dev-bucket-ussyc6snzrn0 mlflow:latest
```