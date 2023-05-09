import io
from typing import List, Optional, Final

import boto3
from botocore.exceptions import ClientError


class S3StorageProxy():
    const_presigned_link_expatration_seconds: Final[int] = 60 * 60 * 24

    @property
    def expatration_seconds(self):
        return type(self).const_presigned_link_expatration_seconds


    # Return a boto3 client object for buckets
    @staticmethod
    def get_s3_client(endpoint, key_id, application_key):
        s3_client = boto3.client(
            service_name='s3',
            endpoint_url=endpoint,
            aws_access_key_id=key_id,
            aws_secret_access_key=application_key,
        )
        return s3_client


    # Return a boto3 resource object for bucket
    @staticmethod
    def get_s3_resource(endpoint, key_id, application_key):
        s3 = boto3.resource(
            service_name='s3',
            endpoint_url=endpoint,
            aws_access_key_id=key_id,
            aws_secret_access_key=application_key,
        )
        return s3


    def __init__(self, endpoint: str, key_id: str, application_key: str, default_bucket_name: str):
        self.endpoint               = endpoint
        self.key_id                 = key_id
        self.application_key        = application_key
        self.default_bucket_name    = default_bucket_name
        self.s3_client = S3StorageProxy.get_s3_client(endpoint, key_id, application_key)
        self.s3_resource = S3StorageProxy.get_s3_resource(endpoint, key_id, application_key)


    def set_default_bucket(self, new_bucket_name: str):
        self.default_bucket_name = new_bucket_name


    def list_object_keys_by_filter(self, bucket: Optional[str] = None, prefix: str = '/', endwith: Optional[str] = None):
        if bucket is None:
            bucket = self.default_bucket_name

        result = []
        for object_summary in self.s3_resource.Bucket(bucket).objects.filter(Prefix=prefix):
            if  object_summary.key != prefix:
                if endwith is not None:
                    if object_summary.key.endswith(endwith):
                        result.append(object_summary.key)
                else:
                    result.append(object_summary.key)

        return result


    # List the keys of the objects in the specified bucket
    def list_object_keys(self, bucket: Optional[str] = None):
        '''
        for public backet
        '''
        if bucket is None:
            bucket = self.default_bucket_name

        try:
            response = self.s3_resource.Bucket(bucket).objects.all()

            return_list = []               # create empty list
            for object in response:        # iterate over response
                return_list.append(object.key) # for each item in response append object.key to list
            return return_list             # return list of keys from response

        except ClientError as ce:
            # TODO: create logger
            print('error', ce)


    # List the buckets in account in the specified region
    def list_buckets(self, raw_object: bool = False):
        '''
        client method
        for public backet
        '''
        try:
            my_buckets_response = self.s3_client.list_buckets()

            print('\nBUCKETS')
            for bucket_object in my_buckets_response[ 'Buckets' ]:
                print(bucket_object[ 'Name' ])

            if raw_object:
                print('\nFULL RAW RESPONSE:')
                print(my_buckets_response)

        except ClientError as ce:
            print('error', ce)


    # List browsable URLs of the objects in the specified bucket - Useful for *PUBLIC* buckets
    def list_objects_browsable_url(self, bucket: Optional[str] = None):
        '''
        for public backet
        '''
        if bucket is None:
            bucket = self.default_bucket_name

        try:
            bucket_object_keys = self.list_object_keys(bucket)

            return_list = []                # create empty list
            for key in bucket_object_keys:  # iterate bucket_objects
                url = "%s/%s/%s" % (self.endpoint, bucket, key) # format and concatenate strings as valid url
                return_list.append(url)     # for each item in bucket_objects append value of 'url' to list
            return return_list              # return list of keys from response

        except ClientError as ce:
            print('error', ce)


    # Return presigned URL of the object in the specified bucket - Useful for *PRIVATE* buckets
    def get_object_presigned_url(self, key: str, bucket: Optional[str] = None, expiration_seconds: int = const_presigned_link_expatration_seconds):
        """
        my_bucket_object.key == filename in bucket

        my_bucket = s3_private.Bucket(PRIVATE_BUCKET_NAME)
        print('my_bucket: ', my_bucket)
        for my_bucket_object in my_bucket.objects.all():
            file_url = get_object_presigned_url(PRIVATE_BUCKET_NAME, my_bucket_object.key, 3000, s3_private)
            print (file_url)
        """
        if bucket is None:
            bucket = self.default_bucket_name

        try:
            response = self.s3_resource.meta.client.generate_presigned_url(
                ClientMethod='get_object',
                ExpiresIn=expiration_seconds,
                Params={
                    'Bucket': bucket,
                    'Key': key
                    }
            )
            return response

        except ClientError as ce:
            print('error', ce)


    # Download the specified object from s3 and write to local file system
    def download_file_binary(self,
            key_name: str,
            bucket: Optional[str] = None,
        ) -> Optional[bytes]:
        '''
        download_file(
            bucket = PRIVATE_BUCKET_NAME,
            directory = LOCAL_DIR,
            local_name = filename,
            key_name = filename,
            s3 = s3_private
        )
        '''
        if bucket is None:
            bucket = self.default_bucket_name

        try:
            buf = io.BytesIO()
            self.s3_resource.Bucket(bucket).download_fileobj(key_name, buf)
            # Get file content as bytes
            filecontent_bytes = buf.getvalue()
            return filecontent_bytes
        except ClientError as ce:
            print('error', ce)
            return None


    # Download the specified object from s3 and write to local file system
    def download_file(self,
            key_name: str,
            directory: Optional[str] = None,
            local_name: Optional[str] = None,
            local_path: Optional[str] = None,
            bucket: Optional[str] = None,
        ):
        '''
        download_file(
            bucket = PRIVATE_BUCKET_NAME,
            directory = LOCAL_DIR,
            local_name = filename,
            key_name = filename,
            s3 = s3_private
        )
        '''
        if bucket is None:
            bucket = self.default_bucket_name

        if local_path is not None:
            file_path = local_path
        else:
            file_path = directory + '/' + local_name

        try:
            self.s3_resource.Bucket(bucket).download_file(key_name, file_path)
        except ClientError as ce:
            print('error', ce)


    # Upload specified file into the specified bucket
    def upload_file_binary(self, file: bytes, s3path: str, bucket: Optional[str] = None):
        '''
        response = upload_file(NEW_BUCKET_NAME, LOCAL_DIR, file1, s3)
        print('RESPONSE:  ', response)
        '''
        if bucket is None:
            bucket = self.default_bucket_name

        try:
            response = self.s3_resource.Object(bucket, s3path).put(Body=file)
        except ClientError as ce:
            print('error', ce)

        return response

    # Upload specified file into the specified bucket
    def upload_file(self, local_directory: str, file: str, s3path: Optional[str] = None, bucket: Optional[str] = None):
        '''
        response = upload_file(NEW_BUCKET_NAME, LOCAL_DIR, file1, s3)
        print('RESPONSE:  ', response)
        '''
        if bucket is None:
            bucket = self.default_bucket_name

        file_path = local_directory + '/' + file
        remote_path = s3path
        if remote_path is None:
            remote_path = file
        try:
            response = self.s3_resource.Bucket(bucket).upload_file(file_path, remote_path)
        except ClientError as ce:
            print('error', ce)

        return response


    # Copy the specified existing object in a s3 bucket, creating a new copy in a second s3 bucket
    def copy_file(self, source_bucket: str, destination_bucket: str, source_key: str, destination_key: str):
        '''
        copy_file(NEW_BUCKET_NAME, TRANSIENT_BUCKET_NAME, file1, file1)
        '''
        try:
            source = {
                'Bucket': source_bucket,
                'Key': source_key
            }
            self.s3_resource.Bucket(destination_bucket).copy(source, destination_key)
        except ClientError as ce:
            print('error', ce)


    # Delete the specified objects from s3
    def delete_files(self, keys: List[str], bucket: Optional[str] = None):
        '''
        delete_files(NEW_BUCKET_NAME, [file1], s3)
        '''
        if not isinstance(keys, List):
            keys = [keys]

        if bucket is None:
            bucket = self.default_bucket_name

        objects = []
        for key in keys:
            objects.append({'Key': key})
        try:
            self.s3_resource.Bucket(bucket).delete_objects(Delete={'Objects': objects})
        except ClientError as ce:
            print('error', ce)

    # Delete the specified object from s3 - all versions
    def delete_files_all_versions(self, keys: List[str], bucket: Optional[str] = None):
        '''
        delete_files_all_versions(
            [file1],
            BUCKET_NAME
        )
        '''
        if not isinstance(keys, List):
            keys = list(keys)

        if bucket is None:
            bucket = self.default_bucket_name

        objects = []
        for key in keys:
            objects.append({'Key': key})
        try:
            # SOURCE re LOGIC FOLLOWING:  https://stackoverflow.com/questions/46819590/delete-all-versions-of-an-object-in-s3-using-python
            paginator = self.s3_client.get_paginator('list_object_versions')
            response_iterator = paginator.paginate(Bucket=bucket)
            for response in response_iterator:
                versions = response.get('Versions', [])
                versions.extend(response.get('DeleteMarkers', []))
                for version_id in [x['VersionId'] for x in versions
                                if x['Key'] == key and x['VersionId'] != 'null']:
                    print('Deleting {} version {}'.format(key, version_id))
                    self.s3_client.delete_object(Bucket=bucket, Key=key, VersionId=version_id)

        except ClientError as ce:
            print('error', ce)


    # Delete the specified bucket from s3
    def delete_bucket(self, bucket: str, delete_default_check: bool = False):
        '''
        avoid delete default bucket or
            set delete_default_check == True
        '''
        if bucket == self.default_bucket_name and not delete_default_check:
            raise Exception(f"Cannot delete default bucket {self.default_bucket_name}")

        try:
            self.s3_resource.Bucket(bucket).delete()
        except ClientError as ce:
            print('error', ce)


def main():
    # TODO: remove private information 
    s3 = S3StorageProxy(endpoint='', key_id='', application_key='', default_bucket_name='style-bucket')

    s3.list_buckets(True)
    print(s3.list_object_keys_by_filter(prefix='torch_models/style_transfer/v1/', endwith="ic_20000.pth"))

    return



# Optional (not strictly required)
if __name__ == '__main__':
    main()


'''
'print('BEFORE CREATE NEW BUCKET NAMED:  ',NEW_BUCKET_NAME )
        list_buckets( s3_client )

        s3 = s3_rw

        response = s3.create_bucket( Bucket=NEW_BUCKET_NAME )

        print('RESPONSE:  ', response)

        print('\nAFTER CREATE BUCKET')
        list_buckets( s3_client )
'''