import os
import shutil
import uuid
from pathlib import Path

try:
    from google.cloud import storage  # type: ignore
except Exception:
    storage = None

# Construct absolute path to the key file if it was copied over (works locally & in Docker)
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../../../"))
key_path = os.path.join(root_dir, "gleaming-entry-471909-s1-5c03f3ad584a.json")

bucket_name = os.getenv("CITYSCALE_GCS_BUCKET", "cityscale-bucket")
_client = None

def _get_client():
    global _client
    if _client is not None:
        return _client
    if storage is None:
        return None
    try:
        # Try to use the explicit service account file if it exists,
        # otherwise fallback to Application Default Credentials.
        if os.path.exists(key_path):
            _client = storage.Client.from_service_account_json(key_path)
        else:
            _client = storage.Client(project="gleaming-entry-471909-s1")
        return _client
    except Exception:
        return None

def _upload_local(file_obj, filename: str) -> str:
    uploads_dir = Path(root_dir) / "data" / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)

    safe_name = Path(filename).name
    target = uploads_dir / f"{uuid.uuid4().hex}_{safe_name}"

    # file_obj is a SpooledTemporaryFile; copy its current contents to disk
    with open(target, "wb") as out:
        try:
            file_obj.seek(0)
        except Exception:
            pass
        shutil.copyfileobj(file_obj, out)
    return str(target)

def upload_file(file, filename):
    storage_mode = os.getenv("CITYSCALE_STORAGE", "").strip().lower()
    if storage_mode in {"local", "disk", "filesystem"}:
        return _upload_local(file, filename)

    # If the runtime can't read gs:// paths (missing fsspec/gcsfs), keep uploads local
    try:
        import fsspec  # noqa: F401
    except Exception:
        return _upload_local(file, filename)

    client = _get_client()
    if client is None:
        return _upload_local(file, filename)

    try:
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(filename)
        blob.upload_from_file(file)
        return f"gs://{bucket_name}/{filename}"
    except Exception:
        # If GCS fails locally (missing creds / bucket perms), fallback to disk.
        return _upload_local(file, filename)