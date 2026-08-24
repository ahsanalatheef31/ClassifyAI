# 🛍️ Product Classification AI

An AI-powered product classification system that automatically analyzes product information and classifies products according to the **Shopify Product Taxonomy**.

The application accepts product data through an Excel/CSV file and uses AI to determine the appropriate:

* 🏷️ Shopify Category
* 🔹 Product Attributes
* 🔸 Attribute Values
* 🖼️ Image-based product information when an image is available

The system is designed to process products asynchronously using **Celery + Redis** and uses a locally hosted **Qwen2.5-VL** model for AI-powered classification.

---

## 🚀 Features

* Upload product data using CSV or Excel
* Automatic product classification
* Shopify taxonomy/category prediction
* Attribute and attribute-value extraction
* AI-powered image understanding
* Handles products with missing descriptions/images
* Background processing using Celery
* Redis-based task management
* Local LLM inference using Qwen2.5-VL
* Results displayed through a web interface
* Designed to support large product datasets

---

## 🏗️ Architecture

```text
                    ┌─────────────────────┐
                    │      Frontend       │
                    │      React/Vite     │
                    │      Port 5173      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      Django API     │
                    │      Port 8000      │
                    └──────────┬──────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
        ┌─────────────────┐        ┌─────────────────┐
        │     Celery      │        │   Qwen2.5-VL    │
        │ Background Jobs │        │   llama.cpp     │
        └────────┬────────┘        │   Port 8080     │
                 │                 └─────────────────┘
                 ▼
        ┌─────────────────┐
        │     Memurai     │
        │ Redis-compatible│
        │      Server     │
        └─────────────────┘
```

---

## 🛠️ Tech Stack

### Frontend

* React
* Vite
* JavaScript
* HTML/CSS

### Backend

* Python
* Django
* Django REST Framework
* Celery

### AI

* Qwen2.5-VL-3B-Instruct
* llama.cpp
* GGUF quantized model
* Vision-language model for text + image understanding

### Background Processing

* Celery
* Memurai (Redis-compatible server)

### Data Processing

* Pandas
* Excel/CSV processing

---

## 📁 Project Structure

```text
product-classification-ai/
│
├── backend/
│   ├── ...
│
├── frontend/
│   ├── ...
│
├── models/
│   └── qwen-gguf/
│       ├── Qwen2.5-VL-3B-Instruct-Q4_K_M.gguf
│       └── mmproj-Qwen2.5-VL-3B-Instruct-f16.gguf
│
├── venv/
│
├── manage.py
├── requirements.txt
└── README.md
```

> **Important:** The actual model files are not included in this GitHub repository because GGUF model files can be very large. Download the required Qwen2.5-VL model files separately and place them inside `models/qwen-gguf/`.

---

# ⚙️ Installation & Setup

## 1. Clone the repository

```powershell
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd product-classification-ai
```

---

## 2. Create and activate the Python virtual environment

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

---

# 🤖 Qwen2.5-VL Model Setup

This project uses a locally hosted **Qwen2.5-VL-3B-Instruct** GGUF model through `llama.cpp`.

The required model files are:

```text
models/
└── qwen-gguf/
    ├── Qwen2.5-VL-3B-Instruct-Q4_K_M.gguf
    └── mmproj-Qwen2.5-VL-3B-Instruct-f16.gguf
```

Make sure the model files exist at these locations before starting the application.

---

# ▶️ Running the Application

The application requires **four services**:

1. Memurai
2. Qwen2.5-VL llama.cpp server
3. Django backend
4. Celery worker
5. React/Vite frontend

Open separate PowerShell terminals for each service.

---

## Terminal 1 — Start Memurai

Run:

```powershell
& "C:\Program Files\Memurai\memurai.exe"
```

Keep this terminal running.

Memurai acts as the Redis-compatible message broker for Celery.

---

## Terminal 2 — Start Qwen2.5-VL

Run:

```powershell
& "C:\Users\riswa\AppData\Local\Microsoft\WinGet\Packages\ggml.llamacpp_Microsoft.Winget.Source_8wekyb3d8bbwe\llama-server.exe" -m "C:\Users\riswa\product-classification-ai\models\qwen-gguf\Qwen2.5-VL-3B-Instruct-Q4_K_M.gguf" --mmproj "C:\Users\riswa\product-classification-ai\models\qwen-gguf\mmproj-Qwen2.5-VL-3B-Instruct-f16.gguf" --alias "Qwen2.5-VL-3B-Instruct-Q4_K_M.gguf" --port 8080 --host 127.0.0.1 -c 4096 -t 4 -ngl 0
```

The AI model will be available locally on:

```text
http://127.0.0.1:8080
```

Keep this terminal running.

---

## Terminal 3 — Start Django Backend

Navigate to the project directory:

```powershell
cd C:\Users\riswa\product-classification-ai
```

Then start Django:

```powershell
.\venv\Scripts\python manage.py runserver 8000
```

The backend will run on:

```text
http://127.0.0.1:8000
```

---

## Terminal 4 — Start Celery Worker

Navigate to the project directory:

```powershell
cd C:\Users\riswa\product-classification-ai
```

Start Celery:

```powershell
.\venv\Scripts\celery -A backend worker -l info -P threads
```

Keep the worker running.

Celery handles product classification jobs in the background so large uploads do not block the web application.

---

## Terminal 5 — Start Frontend

Navigate to the frontend directory:

```powershell
cd C:\Users\riswa\product-classification-ai\frontend
```

Start the development server:

```powershell
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173
```

---

# 🔄 Application Workflow

```text
User
 │
 ▼
Upload CSV / Excel
 │
 ▼
React Frontend
 │
 ▼
Django REST API
 │
 ▼
Celery Background Task
 │
 ▼
Product Information
 │
 ├───────────────┐
 ▼               ▼
Product Text    Product Image
 │               │
 └───────┬───────┘
         ▼
    Qwen2.5-VL
         │
         ▼
Shopify Category
Attributes
Attribute Values
         │
         ▼
    Store Results
         │
         ▼
Display Results
```

---

# 📊 Example Input

The application accepts product files containing product information such as:

| Product Name          | Description               | Image     |
| --------------------- | ------------------------- | --------- |
| Women's Running Shoes | Lightweight running shoes | Available |
| Ceramic Coffee Mug    | White ceramic coffee mug  | Available |
| Bluetooth Speaker     | Portable wireless speaker | Available |

---

# 📋 Example Output

The AI classifies each product and produces information such as:

```text
Product:
Women's Running Shoes

Shopify Category:
Apparel & Accessories > Shoes > Athletic Shoes

Attributes:
- Gender: Women's
- Sport Type: Running
- Shoe Type: Running Shoes

Attribute Values:
- Color: Black
- Material: Mesh
```

---

# ⚡ Large Dataset Processing

The application uses **Celery background workers** to process product classification jobs asynchronously.

This allows the system to handle large uploads without making the frontend wait for every product to finish individually.

The architecture can be scaled by increasing the number of Celery workers when more computational resources are available.

---

# 🔐 Environment Variables

If environment variables are used in the project, create a `.env` file locally.

Example:

```env
DEBUG=True
SECRET_KEY=your-secret-key
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
LLAMA_SERVER_URL=http://127.0.0.1:8080
```

Do **not** commit sensitive keys, passwords, tokens, or `.env` files to GitHub.

---

# ⚠️ Important GitHub Notes

### Do not upload:

```text
venv/
node_modules/
.env
*.pyc
__pycache__/
large GGUF model files
```

Add them to `.gitignore`.

Example:

```gitignore
# Python
venv/
__pycache__/
*.py[cod]

# Django
*.sqlite3
.env

# Node
node_modules/
dist/

# AI Models
models/qwen-gguf/*.gguf

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

---

# 💻 System Requirements

Recommended:

* Windows 10/11
* Python 3.10+
* Node.js
* npm
* Memurai
* llama.cpp
* Sufficient RAM for the Qwen2.5-VL model
* CPU/GPU depending on the configured llama.cpp inference settings

---

# 🎯 Project Goal

The goal of this project is to automate product categorization and attribute extraction using a locally hosted multimodal AI model.

Instead of manually assigning Shopify categories and attributes to thousands of products, the system analyzes available product text and images and generates structured classification results automatically.

---

## 👩‍💻 Author

**Ahsana Latheef**

B.Tech Computer Science Engineering

---

## ⭐ Future Improvements

* GPU-accelerated inference
* Improved classification confidence scoring
* Support for additional product taxonomies
* Human review and correction workflow
* Classification history
* Advanced batch processing
* Model fine-tuning
* Cloud deployment
* Multi-user authentication and role management
