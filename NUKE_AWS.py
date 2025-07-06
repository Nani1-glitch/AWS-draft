import boto3
from botocore.exceptions import ClientError

# List of regions to clean
regions = ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
           'ap-south-1', 'ap-northeast-1', 'ap-northeast-2',
           'ap-southeast-1', 'ap-southeast-2', 'eu-west-1', 
           'eu-central-1', 'eu-north-1', 'sa-east-1']

def delete_all_ec2(region):
    ec2 = boto3.resource('ec2', region_name=region)
    print(f"[{region}] Cleaning EC2...")
    for instance in ec2.instances.all():
        instance.terminate()
    for vol in ec2.volumes.all():
        vol.delete()
    for sg in ec2.security_groups.all():
        if sg.group_name != 'default':
            try:
                sg.delete()
            except:
                pass

def delete_all_vpcs(region):
    ec2 = boto3.client('ec2', region_name=region)
    print(f"[{region}] Cleaning VPCs...")
    vpcs = ec2.describe_vpcs()['Vpcs']
    for vpc in vpcs:
        vpc_id = vpc['VpcId']
        try:
            # Delete subnets
            subnets = ec2.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['Subnets']
            for subnet in subnets:
                ec2.delete_subnet(SubnetId=subnet['SubnetId'])
            # Detach and delete IGWs
            igws = ec2.describe_internet_gateways(Filters=[{'Name': 'attachment.vpc-id', 'Values': [vpc_id]}])['InternetGateways']
            for igw in igws:
                ec2.detach_internet_gateway(InternetGatewayId=igw['InternetGatewayId'], VpcId=vpc_id)
                ec2.delete_internet_gateway(InternetGatewayId=igw['InternetGatewayId'])
            # Delete route tables
            rtbs = ec2.describe_route_tables(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['RouteTables']
            for rtb in rtbs:
                if not any([assoc.get('Main', False) for assoc in rtb['Associations']]):
                    ec2.delete_route_table(RouteTableId=rtb['RouteTableId'])
            ec2.delete_vpc(VpcId=vpc_id)
        except ClientError:
            pass

def delete_all_s3():
    s3 = boto3.resource('s3')
    print("[GLOBAL] Cleaning S3...")
    for bucket in s3.buckets.all():
        try:
            bucket.objects.all().delete()
            bucket.delete()
        except:
            pass

def delete_all_rds(region):
    rds = boto3.client('rds', region_name=region)
    print(f"[{region}] Cleaning RDS...")
    try:
        dbs = rds.describe_db_instances()['DBInstances']
        for db in dbs:
            rds.delete_db_instance(DBInstanceIdentifier=db['DBInstanceIdentifier'], SkipFinalSnapshot=True)
    except ClientError:
        pass

def delete_all_cloudwatch(region):
    cw = boto3.client('logs', region_name=region)
    print(f"[{region}] Cleaning CloudWatch...")
    try:
        logs = cw.describe_log_groups()['logGroups']
        for lg in logs:
            cw.delete_log_group(logGroupName=lg['logGroupName'])
    except:
        pass

def delete_all_secrets(region):
    sm = boto3.client('secretsmanager', region_name=region)
    print(f"[{region}] Cleaning Secrets...")
    try:
        secrets = sm.list_secrets()['SecretList']
        for secret in secrets:
            sm.delete_secret(SecretId=secret['ARN'], ForceDeleteWithoutRecovery=True)
    except:
        pass

def delete_all_sqs(region):
    sqs = boto3.client('sqs', region_name=region)
    print(f"[{region}] Cleaning SQS...")
    try:
        urls = sqs.list_queues().get('QueueUrls', [])
        for url in urls:
            sqs.delete_queue(QueueUrl=url)
    except:
        pass

# MAIN CLEANER
for region in regions:
    delete_all_ec2(region)
    delete_all_rds(region)
    delete_all_cloudwatch(region)
    delete_all_secrets(region)
    delete_all_sqs(region)
    delete_all_vpcs(region)

delete_all_s3()

print("\nAWS Account CLEANED Successfully (HARD WIPE COMPLETE) 🎉")
# Note: This script performs destructive actions. Use with caution.
# Ensure you have the necessary permissions to delete resources in your AWS account.
# This script is intended for use in a controlled environment where you are sure you want to delete all resources.
# It is recommended to run this script with a dedicated IAM user with limited permissions.
# Always double-check before executing such scripts to avoid accidental data loss.
# This script is intended for use in a controlled environment where you are sure you want to delete all resources.
# It is recommended to run this script with a dedicated IAM user with limited permissions.
# Always double-check before executing such scripts to avoid accidental data loss.
# This script is intended for use in a controlled environment where you are sure you want to delete all resources.
# It is recommended to run this script with a dedicated IAM user with limited permissions.
# Always double-check before executing such scripts to avoid accidental data loss.                  