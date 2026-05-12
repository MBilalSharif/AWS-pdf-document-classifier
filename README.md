# 📄 Serverless Document Classification System

An intelligent, event-driven document processing pipeline that automatically classifies PDF files and extracts structured metadata using AWS serverless services.

Built using **AWS Lambda, S3, DynamoDB**, and **PyPDF**, this system demonstrates how to build scalable document intelligence workflows in the cloud.

---

## 🚀 Features

- 📥 Automatic PDF processing from S3 uploads
- 🧠 Document classification (Invoice, Sales Report, Customer Application)
- 🔍 Weighted keyword + regex-based scoring system
- 📊 Metadata extraction (invoice numbers, totals, emails, etc.)
- 💾 Stores structured data in DynamoDB
- 📦 Saves processed JSON output back to S3
- ⚡ Fully serverless and event-driven architecture



## 🏗️ Architecture


S3 Upload (PDF)
↓
AWS Lambda Trigger
↓
PDF Text Extraction (PyPDF)
↓
Classification Engine (Weighted Scoring + Regex)
↓
Metadata Extraction
↓
Store in DynamoDB
↓
Save JSON Output to S3




## 🧠 Supported Document Types

### 1. Invoice
- Invoice Number
- Total Amount
- Billing Details

### 2. Sales Report
- Region
- Revenue Insights
- Performance Metrics

### 3. Customer Application
- Email
- Phone Number
- Applicant Details



## ⚙️ Tech Stack

- **AWS Lambda** – Serverless compute
- **Amazon S3** – File storage & triggers  
- **Amazon DynamoDB** – NoSQL database  
- **Python** – Core processing logic  
- **PyPDF** – PDF text extraction  
- **Regex (re module)** – Pattern matching



## 🔍 How It Works

1. Upload a PDF file to an S3 bucket  
2. Lambda function is triggered automatically  
3. PDF text is extracted using PyPDF  
4. Document is classified using:
   - Weighted keyword scoring
   - Regex pattern matching
   - Structural analysis  
5. Relevant metadata is extracted  
6. Data is stored in DynamoDB  
7. JSON output is saved back to S3  



## 📦 Example Output

## DynamoDB Record

```json
{
  "document_id": "1234-abc",
  "file_name": "invoice.pdf",
  "category": "Invoice",
  "invoice_number": "INV-1001",
  "total_amount": "500",
  "processed_at": "2026-05-12T18:00:00"
}


## 📊 Classification Logic

The system uses a hybrid approach:

✔ Weighted keyword scoring
✔ Regex-based pattern matching
✔ Structural document detection
✔ Confidence threshold filtering
✔ Ambiguity detection

This ensures higher accuracy compared to simple keyword matching.

## 🛠️ Setup Instructions
1. Clone Repository
git clone https://github.com/your-username/repo-name.git
cd repo-name
2. Install Dependencies
pip install pypdf boto3
3. Configure AWS

Make sure AWS credentials are configured:

aws configure
4. Deploy Lambda
Upload code to AWS Lambda
Set S3 trigger for PDF uploads
Ensure IAM permissions for S3 and DynamoDB
## 🔐 IAM Permissions Required
S3 Read/Write Access
DynamoDB PutItem Access
CloudWatch Logs Access

## 📈 Future Improvements
Add machine learning-based classification (Amazon Comprehend / Textract)
Improve OCR support for scanned PDFs
Add support for more document types (Resume, Contracts, Receipts)
Add API Gateway for REST access
Build frontend dashboard for visualization
👨‍💻 Author

Built as a serverless document intelligence project for learning AWS and real-world document processing pipelines.
