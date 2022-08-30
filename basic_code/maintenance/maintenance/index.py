import boto3, json
import cfnresponse

def handler(event, context):
  try:
    print(event);
    tag = event['ResourceProperties']['fraudResourceTag'];
    resource = event['ResourceProperties']['resource']
    if event["RequestType"] == 'Create':
      client = boto3.client('resourcegroupstaggingapi')
      
      client.tag_resources(
        ResourceARNList=resource,
        Tags={
            tag: tag
        }
      )
      msg = "Tagged Resources"
      responseData = {}
      responseData['Data'] = msg
      cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData, event["LogicalResourceId"]);
    else:
      msg = "No work to do"
      responseData = {}
      responseData['Data'] = msg
      cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData, event["LogicalResourceId"]);
  except Exception as e:
    msg = f"Exception raised for function: Exception details: {e}"
    responseData = {}
    responseData['Data'] = msg
    cfnresponse.send(event, context, cfnresponse.FAILED, responseData, event["LogicalResourceId"]);
    
