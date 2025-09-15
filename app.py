from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

print(f"Gemini API Key: {GEMINI_API_KEY[:10]}...")  # Debug line

genai.configure(api_key=GEMINI_API_KEY)

# Global variables to store data
offer_data = {}
leads = []
results = []

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv'}

def calculate_rule_score(lead, offer_data):
    """Calculate rule-based score (max 50 points)"""
    score = 0
    
    # 1. Role relevance (max 20 points)
    role = str(lead.get('role', '')).lower()
    if any(title in role for title in ['head', 'director', 'chief', 'vp', 'vice president', 'founder', 'ceo', 'cto']):
        score += 20  # Decision maker
    elif any(title in role for title in ['manager', 'lead', 'senior']):
        score += 10  # Influencer
    
    # 2. Industry match (max 20 points)
    lead_industry = str(lead.get('industry', '')).lower()
    ideal_industries = [str(industry).lower() for industry in offer_data.get('ideal_use_cases', [])]
    
    if lead_industry and any(lead_industry in industry or industry in lead_industry for industry in ideal_industries):
        score += 20  # Exact match
    elif lead_industry and any(keyword in lead_industry for industry in ideal_industries for keyword in industry.split()):
        score += 10  # Adjacent match
    
    # 3. Data completeness (max 10 points)
    required_fields = ['name', 'role', 'company', 'industry', 'location', 'linkedin_bio']
    complete_data = all(lead.get(field) and str(lead.get(field)).strip() for field in required_fields)
    if complete_data:
        score += 10
    
    return min(score, 50)  # Cap at 50 points

def get_gemini_score(lead, offer_data):
    """Get buying intent score from Gemini AI"""
    try:
        # Try multiple models with fallback
        try:
            model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
        except:
            try:
                model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
            except:
                model = genai.GenerativeModel('models/gemini-pro')
        
        prompt = f"""
        Analyze this lead for buying intent:

        PRODUCT:
        - Name: {offer_data.get('name', 'N/A')}
        - Value: {', '.join(offer_data.get('value_props', []))}
        - Ideal For: {', '.join(offer_data.get('ideal_use_cases', []))}

        LEAD:
        - Name: {lead.get('name', 'N/A')}
        - Role: {lead.get('role', 'N/A')}
        - Company: {lead.get('company', 'N/A')}
        - Industry: {lead.get('industry', 'N/A')}
        - Location: {lead.get('location', 'N/A')}
        - Bio: {lead.get('linkedin_bio', 'N/A')}

        Classify buying intent as ONLY: High, Medium, or Low.
        Provide 1-2 sentence explanation.

        Format response exactly as:
        Intent: High/Medium/Low
        Reasoning: [explanation]
        """

        response = model.generate_content(prompt)
        response_text = response.text
        print(f"Gemini Response: {response_text}")  # Debug line
        
        # Parse response
        intent = "Low"
        reasoning = "No reasoning provided"
        
        lines = response_text.split('\n')
        for line in lines:
            if line.startswith('Intent:'):
                intent = line.replace('Intent:', '').strip()
            elif line.startswith('Reasoning:'):
                reasoning = line.replace('Reasoning:', '').strip()
        
        # Map to points
        intent_points = {'High': 50, 'Medium': 30, 'Low': 10}
        points = intent_points.get(intent, 10)
        
        return points, reasoning, intent
        
    except Exception as e:
        print(f"Gemini Error: {e}")
        return 10, "Error analyzing lead", "Low"

@app.route('/offer', methods=['POST'])
def set_offer():
    """Accept product/offer details"""
    global offer_data
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        if 'name' not in data:
            return jsonify({'error': 'Offer name is required'}), 400
        
        offer_data = data
        return jsonify({
            'message': 'Offer data saved successfully',
            'data': offer_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/leads/upload', methods=['POST'])
def upload_leads():
    """Accept CSV file with leads"""
    global leads
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            df = pd.read_csv(file)
            
            # Validate required columns
            required_columns = ['name', 'role', 'company', 'industry', 'location', 'linkedin_bio']
            if not all(col in df.columns for col in required_columns):
                return jsonify({
                    'error': f'CSV must contain: {", ".join(required_columns)}'
                }), 400
            
            leads = df.to_dict('records')
            return jsonify({
                'message': 'File uploaded successfully',
                'count': len(leads),
                'columns': list(df.columns)
            }), 200
        else:
            return jsonify({'error': 'Only CSV files allowed'}), 400
            
    except Exception as e:
        return jsonify({'error': f'File error: {str(e)}'}), 500

@app.route('/score', methods=['POST'])
def score_leads():
    """Run scoring on uploaded leads"""
    global results, offer_data, leads
    try:
        if not offer_data:
            return jsonify({'error': 'No offer data. Provide offer first.'}), 400
        
        if not leads:
            return jsonify({'error': 'No leads uploaded. Upload leads first.'}), 400
        
        results = []
        
        for lead in leads:
            # Rule-based scoring
            rule_score = calculate_rule_score(lead, offer_data)
            
            # AI scoring
            ai_points, ai_reasoning, ai_intent = get_gemini_score(lead, offer_data)
            
            # Final score
            total_score = rule_score + ai_points
            intent_category = "High" if total_score >= 70 else "Medium" if total_score >= 40 else "Low"
            
            results.append({
                'name': lead.get('name', 'N/A'),
                'role': lead.get('role', 'N/A'),
                'company': lead.get('company', 'N/A'),
                'industry': lead.get('industry', 'N/A'),
                'intent': intent_category,
                'score': total_score,
                'reasoning': ai_reasoning,
                'rule_score': rule_score,
                'ai_score': ai_points
            })
        
        return jsonify({
            'message': 'Scoring completed',
            'count': len(results)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Scoring error: {str(e)}'}), 500

@app.route('/results', methods=['GET'])
def get_results():
    """Return scoring results"""
    return jsonify(results), 200

@app.route('/results/csv', methods=['GET'])
def export_results_csv():
    """Export results as CSV"""
    try:
        if not results:
            return jsonify({'error': 'No results available'}), 400
        
        df = pd.DataFrame(results)
        csv_data = df.to_csv(index=False)
        
        return csv_data, 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': 'attachment; filename=scoring_results.csv'
        }
        
    except Exception as e:
        return jsonify({'error': f'CSV error: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Lead Scorer API is running'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)