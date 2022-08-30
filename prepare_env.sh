#!/usr/bin/env bash

source .env

git clone https://github.com/mlzoo/iris.git
mv iris/ dataset/

aws s3api create-bucket --bucket bucket-$AWS_REGION-$PROJECT_NAME-$STAGE --region ${AWS_REGION}  --create-bucket-configuration LocationConstraint=${AWS_REGION}

# aws s3 cp basic_code
aws s3 cp basic_code/ s3://bucket-${AWS_REGION}-${PROJECT_NAME}-${STAGE}/${PROJECT_NAME}-$STAGE/scripts/ --recursive

# aws s3 cp layers
aws s3 cp layers/ s3://bucket-${AWS_REGION}-${PROJECT_NAME}-${STAGE}/lambdaLayers/ --recursive

# aws s3 cp data
aws s3 cp dataset/ s3://bucket-${AWS_REGION}-${PROJECT_NAME}-${STAGE}/${PROJECT_NAME}-$STAGE/scripts/data/ --recursive
