#!/usr/bin/env python
#

import argparse
import boto3
import datetime
import sys

parser=argparse.ArgumentParser(
	description='Check the status of all EBS volumes attached to an EC2 instance in AWS.')
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
response=client.describe_volumes(
	Filters=[
		{
			'Name': 'attachment.instance-id',
			'Values': [
				args.instance_id
			]
		}
	],
    DryRun=False
)

# dict that contains key=id and name/status as attrs
statuses={}
# list containing all vol ids for easy use
vols=[]
for i in response['Volumes']:
	id=i['Attachments'][0]['VolumeId']
	try:
		name=i['Tags'][0]['Value']
	except:
		name='NA'
	statuses[id]={
		'name': name
	}
	vols.append(id)

response=client.describe_volume_status(
	VolumeIds=vols,
	DryRun=False
)

non_ok=0
for i in response['VolumeStatuses']:
	id=i['VolumeId']
	status=i['VolumeStatus']['Status']
	if status != 'ok' and status != 'insufficient-data':
		non_ok+=1
	statuses[id]['status']=status

status = 0
state = 'OK'

if non_ok > 0:
	state='WARNING'
	status=1

print "{0} - {1} EBS volumes, attached to {2} in {3}, are in a non-OK state: {4} | non_ok={1};".format(
	state,
	non_ok,
	args.instance_id,
	args.region,
	str(statuses))
sys.exit(status)
