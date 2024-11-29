# app/cloud_function/main.py

from google.cloud import run_v2
import os

def trigger_processing(event, context):
    """TRIGGERED BY A CHANGE TO A GOOGLE DRIVE FILE"""
    file = event
    
    # get file information
    file_id = file.get('id')
    file_name = file.get('name')
    file_path = f"gs://{file['bucket']}/{file_name}"
    
    # create cloud run job client
    client = run_v2.JobsClient()
    
    # configure job
    job = run_v2.Job(
        template=run_v2.ExecutionTemplate(
            containers=[{
                "image": f"gcr.io/{os.getenv('PROJECT_ID')}/document-indexer",
                "env": [
                    {"name": "FILE_ID", "value": file_id},
                    {"name": "FILE_PATH", "value": file_path}
                ]
            }],
            max_retries=3,  # retry failed jobs
            timeout_seconds=600  # 10 minute timeout
        )
    )
    
    # execute job
    operation = client.create_job(
        parent=f"projects/{os.getenv('PROJECT_ID')}/locations/{os.getenv('REGION')}",
        job=job
    )
    
    return operation.result()