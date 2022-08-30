import json, boto3, uuid, logging, sys, os
from datetime import datetime, timezone

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(json.dumps(event))

    # Find latest ECR image
    repositoryName = os.environ['ecrModelRepo']
    trainingFolderPath = os.environ['trainingFolderPath']
    ecr = boto3.client('ecr')
    response = ecr.describe_images(
        repositoryName=repositoryName
    )
    
    try:
        len(response['imageDetails'][0])
    except:
        e = sys.exc_info()[0]
        f = sys.exc_info()[1]
        g = sys.exc_info()[2]
        logger.error("error (No ECR images found): "+str(e) + str(f) + str(g))
        raise

    images = {}
    pubTime = 0
    for image in response['imageDetails']:
        if datetime.timestamp(image['imagePushedAt']) > pubTime:
            imageTag = image['imageTags'][0]
            pubTime = image['imagePushedAt'].timestamp()
        images[image['imageDigest']] = {'pushTime': image['imagePushedAt'], 'tag': image['imageTags'][0]} 

    accountId = context.invoked_function_arn.split(":")[4]
    region = os.environ['AWS_REGION']
    ecrArn = accountId+'.dkr.ecr.'+region+'.amazonaws.com.cn/'+repositoryName+':'+imageTag

    # Trigger the Step Functions
    stateMachineArn = os.environ['trainingStateMachine']
    buildId = str(uuid.uuid4()) # If event is empty, then create this using uuid
    functionInput = {
        'BuildId': buildId, 
        'Job': 'Job-'+buildId, 
        'Model': 'Model-'+buildId, 
        'Endpoint': 'Endpoint-'+buildId, 
        'ecrArn': ecrArn,
        'dataBucketPath': trainingFolderPath,
        'triggerSource': 'Event triggered',
        'DynamoDBTable': os.environ['DynamoDBTable'],
        'commitId': 'NA',
        'authorDate': str(datetime.now()) }

    sf = boto3.client('stepfunctions')
    response = sf.start_execution(
        stateMachineArn=stateMachineArn,
        name=buildId,
        input=json.dumps(functionInput)
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Training Job Started')
    }