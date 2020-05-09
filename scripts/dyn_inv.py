#!/usr/bin/env python

import winrm
import argparse
import json
import string
import boto3


ssm = boto3.client('ssm')
ec2 = boto3.client('ec2')
workspaces = boto3.client('workspaces')
cloudformation = boto3.resource('cloudformation')


def find_public_ip_of_workspace():
    stack = cloudformation.Stack('WorkspaceBuilder')
    stack_resource = stack.Resource('workspace1').physical_resource_id
    workspace_private_ip = workspaces.describe_workspaces(WorkspaceIds=[stack_resource])['Workspaces'][0]['IpAddress']
    workspace_public_ip = ec2.describe_network_interfaces(Filters=[{ 'Name' : 'private-ip-address', 'Values' : [workspace_private_ip] }])['NetworkInterfaces'][0]['Association']['PublicIp']
    return workspace_public_ip


def find_id_of_workspace():
    stack = cloudformation.Stack('WorkspaceBuilder')
    stack_resource = stack.Resource('workspace1').physical_resource_id
    return stack_resource


def update_workspace_running_mode():
    workspace_id = find_id_of_workspace()
    workspaces.modify_workspace_properties(
        WorkspaceId=workspace_id,
        WorkspaceProperties={
            'RunningMode': 'AUTO_STOP',
            'RunningModeAutoStopTimeoutInMinutes': 60
        }
    )


def output_list_inventory(json_output):
    '''
    Output the --list data structure as JSON
    '''
    print(json.dumps(json_output))


def find_host(search_host, inventory):
    '''
    Find the given variables for the given host and output them as JSON
    '''
    host_attribs = inventory.get(search_host, {})
    print(json.dumps(host_attribs))


def ansible_local_init(ansible_inv):
    '''
    Initialize a Ansible 'local'
    '''
    ansible_inv['local'] = {}
    ansible_inv['local']['hosts'] = ['localhost']
    ansible_inv['local']['vars'] = {'ansible_connection': 'local'}


def ansible_group_init(ansible_inv, group_name):
    '''
    Initialize a new Ansible inventory group
    '''
    ansible_inv[group_name] = {}
    ansible_inv[group_name]['hosts'] = []
    ansible_inv[group_name]['vars'] = {
            "ansible_user": "ansible",
            "ansible_password": "",
            "ansible_connection": "winrm",
            "ansible_winrm_server_cert_validation": "ignore",
        }


def main():
    '''
    Ansible dynamic inventory experimentation
    Output dynamic inventory as JSON from statically defined data structures
    '''

    # Argument parsing
    parser = argparse.ArgumentParser(description="Ansible dynamic inventory")
    parser.add_argument("--list", help="Ansible inventory of all of the groups",
                        action="store_true", dest="list_inventory")
    parser.add_argument("--host", help="Ansible inventory of a particular host", action="store",
                        dest="ansible_host", type=str)
    parser.add_argument("--ip", help="Ansible IP of a particular host", action="store",
                        dest="ansible_ip", type=str)

    cli_args = parser.parse_args()
    list_inventory = cli_args.list_inventory
    ansible_host = cli_args.ansible_host
    ansible_ip = cli_args.ansible_ip

    ansible_inv = {}
    host_vars = {}
    ansible_local_init(ansible_inv)
    ansible_group_init(ansible_inv, 'win')

    workspaces_ip = find_public_ip_of_workspace()
    workspaces_password = ssm.get_parameter(Name='ansible-winrm-password', WithDecryption=True)['Parameter']['Value']

    ansible_inv['win']['hosts'].append(workspaces_ip)
    ansible_inv['win']['vars']['ansible_password'] = workspaces_password

    if list_inventory:
        output_list_inventory(ansible_inv)

    if ansible_host:
        find_host(ansible_host, host_vars)

    if ansible_ip:
        print(ansible_inv[ansible_ip]['hosts'][0])


if __name__ == "__main__":
    main()
