#!/usr/bin/env python
#

import argparse
import boto3
import datetime
import sys

parser=argparse.ArgumentParser(
	description='Check the state and telemetry of a VPN connection in AWS.')
parser.add_argument(
	'-d',
	metavar='VPN-ID',
	required=True,
	action='store',
	help='VPN ID of the VPN connection to check',
	dest='vpn_id',
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
response=client.describe_vpn_connections(
	VpnConnectionIds=[
		args.vpn_id
	],
    DryRun=False
)

details=response['VpnConnections'][0]
vpn_name=details['Tags'][0]['Value']
vpn_state=details['State']
vpn_telemetry=details['VgwTelemetry']

non_ups=0
status=0
state='OK'

for i in vpn_telemetry:
	if i['Status'] != "UP":
		non_ups += 1

if vpn_state != "available" or non_ups == len(vpn_telemetry):
	state='CRITICAL'
	status=2
elif non_ups > 0:
	state='WARNING'
	status=1

print "{0} - VPN name = {1} .. VPN state = {2} .. VPN telemetry non-up statuses = {3} | vpn_telemetry_non_ups={3};".format(
	state,
	vpn_name,
	vpn_state,
	non_ups)
sys.exit(status)
