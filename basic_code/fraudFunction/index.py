import boto3, os
import logging, json

logger = logging.getLogger()
logger.setLevel(logging.INFO)
codeBuild = boto3.client('codebuild')
fraudTimeout = int(os.environ['fraudTimeout'])
buildTimeout = int(os.environ['buildTimeout'])

def updateProjects(token=None):
  # Get all project names
  if token != None:
    projects = codeBuild.list_projects(nextToken=token)
  else:
    projects = codeBuild.list_projects()

  # For each project, set max concurrent and run time 
  for project in projects['projects']:
    updateCodeBuild = False
    response = codeBuild.batch_get_projects(names=[project])
    logger.info(json.dumps(response, default=str))
    del response['projects'][0]['arn']
    del response['projects'][0]['created']
    del response['projects'][0]['lastModified']
    del response['projects'][0]['badge']
    if (response['projects'][0]['timeoutInMinutes'] != fraudTimeout or
        response['projects'][0]['queuedTimeoutInMinutes'] != fraudTimeout or
        response['projects'][0]['concurrentBuildLimit'] != 1 or
        response['projects'][0]['environment']['computeType'] != 'BUILD_GENERAL1_SMALL'):
      updateCodeBuild = True
    if updateCodeBuild:
      response['projects'][0]['timeoutInMinutes']=buildTimeout
      response['projects'][0]['queuedTimeoutInMinutes']=buildTimeout
      response['projects'][0]['concurrentBuildLimit']=1
      response['projects'][0]['environment']['computeType']='BUILD_GENERAL1_SMALL'
      logger.info(json.dumps(response['projects'][0]))
      updateResponse = codeBuild.update_project(**response['projects'][0])

  # Loop until you go through all the tokens
  if 'token' in projects:
    updateProjects(projects['token'])

def countBuilds(nextToken=None, activeBuilds=0):
  if nextToken != None:
    buildsRet = codeBuild.list_builds(nextToken=nextToken)
  else:
    buildsRet = codeBuild.list_builds()
  logger.debug(json.dumps(buildsRet))
  response = codeBuild.batch_get_builds(ids=buildsRet['ids'])
  logger.debug(json.dumps(response, default=str))

  for build in response['builds']:
    logger.debug(f'buildId: {build["id"]}')
    logger.debug(f'build status: {build["buildStatus"]}')
    logger.debug(f'build timeout: {build["timeoutInMinutes"]}')
    logger.debug(f'build computeType: {build["environment"]["computeType"]}')
    if build['buildStatus'] == 'IN_PROGRESS':
      activeBuilds += 1
      
    # If there is a build running that has a high timeout or large compute type, stop it.
    if build["timeoutInMinutes"] > fraudTimeout or build["environment"]["computeType"] != 'BUILD_GENERAL1_SMALL':
      logger.warning(f'There is a build on the wrong instance class that will run to long. Stopping build: {build["id"]}')
      codeBuild.stop_build(id=build['id'])
      codeBuild.batch_delete_builds(ids=[build['id']])

  if 'nextToken' in buildsRet:
    countBuilds(buildsRet['nextToken'],activeBuilds)
  logger.info('Finished counting CodeBuild builds')
  logger.info(f'Active builds: {activeBuilds}')

  return activeBuilds

def endCodeBuildBuilds(nextToken=None):
  logger.info('Stopping CodeBuild builds')
  if nextToken != None:
    buildsRet = codeBuild.list_builds(nextToken=nextToken)
  else:
    buildsRet = codeBuild.list_builds()
  #stop all builds

  buildDetails = codeBuild.batch_get_builds(ids=buildsRet['ids'])
  for build in buildsRet['ids']:
    logger.warning(f'Stopping BuildId: {build} ')
    codeBuild.stop_build(id=build)

  logger.info('batch_delete_builds')
  logger.info(json.dumps(buildsRet['ids']))
  codeBuild.batch_delete_builds(ids=buildsRet['ids'])

  if 'nextToken' in buildsRet:
    endCodeBuildBuilds(buildsRet['nextToken'])
  logger.info('Finished stopping CodeBuild builds')

def endCodePipelines(nextToken=None):
  codePipeline = boto3.client('codepipeline')

  if nextToken != None:
    cpRet = codePipeline.list_pipelines(nextToken=nextToken)
  else:
    cpRet = codePipeline.list_pipelines()

  # When build stops, pipeline fails, no need for this.
  for pipeline in cpRet['pipelines']:
    exeRet = codePipeline.list_pipeline_executions(pipelineName=pipeline['name'])
    logger.info(json.dumps(exeRet, default=str))
    for exe in exeRet['pipelineExecutionSummaries']:
      logger.warning('Stopping pipeline executionId: '+exe['pipelineExecutionId'])
      try:
        codePipeline.stop_pipeline_execution(
          pipelineName=pipeline['name'],
          pipelineExecutionId=exe['pipelineExecutionId'],
          abandon=True
          )
      except:
        logger.info('no pipeline to stop')

  if 'nextToken' in cpRet:
    endCodePipelines(cpRet['nextToken'])
  logger.info('Finished removing CodePipelines')

def handler(event, context):
  # Log debug information
  logger.info(json.dumps(event))
  
  # Update the project to have correct tiemout, concurrent limit, and compute type
  # Do this every time 
  updateProjects()

  if event['detail-type'] == 'CodeBuild Build State Change':
    # Determine how many active builds there are
    activeBuilds = countBuilds()
  
    # If there are more than x active builds, end the builds and pipelines
    if activeBuilds > int(os.environ['maxBuildJobs']):
      endCodeBuildBuilds()
      endCodePipelines()
