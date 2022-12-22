import boto3
import string
import json


def find_id_of_workspace():
    cloudformation = boto3.resource('cloudformation')
    stack = cloudformation.Stack('WorkspaceBuilder')
    stack_resource = stack.Resource('workspace2').physical_resource_id
    return stack_resource


def update_workspace_running_mode():
    workspaces = boto3.client('workspaces')
    workspace_id = find_id_of_workspace()
    workspaces.modify_workspace_properties(
        WorkspaceId=workspace_id,
        WorkspaceProperties={
            'RunningMode': 'AUTO_STOP',
            'RunningModeAutoStopTimeoutInMinutes': 60
        }
    )

def main():
    update_workspace_running_mode()


if __name__ == "__main__":
    main()
