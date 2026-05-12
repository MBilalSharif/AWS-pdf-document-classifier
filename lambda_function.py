import json
import boto3
import re
import uuid
from datetime import datetime
from pypdf import PdfReader

# AWS Clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

TABLE_NAME = "DocMetaData"
table = dynamodb.Table(TABLE_NAME)


# =========================================================
# WEIGHTED DOCUMENT CLASSIFICATION RULES
# =========================================================

DOCUMENT_RULES = {

    "Invoice": {

        "keywords": {
            "invoice": 3,
            "invoice number": 8,
            "bill to": 7,
            "due date": 7,
            "amount due": 9,
            "payment terms": 5,
            "subtotal": 5,
            "tax": 4,
            "total amount": 6,
            "total due": 8,
            "unit price": 5,
            "qty": 5
        },

        "regex_patterns": {
            r'invoice\s*(number|#)': 10,
            r'amount\s*due': 9,
            r'bill\s*to': 7,
            r'due\s*date': 7,
            r'subtotal': 5,
            r'tax': 4,
            r'qty\s+.*unit\s*price': 10
        },

        "minimum_score": 12
    },

    "Sales Report": {

        "keywords": {
            "sales report": 10,
            "monthly sales": 8,
            "quarterly sales": 8,
            "quarterly revenue": 8,
            "revenue": 5,
            "sales summary": 7,
            "performance": 4,
            "units sold": 6,
            "analytics": 5,
            "kpi": 5,
            "region": 4,
            "growth": 4,
            "forecast": 4
        },

        "regex_patterns": {
            r'sales\s*report': 10,
            r'monthly\s*sales': 8,
            r'quarterly\s*(sales|revenue)': 9,
            r'units\s*sold': 7,
            r'sales\s*summary': 7,
            r'performance\s*metrics': 6
        },

        "minimum_score": 12
    },

    "Customer Application": {

        "keywords": {
            "application": 4,
            "customer application": 10,
            "application form": 10,
            "applicant": 7,
            "full name": 5,
            "date of birth": 7,
            "email": 4,
            "phone number": 5,
            "address": 4,
            "employment": 5,
            "signature": 5,
            "apply": 3
        },

        "regex_patterns": {
            r'application\s*form': 10,
            r'applicant\s*name': 8,
            r'date\s*of\s*birth': 7,
            r'phone\s*number': 6,
            r'email\s*address': 6,
            r'employment\s*status': 7,
            r'signature': 5
        },

        "minimum_score": 10
    }
}


# =========================================================
# TEXT EXTRACTION
# =========================================================

def extract_text_from_pdf(file_path):

    text = ""

    reader = PdfReader(file_path)

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


# =========================================================
# DOCUMENT CLASSIFICATION
# =========================================================

def classify_document(text):

    text = text.lower()

    scores = {}

    # -----------------------------------------------------
    # Calculate score for each category
    # -----------------------------------------------------

    for category, rules in DOCUMENT_RULES.items():

        score = 0

        # -----------------------------
        # Keyword scoring
        # -----------------------------
        for keyword, weight in rules["keywords"].items():

            if keyword in text:

                score += weight

                print(f"[{category}] Keyword Match: "
                      f"'{keyword}' (+{weight})")

        # -----------------------------
        # Regex scoring
        # -----------------------------
        for pattern, weight in rules["regex_patterns"].items():

            if re.search(pattern, text, re.IGNORECASE):

                score += weight

                print(f"[{category}] Regex Match: "
                      f"'{pattern}' (+{weight})")

        # -----------------------------
        # Structural detection
        # -----------------------------

        # Invoice structure
        if category == "Invoice":

            if (
                "qty" in text and
                "unit price" in text and
                "total" in text
            ):
                score += 12
                print("[Invoice] Structure Match (+12)")

        # Sales report structure
        elif category == "Sales Report":

            if (
                "revenue" in text and
                "region" in text and
                "performance" in text
            ):
                score += 10
                print("[Sales Report] Structure Match (+10)")

        # Customer application structure
        elif category == "Customer Application":

            if (
                "full name" in text and
                "date of birth" in text and
                "signature" in text
            ):
                score += 10
                print("[Customer Application] Structure Match (+10)")

        scores[category] = score

    # -----------------------------------------------------
    # Print scores
    # -----------------------------------------------------

    print("\nFINAL SCORES")
    print(json.dumps(scores, indent=2))

    # -----------------------------------------------------
    # Find best category
    # -----------------------------------------------------

    best_category = max(scores, key=scores.get)
    best_score = scores[best_category]

    # -----------------------------------------------------
    # Confidence threshold check
    # -----------------------------------------------------

    minimum_score = DOCUMENT_RULES[best_category]["minimum_score"]

    if best_score < minimum_score:

        print("Low confidence classification")

        return "Unknown"

    # -----------------------------------------------------
    # Ambiguity detection
    # -----------------------------------------------------

    sorted_scores = sorted(scores.values(), reverse=True)

    # Prevent close-score misclassification
    if len(sorted_scores) > 1:

        if sorted_scores[0] - sorted_scores[1] <= 3:

            print("Ambiguous document detected")

            return "Unknown"

    return best_category


# =========================================================
# METADATA EXTRACTION
# =========================================================

def extract_metadata(text, category):

    metadata = {}

    # -----------------------------------------------------
    # INVOICE
    # -----------------------------------------------------
    if category == "Invoice":

        invoice_number = re.search(
            r'Invoice\s*(Number|#)?[:\s]*([A-Z0-9-]+)',
            text,
            re.IGNORECASE
        )

        metadata["invoice_number"] = (
            invoice_number.group(2)
            if invoice_number
            else None
        )

        total_amount = re.search(
            r'(Total\s*Amount|Amount\s*Due)[:\s]*\$?([0-9,.]+)',
            text,
            re.IGNORECASE
        )

        metadata["total_amount"] = (
            total_amount.group(2)
            if total_amount
            else None
        )

    # -----------------------------------------------------
    # SALES REPORT
    # -----------------------------------------------------
    elif category == "Sales Report":

        region = re.search(
            r'Region[:\s]*(.+)',
            text,
            re.IGNORECASE
        )

        metadata["region"] = (
            region.group(1).strip()
            if region
            else None
        )

    # -----------------------------------------------------
    # CUSTOMER APPLICATION
    # -----------------------------------------------------
    elif category == "Customer Application":

        email = re.search(
            r'[\w\.-]+@[\w\.-]+',
            text
        )

        metadata["email"] = (
            email.group(0)
            if email
            else None
        )

        phone = re.search(
            r'(\+?\d[\d\s\-]{8,15}\d)',
            text
        )

        metadata["phone_number"] = (
            phone.group(0)
            if phone
            else None
        )

    return metadata


# =========================================================
# SAVE TO DYNAMODB
# =========================================================

def save_to_dynamodb(document_id,
                     file_name,
                     category,
                     text,
                     metadata):

    if not document_id:
        document_id = str(uuid.uuid4())

    item = {
        "document_id": document_id,
        "file_name": file_name,
        "category": category,
        "extracted_text": text[:3000],
        "processed_at": datetime.utcnow().isoformat()
    }

    metadata.pop("document_id", None)

    item.update(metadata)

    print("\nFINAL DYNAMODB ITEM")
    print(json.dumps(item, indent=2))

    table.put_item(Item=item)


# =========================================================
# SAVE JSON TO S3
# =========================================================

def save_json(bucket,
              file_name,
              category,
              metadata):

    output = {
        "file_name": file_name,
        "category": category,
        "metadata": metadata,
        "processed_at": datetime.utcnow().isoformat()
    }

    key = f"processed/{file_name.replace('.pdf', '.json')}"

    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(output, indent=2),
        ContentType="application/json"
    )


# =========================================================
# LAMBDA HANDLER
# =========================================================

def lambda_handler(event, context):

    try:

        bucket = (
            event['Records'][0]['s3']['bucket']['name']
        )

        key = (
            event['Records'][0]['s3']['object']['key']
        )

        print(f"\nProcessing File: {key}")

        local_file = f"/tmp/{key.split('/')[-1]}"

        # -------------------------------------------------
        # Download PDF
        # -------------------------------------------------

        s3.download_file(bucket, key, local_file)

        print("PDF Downloaded")

        # -------------------------------------------------
        # Extract text
        # -------------------------------------------------

        text = extract_text_from_pdf(local_file)

        print("Text Extracted")

        # -------------------------------------------------
        # Classify document
        # -------------------------------------------------

        category = classify_document(text)

        print(f"Detected Category: {category}")

        # -------------------------------------------------
        # Extract metadata
        # -------------------------------------------------

        metadata = extract_metadata(text, category)

        print("Metadata Extracted")

        # -------------------------------------------------
        # Generate document ID
        # -------------------------------------------------

        document_id = str(uuid.uuid4())

        # -------------------------------------------------
        # Save to DynamoDB
        # -------------------------------------------------

        save_to_dynamodb(
            document_id,
            key,
            category,
            text,
            metadata
        )

        # -------------------------------------------------
        # Save JSON to S3
        # -------------------------------------------------

        save_json(
            bucket,
            key.split('/')[-1],
            category,
            metadata
        )

        # -------------------------------------------------
        # Success response
        # -------------------------------------------------

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Success",
                "document_id": document_id,
                "category": category
            })
        }

    except Exception as e:

        print("ERROR:", str(e))

        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            })
        }