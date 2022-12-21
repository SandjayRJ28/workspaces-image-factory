import boto3

def main():
    cloudformation = boto3.client('cloudformation')
    response = cloudformation.delete_stack(StackName='WorkspaceBuilder', RetainResources=['workspace1'])


if __name__ == "__main__":
    main()
