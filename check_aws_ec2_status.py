#!/usr/bin/env python
#

import argparse
import boto3
import datetime
import sys

parser=argparse.ArgumentParser(
	description='Check the status of an EC2 instance in AWS.')
parser.add_argument(
	'-d',
	metavar='INSTANCE-ID',
	required=True,
	action='store',
	help='Instance ID of the EC2 to check',
	dest='instance_id',
	type=str)
parser.add_argument(
	'-r',
	metavar='AWS_REGION',
	required=True,
	action='store',
	help='AWS region',
	dest='region',
	type=str)
parser.add_argument(
	'-i',
	metavar='AWS_ACCESS_KEY_ID',
	required=True,
	action='store',
	help='AWS access key id',
	dest='id',
	type=str)
parser.add_argument(
	'-k',
	metavar='AWS_SECRET_ACCESS_KEY',
	required=True,
	action='store',
	help='AWS secret access key',
	dest='key',
	type=str)

args=parser.parse_args()

client=boto3.client(
	'ec2',
	aws_access_key_id=args.id,
	aws_secret_access_key=args.key,
    region_name=args.region
)
response=client.describe_instance_status(
	InstanceIds=[
		args.instance_id,
	],
    DryRun=False,
    IncludeAllInstances=True
)

details=response['InstanceStatuses'][0]
system=details['SystemStatus']['Status']
instance=details['InstanceStatus']['Status']

system_perf = 0 if system == "ok" else 1
instance_perf = 0 if instance == "ok" else 1
status = system_perf + instance_perf
state = 'OK'

if status >= 2:
	state='CRITICAL'
elif status >= 1:
	state='WARNING'

print "{0} - system status = {1} .. instance status = {2} | system_status={3}; instance_status={4};".format(
	state,
	system,
	instance,
	system_perf,
	instance_perf)
sys.exit(status)
