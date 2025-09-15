# Lead Scoring Backend API

A Flask-based backend service that scores leads based on product/offer details and prospect data using rule-based logic and Gemini AI.

## 🚀 Live Deployment
**API Base URL:** `https://lead-scorer.onrender.com`

## 📋 Features
- ✅ Accept product/offer details via JSON API  
- ✅ Upload leads via CSV file  
- ✅ Score leads using rule-based logic + Gemini AI  
- ✅ Get results as JSON or export as CSV  
- ✅ RESTful API design with proper error handling  
- ✅ Health check endpoint  
- ✅ CORS enabled for frontend integration  

## 🛠️ Setup Instructions

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/CoderNikkcoder/lead-scorer.git
   cd lead-scorer
Install dependencies

bash
Copy code
pip install -r requirements.txt
Set up environment variables

Copy .env.example to .env

Add your Gemini API key:

env
Copy code
GEMINI_API_KEY=your_api_key_here
Add Flask environment:

env
Copy code
FLASK_ENV=development
Run the application

bash
Copy code
python app.py
API will be available at: http://localhost:5000

📊 API Endpoints
POST /offer — Set product/offer details
bash
Copy code
curl -X POST https://lead-scorer.onrender.com/offer \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AI Outreach Automation",
    "value_props": ["24/7 outreach", "6x more meetings"],
    "ideal_use_cases": ["B2B SaaS mid-market"]
  }'
POST /leads/upload — Upload CSV file with leads
bash
Copy code
curl -X POST https://lead-scorer.onrender.com/leads/upload \
  -F "file=@leads.csv"
POST /score — Run scoring on uploaded leads
bash
Copy code
curl -X POST https://lead-scorer.onrender.com/score
GET /results — Get scoring results as JSON
bash
Copy code
curl https://lead-scorer.onrender.com/results
GET /results/csv — Export results as CSV file
bash
Copy code
curl https://lead-scorer.onrender.com/results/csv -o results.csv
GET /health — Health check endpoint
bash
Copy code
curl https://lead-scorer.onrender.com/health
📝 CSV Format
Required columns in CSV file:

name

role

company

industry

location

linkedin_bio

🧠 Scoring Logic
Rule-Based Scoring (Max 50 points)
Role Relevance: Decision makers (+20), Influencers (+10), Others (0)

Industry Match: Exact match (+20), Adjacent (+10), No match (0)

Data Completeness: All fields present (+10)

AI Scoring (Max 50 points)
Uses Google Gemini AI for intent analysis

High = 50 points

Medium = 30 points

Low = 10 points

Final Intent Classification
High Intent: ≥70 points

Medium Intent: 40–69 points

Low Intent: <40 points

🏗️ Technology Stack
Backend Framework: Flask (Python)

AI Provider: Google Gemini AI

File Processing: Pandas

Deployment Platform: Render

CORS Handling: Flask-CORS

📞 Support
For issues or questions, please check the GitHub repository.