import os
import fitz  # PyMuPDF
import requests
from msal import ConfidentialClientApplication
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from urllib.parse import urlparse
import argparse

# --- Configuration (Replace with your actual values) ---
# Azure Document Intelligence setup
DI_ENDPOINT = 'https://<your-resource-name>.cognitiveservices.azure.com/'
DI_KEY = 'YOUR-KEY' 
CLASSIFIER_ID = 'TRAINED-CLASSIFICATION-MODEL-NAME' 

# SharePoint details
SITE_URL = 'https://<site-url>.sharepoint.com'  # Replace with your site URL
SITE_RELATIVE_PATH = '/sites/Automation/Prime'  # Replace with your site relative path
DOCUMENT_LIBRARY = 'Files'  # Adjust if your library name differs
PASSPORT_FOLDER = '/Passport'
LICENSE_FOLDER = '/License'

# Azure AD app details for SharePoint authentication
CLIENT_ID = 'YOUR-CLIENT-ID'  # Replace with your Azure AD app client ID 
CLIENT_SECRET = 'YOUR-CLIENT-SECRET'  # Replace with your Azure AD app client secret 
TENANT_ID = 'YOUR-TENANT-ID'  # Replace with your Azure AD tenant ID 

# --- Functions ---

def classify_pdf(pdf_bytes):
    """Classify the PDF using Azure Document Intelligence."""
    di_client = DocumentIntelligenceClient(endpoint=DI_ENDPOINT, credential=AzureKeyCredential(DI_KEY))
    poller = di_client.begin_classify_document(
        classifier_id=CLASSIFIER_ID,
        body=pdf_bytes,
        split="auto"
    )
    result = poller.result()
    doc_count = len(result.documents) if result.documents is not None else 0
    print(f"Classification complete. Found {doc_count} documents.")
    return result

def split_pdf(pdf_bytes, classification_result):
    """Split the PDF based on classification results."""
    if classification_result.documents is None:
        print("No documents found in classification result.")
        return []
    
    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
    split_pdfs = []
    seen_pages = set()
    for doc in classification_result.documents:
        doc_type = doc.doc_type.lower()
        if doc_type not in ['passport', 'license']:
            print(f"Skipping unrecognized doc_type: {doc_type}")
            continue
        for region in doc.bounding_regions:
            page_index = region.page_number - 1
            if page_index in seen_pages:
                print(f"Page {page_index + 1} already processed, skipping.")
                continue
            pdf_writer = fitz.open()
            pdf_writer.insert_pdf(pdf_document, from_page=page_index, to_page=page_index)
            split_pdf_bytes = pdf_writer.tobytes()
            pdf_writer.close()
            split_pdfs.append((split_pdf_bytes, doc_type))
            seen_pages.add(page_index)
            print(f"Split page {page_index + 1} as {doc_type}")
    pdf_document.close()
    return split_pdfs

def get_access_token():
    """Acquire access token for Microsoft Graph API."""
    authority = f'https://login.microsoftonline.com/{TENANT_ID}'
    app = ConfidentialClientApplication(CLIENT_ID, authority=authority, client_credential=CLIENT_SECRET)
    token_response = app.acquire_token_for_client(scopes=['https://graph.microsoft.com/.default'])
    if 'access_token' not in token_response:
        raise Exception(f"Failed to get access token: {token_response.get('error_description')}")
    return token_response['access_token']

def get_site_id(access_token):
    """Get the site ID for the SharePoint site."""
    parsed_url = urlparse(SITE_URL)
    tenant = parsed_url.netloc
    # Extract the site path, removing the "Forms/AllItems.aspx" part
    site_path_parts = parsed_url.path.split('/')
    site_name = '/'.join(site_path_parts[1:-2]) if len(site_path_parts) > 3 else ''
    if site_name.startswith('/'):
        site_name = site_name[1:]  # Remove leading slash

    graph_url = f'https://graph.microsoft.com/v1.0/sites/{tenant}:/{site_name}'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(graph_url, headers=headers)
    if response.status_code == 200:
        site_data = response.json()
        return site_data['id']
    else:
        raise Exception(f"Failed to get site ID: {response.status_code} - {response.text}")

def upload_to_sharepoint(split_pdf_bytes, doc_type, output_filename):
    """Upload the split PDF to the appropriate SharePoint folder using Graph API."""
    folder_name = os.path.join(DOCUMENT_LIBRARY, PASSPORT_FOLDER if doc_type == 'passport' else LICENSE_FOLDER)
    # Ensure folder names are correctly formatted for Graph API
    folder_name = folder_name.replace('\\', '/')
    if folder_name.startswith('/'):
        folder_name = folder_name[1:]

    access_token = get_access_token()
    site_id = get_site_id(access_token)

    # Ensure the folder exists before attempting to upload
    list_items_url = f'https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{folder_name}'
    headers = {'Authorization': f'Bearer {access_token}'}
    folder_check_response = requests.get(list_items_url, headers=headers)
    if folder_check_response.status_code == 404:
        print(f"Warning: Folder '{folder_name}' not found. Attempting to create...")
        create_folder_url = f'https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{DOCUMENT_LIBRARY}:/children'
        target_folder_name = PASSPORT_FOLDER if doc_type == 'passport' else LICENSE_FOLDER
        create_folder_payload = {
            "name": target_folder_name,
            "folder": {},
            "@microsoft.graph.conflictBehavior": "rename"
        }
        create_folder_response = requests.post(create_folder_url, headers=headers, json=create_folder_payload)
        if create_folder_response.status_code in (200, 201):
            print(f"Successfully created folder '{target_folder_name}' in '{DOCUMENT_LIBRARY}'.")
        else:
            print(f"Error creating folder '{target_folder_name}' in '{DOCUMENT_LIBRARY}': {create_folder_response.status_code} - {create_folder_response.text}")
            return

    upload_url = f'https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{folder_name}/{output_filename}:/content'
    upload_headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/pdf'
    }
    response = requests.put(upload_url, headers=upload_headers, data=split_pdf_bytes)
    if response.status_code in (200, 201):
        print(f"Successfully uploaded {output_filename} to {folder_name}")
    else:
        print(f"Failed to upload {output_filename}: {response.status_code} - {response.text}")

def main():
    """Main function to process the PDF and upload split files to SharePoint."""
    parser = argparse.ArgumentParser(description="Classify and split PDF, then upload to SharePoint")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    args = parser.parse_args()
    pdf_path = args.pdf_path
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]

    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        return

    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()

    print("Starting PDF processing...")
    classification_result = classify_pdf(pdf_bytes)
    split_pdfs = split_pdf(pdf_bytes, classification_result)

    if not split_pdfs:
        print("No valid documents to upload after splitting.")
        return

    doc_type_counter = {}
    for split_pdf_bytes, doc_type in split_pdfs:
        doc_type_counter[doc_type] = doc_type_counter.get(doc_type, 0) + 1
        suffix = f"{doc_type}" if doc_type_counter[doc_type] == 1 else f"{doc_type}_{doc_type_counter[doc_type]}"
        output_filename = f"{base_name}_{suffix}.pdf"
        print(f"Preparing to upload {output_filename}...")
        upload_to_sharepoint(split_pdf_bytes, doc_type, output_filename)

    print("Processing complete.")

if __name__ == "__main__":
    main()
