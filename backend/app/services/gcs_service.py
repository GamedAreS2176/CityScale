from google.cloud import storage

client = storage.Client(project="gleaming-entry-471909-s1")
bucket_name = "cityscale-bucket"

def upload_file(file, filename):
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(filename)
    blob.upload_from_file(file)
    return f"gs://{bucket_name}/{filename}"