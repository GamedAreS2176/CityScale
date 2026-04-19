import os
from google.cloud import storage

# Construct absolute path to the key file if it was copied over (works locally & in Docker)
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../../../"))
key_path = os.path.join(root_dir, "gleaming-entry-471909-s1-5c03f3ad584a.json")

# Try to use the explicit service account file if it exists,
# otherwise fallback to Application Default Credentials (e.g. when hosted on Cloud Run directly)
if os.path.exists(key_path):
    client = storage.Client.from_service_account_json(key_path)
else:
    client = storage.Client(project="gleaming-entry-471909-s1")
bucket_name = "cityscale-bucket"

def upload_file(file, filename):
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(filename)
    blob.upload_from_file(file)
    return f"gs://{bucket_name}/{filename}"