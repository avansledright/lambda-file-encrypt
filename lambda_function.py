import boto3
from botocore.exceptions import ClientError
from cryptography.fernet import Fernet

def upload_file(file_name, bucket, object_name=None):
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, 'encrypted' + object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

def lambda_handler(event, context):
    print(event)
    print("Object has been uploaded")
    bucket_name = "adventasparagus"
    for record in event['Records']:
        object_key = record['s3']['object']['key']
    client = boto3.client('s3', region_name='us-west-2')
    print("Getting object")
    try:
        response = client.download_file(
            bucket_name, object_key, '/tmp/' + object_key[14:]
        )
        encryption_key = Fernet.generate_key()
        fernet = Fernet(encryption_key)
        with open('/tmp/' + object_key[14:], 'rb') as file:
            original = file.read()
            file.close()
        encrypted_file = fernet.encrypt(original)
        with open('/tmp/encrypted_' + object_key[14:], "wb") as enc_file:
            enc_file.write(encrypted_file)
            enc_file.close()
        print("Finished encrypting file")
        if upload_file('/tmp/encrypted_' + object_key[14:], bucket_name, object_key[14:]) == True:
            print("Successfully uploaded encrypted file")
            return True
        else:
            print("Failed to upload")
            return False

    except ClientError as e:
        print("failed to get object")
        print(e)
        return False