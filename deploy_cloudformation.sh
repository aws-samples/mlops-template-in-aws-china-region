#!/usr/bin/env bash

source .env

./auto-pre.sh

echo S3ResourceBucket="bucket-$AWS_REGION-$PROJECT_NAME-$STAGE"

aws cloudformation deploy\
    --template-file "cloudformation.yaml"\
    --region "$AWS_REGION"\
    --stack-name "$PROJECT_NAME-$STAGE"\
    --capabilities CAPABILITY_NAMED_IAM \
    --parameter-overrides \
    S3PathPrefix="$PROJECT_NAME-$STAGE" \
    S3ResourceBucket="bucket-$AWS_REGION-$PROJECT_NAME-$STAGE"