import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

STORAGE_ACCOUNT_A = os.getenv("STORAGE_ACCOUNT_A")
STORAGE_ACCOUNT_B = os.getenv("STORAGE_ACCOUNT_B")
CONNECTION_STRING_A = os.getenv("CONNECTION_STRING_A", "").strip()
CONNECTION_STRING_B = os.getenv("CONNECTION_STRING_B", "").strip()
CONTAINER_NAME = os.getenv("CONTAINER_NAME", "container1")
SAS_TOKEN = os.getenv("SAS_TOKEN", "").strip()

if not CONNECTION_STRING_A:
    raise ValueError("ERROR: CONNECTION_STRING_A is missing or empty!")

if not CONNECTION_STRING_B:
    raise ValueError("ERROR: CONNECTION_STRING_B is missing or empty!")

if not SAS_TOKEN:
    raise ValueError("ERROR: SAS_TOKEN is missing or empty!")

blob_service_client_a = BlobServiceClient.from_connection_string(CONNECTION_STRING_A)
blob_service_client_b = BlobServiceClient.from_connection_string(CONNECTION_STRING_B)


if SAS_TOKEN:
    SAS_TOKEN = SAS_TOKEN.strip()
    if not SAS_TOKEN.startswith("?"):
        SAS_TOKEN = "?" + SAS_TOKEN


container_client_a = blob_service_client_a.get_container_client(CONTAINER_NAME)
container_client_b = blob_service_client_b.get_container_client(CONTAINER_NAME)

if not container_client_a.exists():
    try:
        container_client_a.create_container()
        print(f"Created container '{CONTAINER_NAME}' in Storage Account A.")
    except Exception as e:
        print(f"Failed to create container in Storage Account A: {e}")

if not container_client_b.exists():
    try:
        container_client_b.create_container()
        print(f"Created container '{CONTAINER_NAME}' in Storage Account B.")
    except Exception as e:
        print(f"Failed to create container in Storage Account B: {e}")

print("\nUploading 100 blobs to Storage Account A...")
for i in range(100):
    blob_name = f"blob-{i}.txt"
    blob_client_a = container_client_a.get_blob_client(blob_name)

    try:
        blob_properties = blob_client_a.get_blob_properties()
        print(f"Blob {blob_name} already exists, skipping upload.")
    except Exception:
        blob_client_a.upload_blob(f"Sample content for {blob_name}", overwrite=True)
        print(f"Uploaded: {blob_name}")

print("\nAll 100 blobs uploaded to Storage Account A!\n")

print("\nCopying blobs from Storage Account A to B...")
for blob in container_client_a.list_blobs():
    blob_client_a = blob_service_client_a.get_blob_client(CONTAINER_NAME, blob.name)
    blob_client_b = blob_service_client_b.get_blob_client(CONTAINER_NAME, blob.name)

    source_blob_url = f"{blob_client_a.url}{SAS_TOKEN}"

    print(f"Copying from: {source_blob_url}")

    try:
        blob_client_b.start_copy_from_url(source_blob_url)
        print(f"Copied {blob.name} to Storage Account B.")
    except Exception as e:
        print(f"Failed to copy {blob.name}: {e}")