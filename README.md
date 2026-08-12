# 💧 JalJeevan.AI

> An intelligent web platform for **rooftop rainwater harvesting assessment, rainfall analysis, water-conservation workflows, and AI-assisted guidance**.

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/DRF-API-A30000?logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![FAISS](https://img.shields.io/badge/FAISS-Vector%20Search-0468C8)](https://github.com/facebookresearch/faiss)
[![Gemini](https://img.shields.io/badge/Google-Gemini%20API-4285F4?logo=google&logoColor=white)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-Add%20Your%20License-lightgrey)](#license)

**Live application:** https://jaljeevan-ai.onrender.com

---

## Overview

JalJeevan.AI is a group-developed Django web application built around practical rainwater-harvesting assessment and water-resource workflows.

The current codebase provides:

- A rainwater harvesting calculator with district-based rainfall lookup and rainfall charts
- AI-assisted chatbot responses using **Google Gemini**
- Local semantic retrieval using **FAISS** and **Sentence Transformers**
- User registration, login, logout, and profile photo upload
- Calculation logging and user dashboards
- Vendor registration and vendor search
- Public subsidy/application workflows and an officer dashboard
- A community leaderboard
- A premium feature flag and upgrade flow
- Translation support through the translation service used by the project
- Static pages for the home, about, and contact sections

The project is designed as a web application rather than a separate mobile application.

---

## 🌐 Website Preview

The image below is an **actual visual asset used by the current home page**.

<p align="center">
  <img src="static\assets\Home.png" width="48%">
  <img src="static\assets\Login.png" width="48%">
</p>

<p align="center">
  <img src="static\assets\ChatBot.png" width="48%">
  <img src="static\assets\Calculator.png" width="48%">
</p>

---

## ✨ Current Features

### 🌧️ Rainwater Harvesting Calculator

The calculator supports:

- District search
- Rainfall-based harvesting calculations
- Roof-area and runoff inputs
- Annual harvesting potential
- Tank-size recommendation
- Cost and ROI-related calculations
- Technical result sections
- Monthly rainfall visualisation
- Calculation logging

### 🤖 AI Chatbot

The chatbot is integrated into the Django application through:

```text
User
  │
  ▼
Django /chatbot/api/
  │
  ├── Calculation path
  │
  └── AI path
       │
       ▼
   FAISS retrieval
       │
       ▼
SentenceTransformer embeddings
       │
       ▼
 Relevant documents
       │
       ▼
 Google Gemini API
       │
       ▼
     Response
```

The current implementation uses:

- **FAISS** for vector retrieval
- **`all-MiniLM-L6-v2`** for query embeddings
- **Google Gemini `gemini-2.5-flash`** for response generation
- `faiss_index.bin` and `docs.json` as the local retrieval assets

The chatbot is intentionally **lazy-loaded**: the FAISS index, document metadata, and embedding model are loaded when the chatbot is first used rather than when Django starts.

### 👤 Accounts & Profiles

- Registration
- Login / logout
- Authenticated profile endpoint
- Profile photo upload
- User-specific calculation and chatbot history

### 🏪 Vendor Module

- Vendor registration
- Vendor search by district/pincode
- Vendor service information
- Vendor listing interface

### 🏛️ Government Application Workflow

The current project includes:

- Public application forms
- Application submission
- Application tracking
- Officer registration/login/logout
- Officer dashboard
- Approve / reject / mark-under-review actions

### 🏆 Community & Premium Features

- Community leaderboard
- Premium feature status
- Premium upgrade endpoint
- Premium UI elements in the application

> The current premium implementation is an application-level feature/upgrade flow. It should not be described as a payment gateway unless a payment provider is added to the project.

### 🌍 Translation

The project contains a translation API and translation caching model. The current implementation uses the `deep-translator` package.

---

## 🧱 Technology Stack

| Layer | Technologies |
|---|---|
| Backend | Python, Django |
| APIs | Django REST Framework, Django JSON endpoints |
| Frontend | Django Templates, HTML, CSS, JavaScript |
| AI Generation | Google Gemini API |
| Semantic Search | FAISS, Sentence Transformers |
| Numerical/Data Processing | NumPy, Matplotlib |
| Translation | `deep-translator` |
| Database | SQLite for the current configuration |
| Production Server | Gunicorn |
| Static Files | WhiteNoise / Django static files |
| Deployment | Render |

---

## 📁 Project Structure

```text
jaljeevan.Ai/
├── rainwater_harvesting/       # Django project configuration
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── pages/                      # Home, about, contact, leaderboard, vendor page
├── calculator/                 # Rainfall data and harvesting calculations
├── chatbot/                    # Chat API, retrieval, chat history
├── accounts/                   # Authentication and profiles
├── vendorRegistration/         # Vendor registration/search
├── GovtApplications/           # Public applications and officer workflow
├── premium/                    # Premium feature state/upgrade flow
├── translations/               # Translation API and cache
│
├── templates/                  # Django HTML templates
├── static/                     # CSS, JavaScript, images
├── fixtures/                   # Project data fixtures
│
├── faiss_index.bin             # Local FAISS index used by chatbot
├── docs.json                   # Chatbot document metadata
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## 📊 Project Data

The repository includes rainfall-related fixture files and chatbot retrieval assets.

Examples include:

```text
fixtures/
├── Annual_AVG_Rainfall_fixtures_for_model.json
├── Area_Monthly_Rainfall_graphplot_fixtures_with_timestamps.json
├── Monthly Rainfall Data.json
└── vendordata.json
```

The project materials also reference rainfall, groundwater, aquifer, soil, and Bhuvan/CGWB/IMD-related datasets. The README does **not** claim that these are all live external API integrations; the current repository contains local data/metadata and application logic built around them.

---

## 🔐 Environment Variables

Create a `.env` file in the project root.

Start from:

```bash
copy .env.example .env
```

or on Linux/macOS:

```bash
cp .env.example .env
```

Then configure:

```env
GEMINI_API_KEY=your_own_gemini_api_key
SECRET_KEY=your_django_secret_key
DEBUG=True
```

For production, also configure the appropriate allowed hosts and production settings required by your deployment.

### Security

**Never commit `.env` or real API credentials to GitHub.**

Use `.env.example` only as a template.

> **Important:** before publishing this repository, inspect `rainwater_harvesting/settings.py` and rotate/remove any credential material that may already exist there. A credential that has appeared in source code should be considered exposed.

---

## 🛠️ Local Development

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd jaljeevan.Ai
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install the dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Create `.env` and add your own Gemini API key and Django secret key.

### 5. Apply migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Load the included fixtures

```bash
python manage.py loaddata fixtures/Annual_AVG_Rainfall_fixtures_for_model.json
python manage.py loaddata fixtures/Area_Monthly_Rainfall_graphplot_fixtures_with_timestamps.json
python manage.py loaddata "fixtures/Monthly Rainfall Data.json"
python manage.py loaddata fixtures/vendordata.json
```

If a fixture has already been loaded or conflicts with existing database data, use the normal Django fixture/database workflow for your environment.

### 7. Check the Django project

```bash
python manage.py check
```

### 8. Run locally

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

---

## 🧪 Useful Development Commands

Create an admin account:

```bash
python manage.py createsuperuser
```

Run tests:

```bash
python manage.py test
```

Collect production static files:

```bash
python manage.py collectstatic
```

---

## 🚀 Deployment

The application can be deployed as a Django web service using Gunicorn.

A typical production start command is:

```bash
gunicorn rainwater_harvesting.wsgi:application
```

Set production environment variables in the hosting platform rather than committing them to the repository.

### Render

The current project has been deployed at:

```text
https://jaljeevan-ai.onrender.com
```

When deploying on a low-memory instance, the chatbot can be the most resource-intensive component because it loads:

- FAISS index data
- document metadata
- the Sentence Transformer embedding model

For this reason, deployment memory should be considered separately from normal Django website memory. A future production architecture may separate the chatbot into its own service if needed.

---

## 🤝 Contributing

JalJeevan.AI is a **group project**, and contributions are welcome.

### Contribution workflow

1. Fork the repository.
2. Create a feature branch.

```bash
git checkout -b feature/your-feature-name
```

3. Make your changes.
4. Test locally.

```bash
python manage.py check
python manage.py test
```

5. Commit with a clear message.

```bash
git add .
git commit -m "Add <feature>"
```

6. Push the branch.

```bash
git push origin feature/your-feature-name
```

7. Open a Pull Request describing:
   - what changed
   - why it changed
   - how it was tested
   - any deployment or database considerations

### Contribution guidelines

- Keep secrets out of source control.
- Avoid committing generated files unless they are required by the application.
- Keep changes focused and easy to review.
- Update documentation when behaviour or setup changes.
- Test chatbot, calculator, authentication, and related endpoints when modifying shared backend code.

---

## 👥 Contributors

The current project materials identify the following group members:

## 👥 Contributors

JalJeevan.AI was developed collaboratively as a group project, with responsibilities distributed across different areas of the application.

| Contributor     | Role & Contributions                                       |
| --------------- | ---------------------------------------------------------- |
| **Manish Shaw** | Chatbot development, chatbot deployment, and data handling |                                        |
| **Tirthes Samanta**     | Backend development                                        |
| **Tapasi Garai**      | Backend development                                        |
| **Sandip Sen**      | Frontend development                                       |
| **Sovan Kar**       | Frontend development                                       |

### Contribution Areas

* **AI & Chatbot:** Manish Shaw
* **Data:** Manish Shaw
* **Backend:** Tirthes Samanta, Tapasi Garai
* **Frontend:** Sandip Sen, Sovan Kar
* **Deployment:** Manish Shaw

We collaborated throughout development to integrate the frontend, backend, data, chatbot, and deployment components into the final application.


For future commits and pull requests, add contributors based on the work they actually perform rather than assigning unsupported role titles.

---

## 📌 Current Architecture

```text
                         ┌───────────────────────┐
                         │        User           │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │   Django Web App      │
                         │                       │
                         │ Pages / Auth /        │
                         │ Calculator / Vendors  │
                         │ Applications / etc.   │
                         └───────────┬───────────┘
                                     │
                        ┌────────────┴────────────┐
                        │                         │
                        ▼                         ▼
              ┌─────────────────┐       ┌─────────────────┐
              │  Django Data    │       │   Chatbot API   │
              │  & SQLite       │       │                 │
              └─────────────────┘       │ FAISS           │
                                        │ Sentence        │
                                        │ Transformers    │
                                        │ Gemini API      │
                                        └─────────────────┘
```

---

## 🔮 Possible Next Steps

The codebase is suitable for further work in areas such as:

- Separating the chatbot from the main Django process for lower memory pressure
- Moving production data from SQLite to a managed database
- Improving automated tests
- Adding structured production logging
- Adding stronger API authentication and request validation
- Improving chatbot retrieval and indexing
- Adding CI/CD checks for pull requests

These are development directions, not claims that the features are already implemented.

---

## 📄 License

No license file is currently specified in the repository.

Before making the project publicly available, add a license that matches the group's intended terms.

---

<p align="center">
  <strong>JalJeevan.AI</strong><br>
  Building practical digital tools for rainwater harvesting and water conservation.
</p>
