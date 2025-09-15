def calculate_rule_score(lead, offer_data):
    """Calculate rule-based score (max 50 points)"""
    score = 0
    
    # 1. Role relevance (max 20 points)
    role = lead.get('role', '').lower()
    if any(title in role for title in ['head', 'director', 'chief', 'vp', 'vice president', 'founder', 'ceo', 'cto']):
        score += 20  # Decision maker
    elif any(title in role for title in ['manager', 'lead', 'senior']):
        score += 10  # Influencer
    # else: 0 points
    
    # 2. Industry match (max 20 points)
    lead_industry = lead.get('industry', '').lower()
    ideal_industries = [industry.lower() for industry in offer_data.get('ideal_use_cases', [])]
    
    if lead_industry and any(lead_industry in industry or industry in lead_industry for industry in ideal_industries):
        score += 20  # Exact match
    elif lead_industry and any(keyword in lead_industry for industry in ideal_industries for keyword in industry.split()):
        score += 10  # Adjacent match
    # else: 0 points
    
    # 3. Data completeness (max 10 points)
    required_fields = ['name', 'role', 'company', 'industry', 'location', 'linkedin_bio']
    complete_data = all(lead.get(field) and str(lead.get(field)).strip() for field in required_fields)
    if complete_data:
        score += 10
    
    return min(score, 50)  # Cap at 50 points

def calculate_final_score(rule_score, ai_points):
    """Calculate final score and intent category"""
    total_score = rule_score + ai_points
    
    if total_score >= 70:
        intent_category = "High"
    elif total_score >= 40:
        intent_category = "Medium"
    else:
        intent_category = "Low"
    
    return total_score, intent_category