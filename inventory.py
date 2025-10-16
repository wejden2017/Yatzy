inventory/aws_ec2_inventory.py

#!/usr/bin/env python3

import boto3
import json
import os
import sys

def get_ec2_instances(tag_key, tag_value, region):
    """Récupère les instances EC2 avec un tag spécifique"""
    ec2 = boto3.client('ec2', region_name=region)
    response = ec2.describe_instances(
        Filters=[
            {'Name': f'tag:{tag_key}', 'Values': [tag_value]},
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )
    
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            public_dns_tag = next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'PublicDnsName'), None)
            instances.append({
                'private_ip': instance['PrivateIpAddress'],
                'instance_id': instance['InstanceId'],
                'PublicDnsName': public_dns_tag
            })
    
    return instances

def generate_inventory(env, region):
    """Génère l'inventaire Ansible dynamique"""
    
    inventory = {
        '_meta': {'hostvars': {}},
        'all': {'children': ['oracle_servers']},
        'oracle_servers': {'hosts': []}
    }
    
    print(f"🔍 Searching EC2 with tag Role=CATS-DATABASE in {region}...", file=sys.stderr)
    oracle_instances = get_ec2_instances(tag_key='Role', tag_value='CATS-DATABASE', region=region)
    
    if not oracle_instances:
        print(f"⚠️ WARNING: No running EC2 instances found", file=sys.stderr)
        return inventory
    
    print(f"✓ Found {len(oracle_instances)} instance(s)", file=sys.stderr)
    
    for instance in oracle_instances:
        host_ip = instance['private_ip']
        inventory['oracle_servers']['hosts'].append(host_ip)
        inventory['_meta']['hostvars'][host_ip] = {
            'ansible_user': 'ec2-user',
            'ansible_ssh_private_key_file': '{{ ansible_ssh_private_key_file }}',
            'ansible_python_interpreter': '/usr/bin/python3',
            'instance_id': instance['instance_id'],
            'public_dns_name': instance.get('PublicDnsName', 'N/A'),
            'private_ip': host_ip
        }
    
    return inventory

if __name__ == '__main__':
    if '--list' in sys.argv or len(sys.argv) == 1:
        env = os.environ.get('ENV', 'dev')
        region = os.environ.get('AWS_REGION', 'eu-west-2')
        
        try:
            inventory = generate_inventory(env, region)
            print(json.dumps(inventory, indent=2))
        except Exception as e:
            print(f"❌ ERROR: {str(e)}", file=sys.stderr)
            print(json.dumps({'_meta': {'hostvars': {}}}))
            sys.exit(1)
    
    elif '--host' in sys.argv:
        print(json.dumps({}))
    
    else:
        env = sys.argv[1] if len(sys.argv) > 1 else 'dev'
        region = sys.argv[2] if len(sys.argv) > 2 else 'eu-west-2'
        
        try:
            inventory = generate_inventory(env, region)
            print(json.dumps(inventory, indent=2))
        except Exception as e:
            print(f"❌ ERROR: {str(e)}", file=sys.stderr)
            sys.exit(1)
