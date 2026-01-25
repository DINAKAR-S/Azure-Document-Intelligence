# Azure Document Intelligence – AI-Based PDF Classification & Splitting System

This repository demonstrates a **real-world AI document processing system** built using **Azure Document Intelligence**, designed to automatically:

- Classify multi-document PDFs
- Split them into individual files
- Upload each document to the correct SharePoint folder

The solution replicates a **production-grade back-office automation workflow** used in enterprise document pipelines.

---

## 🚀 What This Project Does

Given a single multi-page PDF containing different document types (e.g. passport + license):

1. Classifies each page using a trained Azure classifier
2. Identifies document type per page
3. Splits the PDF accordingly
4. Uploads each document to SharePoint
5. Organizes files into business folders automatically

---

## 🧠 Use Cases

This system is ideal for:

- KYC automation
- Identity verification systems
- Loan onboarding workflows
- Back-office document segregation
- Insurance & banking operations
- Compliance document routing

---

## 📂 Project Structure

```

Azure-Document-Intelligence/
│
├── azure_doc_intelligence.py
│   → Simple local PDF classification demo
│
├── classify_split_pdf_using_azure_doc_intelligence.py
│   → Full enterprise pipeline with:
│      - Classification
│      - Splitting
│      - SharePoint upload
│
└── README.md (this file)

```

---

## ⚙️ Technology Stack

- Azure Document Intelligence
- Azure Custom Classifier
- Python 3.10+
- PyMuPDF (PDF splitting)
- Microsoft Graph API
- Azure AD (MSAL authentication)
- SharePoint Online
- REST APIs

---

## 🔑 Key Features

- AI-powered document classification  
- Automatic PDF splitting  
- Multi-document handling  
- Zero manual sorting  
- Microsoft Graph integration  
- SharePoint upload automation  
- Enterprise authentication  
- Modular processing pipeline  

---

## 🧩 System Architecture

```

PDF Input
↓
Azure Document Intelligence
↓
AI Classification Model
↓
Page-level Document Detection
↓
PDF Split Engine
↓
Microsoft Graph API
↓
SharePoint Document Library

````

---

## 🔐 Security Design

- Azure AD app authentication
- No hardcoded credentials in production
- Token-based Microsoft Graph access
- OAuth2 client credentials flow
- Sample keys only in repository

---

## ▶️ How to Run

### 1. Install dependencies
```bash
pip install azure-ai-documentintelligence pymupdf msal requests
````

### 2. Configure environment

Edit:

```python
DI_ENDPOINT
DI_KEY
CLASSIFIER_ID
CLIENT_ID
CLIENT_SECRET
TENANT_ID
SITE_URL
```

### 3. Execute

```bash
python classify_split_pdf_using_azure_doc_intelligence.py input.pdf
```

---

## 📈 Why This Project Is Valuable

This is not a tutorial demo.

It demonstrates:

* Production-style AI pipelines
* Real enterprise authentication
* Business document automation
* End-to-end system design
* Cloud-native AI integration

The same architecture is used in:

* Banks
* FinTech platforms
* Insurance companies
* Legal tech systems
* Government document processing

---

## 🧪 Sample Output

Input:

```
combined_kyc.pdf
```

Output:

```
combined_kyc_passport.pdf → SharePoint/Passport  
combined_kyc_license.pdf  → SharePoint/License  
```

---

## 👤 Author

**Dinakar S**
AI Engineer | Automation Engineer | Cybersecurity

---
This is exactly how **senior engineers document real systems**.
