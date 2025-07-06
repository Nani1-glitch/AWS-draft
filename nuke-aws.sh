#!/bin/bash

echo "🔥 NUKING AWS RESOURCES 🔥"

echo "➡️ Terminating EC2 instances..."
aws ec2 describe-instances --query 'Reservations[*].Instances[*].InstanceId' --output text | \
xargs -n1 aws ec2 terminate-instances --instance-ids

echo "➡️ Releasing Elastic IPs..."
# First disassociate EIPs
aws ec2 describe-addresses --query 'Addresses[*].AssociationId' --output text | \
xargs -n1 -I {} aws ec2 disassociate-address --association-id {}

# Then release them
aws ec2 describe-addresses --query 'Addresses[*].AllocationId' --output text | \
xargs -n1 -I {} aws ec2 release-address --allocation-id {}

echo "➡️ Deleting Lambda functions..."
aws lambda list-functions --query 'Functions[*].FunctionName' --output text | \
xargs -n1 aws lambda delete-function --function-name

echo "➡️ Deleting S3 buckets..."
for bucket in $(aws s3api list-buckets --query "Buckets[].Name" --output text); do
  aws s3 rb s3://$bucket --force
done

echo "➡️ Deleting SNS topics..."
aws sns list-topics --query 'Topics[*].TopicArn' --output text | \
xargs -n1 aws sns delete-topic --topic-arn

echo "➡️ Deleting SQS queues..."
for url in $(aws sqs list-queues --query 'QueueUrls' --output text); do
  aws sqs delete-queue --queue-url $url
done

echo "➡️ Deleting RDS databases..."
for db in $(aws rds describe-db-instances --query 'DBInstances[*].DBInstanceIdentifier' --output text); do
  aws rds delete-db-instance --db-instance-identifier $db --skip-final-snapshot
done

echo "➡️ Deleting CloudWatch log groups..."
aws logs describe-log-groups --query 'logGroups[*].logGroupName' --output text | \
xargs -n1 aws logs delete-log-group --log-group-name

echo "✅ ALL AWS RESOURCES TERMINATED!"
