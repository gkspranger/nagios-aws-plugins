#!/usr/bin/env python
#

import argparse
import boto3
import datetime
import sys

parser=argparse.ArgumentParser(
	description='Check the maximum surge queue length of an ELB in AWS.')
parser.add_argument(
	'-n',
	metavar='NAME',
	required=True,
	action='store',
	help='Name of the ELB to check',
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
	Namespace='AWS/ELB',
	MetricName='SurgeQueueLength',
    Dimensions=[
		{
			'Name': 'LoadBalancerName',
			'Value': "%s" % args.name
        }
	],
	StartTime=datetime.datetime.utcnow()-datetime.timedelta(minutes=args.minutes),
    EndTime=datetime.datetime.utcnow(),
    Period=args.minutes*60,
    Statistics=[
		'Maximum'
	],
	Unit='Count'
)

if len(response['Datapoints']) > 0:
	max=response['Datapoints'][0]['Maximum']
else:
	max=0
state='UNKNOWN'
status=3

if max >= args.critical:
	state='CRITICAL'
	status=2
elif max >= args.warning:
	state='WARNING'
	status=1
elif max < args.warning:
	state='OK'
	status=0

print "{0} - {1} is the maximum surge queue length for AWS ELB {2} | max={1};".format(
	state,
	max,
	args.name)
sys.exit(status)
