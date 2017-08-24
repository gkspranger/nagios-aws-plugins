#!/usr/bin/env python
#

import argparse
import boto3
import datetime
import sys

parser=argparse.ArgumentParser(
	description='Check the minimum freeable memory (MB) of an RDS instance in AWS.')
parser.add_argument(
	'-n',
	metavar='NAME',
	required=True,
	action='store',
	help='Name of the RDS instance to check',
	dest='name',
	type=str)
parser.add_argument(
	'-m',
	metavar='MINUTES',
	required=True,
	action='store',
	help='Number of minutes to look back; Should coordinate with check interval',
	dest='minutes',
	type=int)
parser.add_argument(
	'-w',
	metavar='WARNING',
	required=True,
	action='store',
	help='Exit with WARNING status if greater than FLOAT',
	dest='warning',
	type=float)
parser.add_argument(
	'-c',
	metavar='CRITICAL',
	required=True,
	action='store',
	help='Exit with CRITICAL status if greater than FLOAT',
	dest='critical',
	type=float)
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
	'cloudwatch',
	aws_access_key_id=args.id,
	aws_secret_access_key=args.key,
    region_name=args.region
)
response=client.get_metric_statistics(
	Namespace='AWS/RDS',
	MetricName='FreeableMemory',
    Dimensions=[
		{
			'Name': 'DBInstanceIdentifier',
			'Value': "%s" % args.name
        }
	],
	StartTime=datetime.datetime.utcnow()-datetime.timedelta(minutes=args.minutes),
    EndTime=datetime.datetime.utcnow(),
    Period=args.minutes*60,
    Statistics=[
		'Minimum'
	],
	Unit='Bytes'
)

min=response['Datapoints'][0]['Minimum'] / 1048576
min=round(min, 2)

state='UNKNOWN'
status=3

if min <= args.critical:
	state='CRITICAL'
	status=2
elif min <= args.warning:
	state='WARNING'
	status=1
elif min > args.warning:
	state='OK'
	status=0

print "{0} - {1}MB is the minimum freeable memory for AWS RDS instance {2} | minimum={1};{3};{4}".format(
	state,
	min,
	args.name,
	args.warning,
	args.critical)
sys.exit(status)
