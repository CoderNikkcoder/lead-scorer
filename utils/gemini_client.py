import google.generativeai as genai
from config import Config

# Configure Gemini
genai.configure(api_key=Config.GEMINI_API_KEY)

def get_gemini_score(lead, offer_data):
    """Get buying intent score from Gemini AI"""
    try:
        # Create the model
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
        You are a sales intelligence tool. Analyze this lead for buying intent:

        PRODUCT DETAILS:
        - Name: {offer_data.get('name', 'N/A')}
        - Value Propositions: {', '.join(offer_data.get('value_props', []))}
        - Ideal Use Cases: {', '.join(offer_data.get('ideal_use_cases', []))}

        LEAD DETAILS:
        - Name: {lead.get('name', 'N/A')}
        - Role: {lead.get('role', 'N/A')}
        - Company: {lead.get('company', 'N/A')}
        - Industry: {lead.get('industry', 'N/A')}
        - Location: {lead.get('location', 'N/A')}
        - LinkedIn Bio: {lead.get('linkedin_bio', 'N/A')}

        Classify this lead's buying intent as ONLY one of: High, Medium, or Low.
        Provide a brief 1-2 sentence explanation.

        Format your response exactly like:
        Intent: High/Medium/Low
        Reasoning: [your explanation here]
        """

        response = model.generate_content(prompt)
        response_text = response.text
        
        # Parse response
        intent = None
        reasoning = ""
        
        lines = response_text.split('\n')
        for line in lines:
            if line.startswith('Intent:'):
                intent = line.replace('Intent:', '').strip()
            elif line.startswith('Reasoning:'):
                reasoning = line.replace('Reasoning:', '').strip()
        
        # Map to points
        intent_points = {
            'High': 50,
            'Medium': 30,
            'Low': 10
        }
        
        points = intent_points.get(intent, 10) if intent else 10
        reasoning = reasoning or "No reasoning provided by AI"
        
        return points, reasoning, intent
        
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return 10, "Error analyzing lead with AI", "Low"