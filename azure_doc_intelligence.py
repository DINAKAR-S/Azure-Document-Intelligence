from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

# -------- CONFIG --------
DI_ENDPOINT = "https://<your-resource-name>.cognitiveservices.azure.com/"
DI_KEY = "YOUR-KEY"
CLASSIFIER_ID = "YOUR-CLASSIFIER-ID"
PDF_PATH = "sample.pdf"
# ------------------------

def classify_local_pdf():
    client = DocumentIntelligenceClient(
        endpoint=DI_ENDPOINT,
        credential=AzureKeyCredential(DI_KEY)
    )

    with open(PDF_PATH, "rb") as f:
        poller = client.begin_classify_document(
            classifier_id=CLASSIFIER_ID,
            body=f
        )

    result = poller.result()

    print("\n=== CLASSIFICATION RESULT ===")
    for i, doc in enumerate(result.documents):
        print(f"\nDocument {i+1}")
        print("Type:", doc.doc_type)
        print("Confidence:", doc.confidence)

        for region in doc.bounding_regions:
            print("Page:", region.page_number)

if __name__ == "__main__":
    classify_local_pdf()
