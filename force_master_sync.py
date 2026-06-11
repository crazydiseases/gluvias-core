from google.cloud import discoveryengine_v1beta as discoveryengine

project_id = "firm-legal-ai-497419"
location = "global"
data_store_id = "gluvias-final-vault"
gcs_uri = "gs://gluvias-vault-temp/*"

client = discoveryengine.DocumentServiceClient()

parent = client.branch_path(
    project=project_id,
    location=location,
    data_store=data_store_id,
    branch="default_branch",
)

request = discoveryengine.ImportDocumentsRequest(
    parent=parent,
    gcs_source=discoveryengine.GcsSource(
        input_uris=[gcs_uri],
        data_schema="content",
    ),
    reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL,
)

print(f"🔄 Forcing Vertex AI to ingest all master law books from {gcs_uri}...")
operation = client.import_documents(request=request)
print(f"📡 Sync operation triggered! Name: {operation.operation.name}")
print("The AI is now processing your master library in the background.")
