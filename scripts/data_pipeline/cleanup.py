import boto3
from datetime import datetime, timedelta
from pathlib import Path

def backup_to_s3(local_path: str, bucket: str):
    s3 = boto3.client('s3')
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    for file in Path(local_path).glob("*.parquet"):
        s3_key = f"backups/{date_str}/{file.name}"
        s3.upload_file(str(file), bucket, s3_key)
        print(f"Uploaded {file.name} to S3")

def delete_old_files(path: str, days: int = 7):
    cutoff = datetime.now() - timedelta(days=days)
    
    for file in Path(path).glob("*"):
        if file.stat().st_mtime < cutoff.timestamp():
            file.unlink()
            print(f"Deleted {file.name}")