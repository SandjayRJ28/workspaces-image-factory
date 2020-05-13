import json
import argparse
import uuid
import os
import boto3
from os import environ as env



def update_product_template(bucket, key, bundle_id):
    s3 = boto3.resource('s3')
    tmp_file = '/tmp/' + str(uuid.uuid4())
    s3.meta.client.download_file(bucket, key, tmp_file)
    
    with open(tmp_file) as json_file:
        data = json.load(json_file)

    data['Resources']['MyWorkSpace']['Properties']['BundleId'] = bundle_id
    with open('/tmp/updated_template.json', 'w') as outfile:
        json.dump(data, outfile)

    s3key = 'sc-templates/workspaces/trader/' + str(uuid.uuid4()) + '.yaml'
    s3.meta.client.upload_file('/tmp/updated_template.json', bucket, s3key)
    return s3key


def create_provisioning_artifact(product_id, s3objectkey):
    """
    
    :param objProduct: Product object for which the provisioning artifact (version of the product) will be created. has all the mandatory details for product.
    :param productid: Product ID
    :param s3objectkey: S3Object Key, which has the cloudformation template for the product
    :return: None
    """
    client = boto3.client('servicecatalog')
    response = client.create_provisioning_artifact(
        ProductId=product_id,
        Parameters={
            'Name': str(uuid.uuid4()),
            'Description': str(datetime.datetime.now()),
            'Info': {
                'LoadTemplateFromURL': 'https://s3.amazonaws.com/' + s3objectkey
            },
            'Type': 'CLOUD_FORMATION_TEMPLATE'
        },
        IdempotencyToken=str(uuid.uuid4())
    )


def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description="Publish to Service Catalog")
    parser.add_argument("--bundleid", help="Workspaces BundleID",
                        action="store", dest="bundle_id", type=str)
    parser.add_argument("--bucket", help="Bucket containing Service Catalog templates", action="store",
                        dest="bucket", type=str)

    cli_args = parser.parse_args()
    bucket = cli_args.bucket
    product_id = env['PRODUCT_ID']
    key = 'workspaces/sc-workspaces-ra.json'

    try:
        s3key = update_product_template(bucket, key, bundle_id)
        create_provisioning_artifact(
            product_id, bucket + "/" + s3key)
    except Exception as e:
        raise


if __name__ == "__main__":
    main()
