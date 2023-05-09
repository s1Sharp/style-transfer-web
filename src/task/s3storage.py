from task.bucket_utils import S3StorageProxy

class S3StyleStorage():

    def __init__(self, endpoint: str, key_id: str, application_key: str, default_bucket_name: str = 'style-bucket'):
        self.s3_proxy = S3StorageProxy(endpoint, key_id, application_key, default_bucket_name)

    def put_src_file(self, file: bytes, filename: str):
        return self.s3_proxy.upload_file_binary(file, filename)

    def get_link_to_download(self):
        pass

