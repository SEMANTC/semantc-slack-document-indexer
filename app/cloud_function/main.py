# app/cloud_function/main.py

from google.cloud import run_v2

def trigger_processing(event, context):
    """TRIGGERED BY A CHANGE TO A GOOGLE DRIVE FILE"""
    file = event
    
    # create cloud run job client
    client = run_v2.JobsClient()
    
    # get file metadata
    file_name = file['name']
    file_path = f"gs://{file['bucket']}/{file_name}"
    
    # execute cloud run job
    job = run_v2.Job(
        template=run_v2.ExecutionTemplate(
            containers=[{
                "image": f"gcr.io/{project_id}/document-indexer",
                "env": [
                    {"name": "FILE_PATH", "value": file_path}
                ]
            }]
        )
    )
    
    return client.create_job(job=job).result()