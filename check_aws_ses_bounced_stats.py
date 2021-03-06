#!/usr/bin/env python
#

import argparse
import boto3
import datetime
import operator
import sys

parser=argparse.ArgumentParser(
	description='Check the total bounced emails for SES in AWS')
parser.add_argument(
	'-H',
	metavar='HOURS',
	required=True,
	action='store',
	help='Number of hours to look back',
	dest='hours',
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
	'ses',
	aws_access_key_id=args.id,
	aws_secret_access_key=args.key,
    region_name=args.region
)
response=client.get_send_statistics()
sent=sorted(response['SendDataPoints'], key=operator.itemgetter('Timestamp'), reverse=True)
bounced=0

for i in sent[:4]:
	bounced=bounced+i['Bounces']

state='UNKNOWN'
status=3

if bounced >= args.critical:
	state='CRITICAL'
	status=2
elif bounced >= args.warning:
	state='WARNING'
	status=1
elif bounced < args.warning:
	state='OK'
	status=0

print "{0} - {1} is the total bounced emails in the past {2} hour(s) for SES in AWS {3} | bounced={1};{4};{5}".format(
	state,
	bounced,
	args.hours,
	args.region,
	args.warning,
	args.critical)
sys.exit(status)
