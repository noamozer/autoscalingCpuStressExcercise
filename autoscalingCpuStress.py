import boto3
import time
from consts import US_WEST_2_LINUX_AMI, ELB_NAME, BASE64_ENCODED_USERDATA, AUTOSCALE_CPU_THRESHOLD
from datetime import datetime, timedelta
from operator import itemgetter

def runInstance():
    # Launch an EC2 instance and return its id

    print("Launching an instance")
    try:
        # init boto3 ec2 client
        ec2 = boto3.client('ec2')

        # run a single ec2 instance with boto3 client
        response = ec2.run_instances(
        ImageId=US_WEST_2_LINUX_AMI,
        InstanceType='t2.micro',
        MaxCount=1,
        MinCount=1,
        UserData=BASE64_ENCODED_USERDATA,
        KeyName='guestTestKey',
        Monitoring={'Enabled': True},
        SecurityGroupIds=['sg-08b3a5b9e1ef6249a'])

        # get instanceId from response
        instanceId = response['Instances'][0]['InstanceId']
        print("Got instance ID: {0}".format(instanceId))

        waitForInstanceToGetToRunningState(instanceId)
        return instanceId

    except Exception as e:
        return "Could not launch an EC2 instance. Exception: {0}".format(e)


def registerInstanceToElb(instanceId, elbName):
    # register instanceId to load balancer by elb name

    print("Registering {0} to ELB {1}".format(instanceId, elbName))
    try:
        # init boto3 elb client
        elb = boto3.client('elb')
        response = elb.register_instances_with_load_balancer(
        LoadBalancerName=elbName,
        Instances=[
            {
                'InstanceId': instanceId
            }])

        # get status code from response and check it
        responseStatusCode = response['ResponseMetadata']['HTTPStatusCode']
        if responseStatusCode == 200:
            print("Succesfully registered instance to ELB {0}".format(ELB_NAME))
        else:
            print("Could not register instance to ELB. Got status code {0}"\
                .format(responseStatusCode))

    except Exception as e:
        return "Could not register instance to ELB. Exception: {0}".format(e)


def waitForInstanceToGetToRunningState(instanceId):
    #  waits for an instance to get to a 'running' state

    instanceState = getInstanceState(instanceId)

    while (instanceState == 'pending'):
        print ("Instance is still in 'pending' state. Waiting 10 seconds...")
        time.sleep(10)
        instanceState = getInstanceState(instanceId)
    
    if  (instanceState == 'running'):
        print ("Instance {0} is now in a 'running' state".format(instanceId))
    else:
         print ("Instance {0} is not pending but is not running. "\
             "Need to check further".format(instanceId))


def getInstanceState(instanceId):
    # returns state of ec2 instanceId

    ec2 = boto3.client('ec2')
    instanceJsonDetails = ec2.describe_instances(InstanceIds=[instanceId])
    instanceState = instanceJsonDetails['Reservations'][0]['Instances'][0]['State']['Name']
    return instanceState


def monitorAndAutoscaleInstanceByCpu(instanceId):
    # monitor instance cpu
    # scale a second instance when cpu reaches 80

    print("Monitoring instance {0} cpu. Will autoscale when cpu reaches {1}"\
        .format(instanceId, AUTOSCALE_CPU_THRESHOLD))
    latestCpuMetric = getLatestAverageCpuMetricForInstance(instanceId)

    while (float(latestCpuMetric) < AUTOSCALE_CPU_THRESHOLD):
        print("Latest datapoint of instance cpu is {0}. Still not reached threshold of {1}.\n"\
            "Waiting another minute...".format(latestCpuMetric, AUTOSCALE_CPU_THRESHOLD))
        time.sleep(60)
        latestCpuMetric = getLatestAverageCpuMetricForInstance(instanceId)
    
    print ("Instance {0} had reached CPU threshold of {1}. "\
         "Launching another instance.".format(instanceId, AUTOSCALE_CPU_THRESHOLD))
    return runInstance()
    

def getLatestAverageCpuMetricForInstance(instanceId):
    # fetche cloudwatch metrics for instanceId 
    # returns the latest average cpu datapoint

    try:
        cloudwatch = boto3.client('cloudwatch')
        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': instanceId
            },],
        StartTime=datetime.utcnow() - timedelta(minutes=10),
        EndTime=datetime.now(),
        Period=60,
        Statistics=['Average'],
        Unit='Percent')

        # sort results in order to return the latest datapoint
        sortedDatapoints = sorted(response['Datapoints'], key=itemgetter('Timestamp'), reverse=True)
        latestAverageCpuMetric = sortedDatapoints[0]['Average']
        return latestAverageCpuMetric

    except Exception as e:
        return "Could not get cpu metric. Excpetion: {0}".format(e)


# main function
if __name__ == "__main__":

    # launch ec2 instance and get id
    ec2InstanceId = runInstance()
    
    # register instance to ELB
    registerInstanceToElb(ec2InstanceId, ELB_NAME)

    print ("Waiting 3 minutes for instance to boot"\
        " and for cpu metrics to get populated in Cloudwatch")
    time.sleep(180)

    # monitor instance cpu and launch a second instance 
    # when the autoscaling threshold is reached
    secondInstanceId = monitorAndAutoscaleInstanceByCpu(ec2InstanceId)

     # register second instance to ELB
    registerInstanceToElb(secondInstanceId, ELB_NAME)

    print("Finished autoscaling. "\
        "Launched and registered 2 instances succesfully: {0}, {1}".format(ec2InstanceId, 
        secondInstanceId))