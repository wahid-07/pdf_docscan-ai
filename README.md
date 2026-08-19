# 📄 PDF DocScan AI

**PDF DocScan AI** is an AI-powered document processing and PDF extraction platform that uses **Google Gemini AI** to extract structured information from PDF documents.

The application provides a web-based interface where users can upload PDF files, process them page by page, extract text/tables/images using AI, and manage the extracted records through a PostgreSQL database.

It also includes authentication, admin controls, audit logging, PDF validation, rejected-upload management, search, and bulk upload functionality.

---

## 🚀 Live Demo

**Live Application:**  
https://pdf-docscan-ai.onrender.com

> The application is deployed on Render using Docker.

---

## ✨ Features

### 📤 PDF Upload

- Single PDF upload
- Bulk PDF upload
- Drag & drop support
- PDF file validation
- File size validation
- Duplicate upload detection
- Background processing support
- Upload status tracking

### 🤖 AI-Powered Extraction

- Page-by-page PDF processing
- Google Gemini AI integration
- Extraction of:
  - Text
  - Tables
  - Structured information
  - Images/content where applicable
- AI extraction status tracking
- Error handling for failed pages

### 🗂️ Document Management

- View uploaded PDFs
- Manage uploaded documents
- Delete PDFs
- View document status
- Track number of pages
- Track upload time
- PDF preview/support

### 🔎 Search & Records

- View all extracted records
- Search extracted content
- Page-wise extraction results
- Store extracted data in PostgreSQL
- Link extracted records with their source PDF

### 🚫 Rejected PDF Management

Invalid or unsupported PDFs are automatically moved to a rejected location.

The application records:

- File name
- File path
- Rejection reason
- File size
- Uploading user
- Upload timestamp

### 👤 Authentication & Authorization

- User authentication
- Login/logout
- Protected API endpoints
- User-based access
- Admin access control

### 🛡️ Admin Panel

Administrators can view:

- Application overview
- Registered users
- Audit logs
- Rejected uploads
- Application statistics

### 📋 Audit Logging

Important application events are recorded, such as:

- Login
- Upload success
- Duplicate upload
- Upload rejection
- Other important user/application actions

### 📊 Dashboard

The dashboard provides an overview of:

- Uploaded documents
- Extracted records
- PDF statistics
- Rejected PDFs
- Processing information

---

# 🏗️ System Architecture

```text
                         ┌──────────────────────┐
                         │      Web Browser      │
                         │   HTML/CSS/JavaScript │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       FastAPI        │
                         │      REST APIs       │
                         └──────────┬───────────┘
                                    │
                    ┌───────────────┼────────────────┐
                    │               │                │
                    ▼               ▼                ▼
             ┌────────────┐  ┌────────────┐  ┌──────────────┐
             │ PDF Handler│  │ Gemini AI  │  │ Authentication│
             │ Validation │  │ Extraction │  │ & Admin       │
             └──────┬─────┘  └──────┬─────┘  └──────────────┘
                    │               │
                    └───────┬───────┘
                            ▼
                   ┌─────────────────┐
                   │   PostgreSQL    │
                   │    Database     │
                   └─────────────────┘
```

---

# 🔄 PDF Processing Workflow

```text
User selects PDF
       │
       ▼
File Upload
       │
       ▼
File Size / Extension Validation
       │
       ▼
PDF Validation
       │
       ├──────────── Invalid ────────────► Rejected Upload
       │
       ▼
Duplicate Check
       │
       ├──────────── Duplicate ─────────► Reject
       │
       ▼
Create PDF Master Record
       │
       ▼
Convert PDF Pages to Images
       │
       ▼
Send Page to Gemini AI
       │
       ▼
Extract Content
       │
       ▼
Store Temporary Records
       │
       ▼
Move Valid Records to Final Table
       │
       ▼
Update PDF Status
       │
       ▼
Display Results
```

---

# 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| **Python** | Backend programming |
| **FastAPI** | REST API and web backend |
| **PostgreSQL** | Database |
| **SQLAlchemy** | ORM and database interaction |
| **Google Gemini AI** | AI-based PDF content extraction |
| **google-genai** | Gemini API integration |
| **PyMuPDF (fitz)** | PDF reading and page information |
| **pdf2image** | PDF page to image conversion |
| **Pillow** | Image processing |
| **Uvicorn** | ASGI server |
| **Docker** | Containerization |
| **Render** | Cloud deployment |
| **HTML/CSS/JavaScript** | Frontend |
| **openpyxl** | Excel export |
| **JWT / Authentication** | User authentication and authorization |

---

# 📁 Project Structure

```text
pdf_docscan-ai/
│
├── main.py
├── requirements.txt
├── Dockerfile
├── README.md
├── .dockerignore
├── .gitignore
│
├── routes/
│   ├── upload.py
│   ├── auth.py
│   ├── admin.py
│   └── ...
│
├── services/
│   ├── ai_extractor.py
│   ├── pdf_handler.py
│   ├── db_handler.py
│   └── ...
│
├── models/
│   └── table_model.py
│
├── database/
│   └── connection.py
│
├── static/
│   ├── index.html
│   ├── script.js
│   └── styles.css
│
├── uploads/
│   ├── accepted/
│   ├── rejected/
│   └── ...
│
└── ...
```

---

# 🗄️ Database

The application uses **PostgreSQL** to store application and extraction data.

The database contains information related to:

### PDF Master

Stores document-level information such as:

- PDF ID
- File name
- File size
- Number of pages
- Status
- Upload timestamp

### Temporary Extraction Data

Stores extracted page-level data while processing is in progress.

### Extracted Data

Stores successfully processed extraction results.

### Rejected Uploads

Stores information about PDFs rejected during validation.

### Users

Stores user authentication and account information.

### Audit Logs

Stores important application events for monitoring and security.

---

# ⚙️ Local Setup

## 1. Clone the Repository

```bash
git clone https://github.com/wahid-07/pdf_docscan-ai.git
```

```bash
cd pdf_docscan-ai
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
```

```bash
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---


# 🗃️ PostgreSQL Setup

Create a PostgreSQL database and configure the connection using:

The application uses SQLAlchemy to communicate with PostgreSQL.

---

# ▶️ Run the Application

Start the FastAPI development server:

```bash
uvicorn main:app --reload
```

The application will normally be available at:

```text
http://127.0.0.1:8000
```

---

# 📚 API Documentation

FastAPI automatically provides interactive API documentation.

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

---

# 🐳 Docker

The project can be built and run using Docker.

### Build

```bash
docker build -t pdf-docscan-ai .
```

### Run

```bash
docker run -p 8000:8000 pdf-docscan-ai
```

---

# ☁️ Deployment

The application is deployed using:

```text
GitHub
   ↓
Docker
   ↓
Render
   ↓
FastAPI
   ↓
PostgreSQL
   ↓
Gemini AI
```

Every update can be deployed by pushing the latest changes to the GitHub repository.

```bash
git add .
git commit -m "Update application"
git push origin main
```

Render can then automatically deploy the latest commit.

---

# 🔒 Security Considerations

The application includes several security-related features:

- Authentication
- Protected API endpoints
- Admin authorization
- User-based access
- Audit logging
- Environment variables for secrets
- Duplicate upload detection
- PDF validation
- File size restrictions

API keys and database credentials should never be hard-coded in the source code.

---

# 🧪 Error Handling

The application handles several types of failures:

- Invalid PDF files
- Empty/invalid documents
- Duplicate uploads
- Gemini API errors
- Database errors
- Authentication errors
- Failed page extraction
- Upload failures

Failed operations are logged for debugging and monitoring.

---

# 🎯 Project Goals

The main goals of PDF DocScan AI are:

1. Automate document information extraction.
2. Reduce manual PDF processing.
3. Use AI to understand unstructured document content.
4. Store extracted information in a structured database.
5. Provide a simple interface for document management.
6. Support scalable document processing.

---

# 👨‍💻 Author

**Wahid Naseem**

B.Tech — Computer Science & Engineering  
NIT Patna

---
