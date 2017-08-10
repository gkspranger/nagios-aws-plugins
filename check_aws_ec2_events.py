#!/usr/bin/env python
#

import argparse
import boto3
import datetime
import sys

parser=argparse.ArgumentParser(
	description='Check the events of an EC2 instance in AWS.')
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

details = response['InstanceStatuses'][0]
events = 0 if 'Events' not in details else len(details['Events'])
status = 0
state = 'OK'

if events > 0:
	state='WARNING'
	status=1

print "{0} - {1} events found for {2} EC2 {3} | events={1};".format(
	state,
	events,
	args.region,
	args.instance_id)
sys.exit(status)
