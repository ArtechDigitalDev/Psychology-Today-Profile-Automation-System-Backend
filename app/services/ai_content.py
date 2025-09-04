"""
ai_content.py
AI-powered content generation for Psychology Today profile updates.
"""
from openai import OpenAI
from app.config import settings
import logging
import random

logger = logging.getLogger(__name__)

# Configure OpenAI
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def personal_statement_content(ideal_client: str, how_can_help: str, empathy_invitation: str) -> dict:
    """
    Generate personal statement content using AI for Psychology Today profiles.
    
    Args:
        ideal_client: Description of ideal client
        how_can_help: How the therapist can help
        empathy_invitation: Empathy invitation text
        
    Returns:
        dict: Generated content with ideal_client, how_can_help, and empathy_invitation
    """
    try:
        prompt = f"""
You are an expert psychologist and content writer specializing in mental health marketing and profile optimization.

**Task:** Make MINIMAL changes to content for Psychology Today profile.

**STRICT REQUIREMENTS:**
- Change ONLY ONE sentence at a time in each section
- Keep ALL other sentences completely unchanged
- Maintain original character count as much as possible
- Only adjust tone for warmth and professionalism
- DO NOT summarize or condense
- ABSOLUTELY CRITICAL: DO NOT reduce character count from original
- If original content is within limits, make ZERO length changes
- Preserve exact same number of words and sentences
- DO NOT shorten any sentences - keep all sentences at original length
- DO NOT break up long sentences into shorter ones
- DO NOT combine multiple sentences into one
- Maintain exact sentence structure and flow
- The tone must be warm and empathetic
- CRITICAL: Select only ONE sentence to modify per section, leave all others identical

**CHARACTER LIMITS (MAXIMUM):**
- ideal_client: MAX 600 chars
- how_can_help: MAX 360 chars
- empathy_invitation: MAX 360 chars

**Original Content:**
- ideal_client: "{ideal_client}"
- how_can_help: "{how_can_help}"
- empathy_invitation: "{empathy_invitation}"

**Instructions:**
1. Identify ONE sentence in each section that needs improvement
2. Modify ONLY that one sentence for better tone/warmth
3. Keep ALL other sentences exactly the same
4. Count characters exactly
5. Maintain original character count
6. Only trim if exceeds maximum limits

Return JSON with these keys:
{{
    "ideal_client": "content (MAX 600 chars)",
    "how_can_help": "content (MAX 360 chars)",
    "empathy_invitation": "content (MAX 360 chars)"
}}
"""

        system_message = """You are a content editor for Psychology Today therapist profiles. Make minimal changes to existing content while keeping 95-99% of the original text. CRITICAL: Change ONLY ONE sentence at a time in each section, keeping all other sentences completely unchanged. Maintain the original character count as much as possible. Count characters exactly and ensure content meets the specified limits without significantly reducing the original length. MOST IMPORTANT: DO NOT reduce character count from original content - preserve exact same length."""
        
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.5
        )
        
        # Extract the generated content
        content = response.choices[0].message.content
        print("content: ", content)
        # Try to parse JSON from response
        try:
            import json
            parsed_content = json.loads(content)
            print("parsed_content: ", parsed_content)
            
            # Ensure character limits with strict enforcement
            ideal_client = parsed_content.get("ideal_client", "")
            how_can_help = parsed_content.get("how_can_help", "")
            empathy_invitation = parsed_content.get("empathy_invitation", "")
            
            # Validate character limits and log for debugging
            print(f"ideal_client length: {len(ideal_client)} (MAX: 600)")
            print(f"how_can_help length: {len(how_can_help)} (MAX: 360)")
            print(f"empathy_invitation length: {len(empathy_invitation)} (MAX: 360)")
            
            # Check if content meets character requirements and trim if necessary
            if len(ideal_client) > 600:
                print(f"WARNING: ideal_client exceeds maximum: {len(ideal_client)}")
                ideal_client = ideal_client[:597] + "..."
                print(f"Trimmed ideal_client to: {len(ideal_client)} characters")
                
            if len(how_can_help) > 360:
                print(f"WARNING: how_can_help exceeds maximum: {len(how_can_help)}")
                how_can_help = how_can_help[:357] + "..."
                print(f"Trimmed how_can_help to: {len(how_can_help)} characters")
                
            if len(empathy_invitation) > 360:
                print(f"WARNING: empathy_invitation exceeds maximum: {len(empathy_invitation)}")
                empathy_invitation = empathy_invitation[:357] + "..."
                print(f"Trimmed empathy_invitation to: {len(empathy_invitation)} characters")
            
            return {
                "ideal_client": ideal_client,
                "how_can_help": how_can_help,
                "empathy_invitation": empathy_invitation,
                "raw_content": content
            }
        except json.JSONDecodeError:
            # Return original content if JSON parsing fails
            logger.warning("JSON parsing failed, returning original content")
            return {
                "ideal_client": ideal_client,
                "how_can_help": how_can_help,
                "empathy_invitation": empathy_invitation,
                "raw_content": content
            }
        
    except Exception as e:
        logger.error(f"Error generating personal statement content: {str(e)}")
        
        # Return original content if any error occurs
        return {
            "ideal_client": ideal_client,
            "how_can_help": how_can_help,
            "empathy_invitation": empathy_invitation,
            "raw_content": f"Error occurred: {str(e)}"
        }


def top_specialties_content(top_specialties: str = "") -> dict:
    """
    Generate AI-powered content for Psychology Today top specialties section by rewriting existing content.
    
    Args:
        top_specialties (str): Original top specialties text to rewrite
        
    Returns:
        dict: Generated content for the top specialties textarea with proper key
    """
    try:
        
        prompt = f"""
You are an expert psychologist and content writer specializing in mental health marketing and profile optimization.
**Task:** Make MINIMAL changes to content for Psychology Today profile.

**STRICT REQUIREMENTS:**
- Change ONLY ONE sentence at a time in the content
- Keep ALL other sentences completely unchanged
- Maintain original character count as much as possible
- Only adjust tone for warmth and professionalism
- DO NOT summarize or condense
- ABSOLUTELY CRITICAL: DO NOT reduce character count from original
- If original content is within limits, make ZERO length changes
- Preserve exact same number of words and sentences
- DO NOT shorten any sentences - keep all sentences at original length
- DO NOT break up long sentences into shorter ones
- DO NOT combine multiple sentences into one
- Maintain exact sentence structure and flow
- The tone must be warm and empathetic
- CRITICAL: Select only ONE sentence to modify, leave all others identical

**CHARACTER LIMIT (MAXIMUM):** MAX 400 chars

**Original Content:**
- top_specialties: "{top_specialties}"

**Instructions:**
1. Identify ONE sentence that needs improvement
2. Modify ONLY that one sentence for better tone/warmth
3. Keep ALL other sentences exactly the same
4. Count characters exactly
5. Preserve exact same number of words and sentences
6. Only trim if exceeds maximum limit

Return JSON with this key:
{{
    "top_specialties": "content MAX 400 chars"
}}
"""

        system_message = """You are a content editor for Psychology Today therapist profiles. Make minimal changes to existing content while keeping 95-99% of the original text. CRITICAL: Change ONLY ONE sentence at a time, keeping all other sentences completely unchanged. Maintain the original character count as much as possible. Count characters exactly and ensure content meets the specified limit without significantly reducing the original length. MOST IMPORTANT: DO NOT reduce character count from original content - preserve exact same length."""
        
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.5
        )
        
        # Extract the generated content
        content = response.choices[0].message.content
        print("top_specialties content: ", content)
        # Try to parse JSON from response
        try:
            import json
            parsed_content = json.loads(content)
            print("top_specialties parsed_content: ", parsed_content)
            
            # Strict character limit validation and enforcement
            top_specialties = parsed_content.get("top_specialties", "")
            
            # Validate character limits and log for debugging
            print(f"top_specialties length: {len(top_specialties)} (MAX: 400)")
            
            # Check if content meets character requirements
            if len(top_specialties) > 400:
                print(f"WARNING: top_specialties exceeds maximum: {len(top_specialties)}")
                top_specialties = top_specialties[:397] + "..." 
            
            return {
                "top_specialties": top_specialties,
                "raw_content": content
            }
        except json.JSONDecodeError:
            # Return original content if JSON parsing fails
            logger.warning("JSON parsing failed, returning original content")
            return {
                "top_specialties": top_specialties,
                "raw_content": content
            }
        
    except Exception as e:
        logger.error(f"Error generating top specialties content: {str(e)}")
        
        # Return original content if any error occurs
        return {
            "top_specialties": top_specialties,
            "raw_content": f"Error occurred: {str(e)}"
        }




# def personal_statement_content(mental_health_role: str) -> dict:
#     """
#     Generate AI-powered content for Psychology Today profile sections based on mental health role.
    
#     Args:
#         mental_health_role (str): The mental health role (e.g., "Marriage & Family Therapist", "Licensed Clinical Social Worker")
        
#     Returns:
#         dict: Generated content for the four statement textareas with proper keys
#     """
#     try:
#         prompt = f"""
#         Generate comprehensive, professional, empathetic content for a Psychology Today therapist profile with role: {mental_health_role}
        
#         CRITICAL: You MUST follow these EXACT character limits for each section:
        
#         1. PERSONAL STATEMENT - THREE textareas:
#            - "Ideal client description - What are their issues, needs, goals? What do they want and why?" 
#              EXACTLY: 500-580 characters (not less, not more)
#            - "How can you help? Talk about your specialty and what you offer." 
#              EXACTLY: 200-330 characters (not less, not more)
#            - "Build empathy and invite the potential client to reach out to you. Do not include contact details here." 
#              EXACTLY: 200-330 characters (not less, not more)
        
#         2. TOP SPECIALTIES NOTE - ONE textarea:
#            - "These are the main issues I can help you with, this is what a typical treatment plan may involve and the benefits you can expect..." 
#              EXACTLY: 200-320 characters (not less, not more)
#            - Write 3-4 concise, complete sentences
#            - Focus on main issues you can help with
#            - Describe what a typical treatment plan involves
#            - Mention the benefits clients can expect
        
#         STRICT REQUIREMENTS:
#         - Professional yet warm and approachable tone
#         - Specific to the mental health role: {mental_health_role}
#         - Engaging and trustworthy
#         - Encourages potential clients to reach out
#         - RESPECT CHARACTER LIMITS EXACTLY - COUNT EVERY CHARACTER
#         - Avoid generic language, be specific about therapeutic approach
#         - Do not include contact information in the empathy invitation
#         - Use evidence-based therapeutic approaches
#         - Create authentic, empathetic content that builds trust
#         - Make content SEO-friendly for mental health searches
#         - Ensure consistency across all sections
#         - Each section must be substantial and meaningful
        
#         IMPORTANT: Before returning, count the characters in each field and ensure they meet the exact limits.
        
#         Return as JSON with these exact keys:
#         - "ideal_client"
#         - "how_can_help" 
#         - "empathy_invitation"
#         - "top_specialties"
        
#         DO NOT include any other text, comments, or explanations - ONLY the JSON object.
#         """
        
#         response = client.chat.completions.create(
#             model="gpt-4-turbo",
#             messages=[
#                 {"role": "system", "content": "You are an expert therapist and content writer specializing in mental health marketing and profile optimization. Create authentic, empathetic, and conversion-focused content that builds trust with potential clients. Always return valid JSON format with all required keys and do not include any other text or comments or child key."},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=1000,
#             temperature=0.5
#         )
        
#         # Extract the generated content
#         content = response.choices[0].message.content
#         print("content: ", content)
#         # Try to parse JSON from response
#         try:
#             import json
#             parsed_content = json.loads(content)
#             print("parsed_content: ", parsed_content)
            
#             # Ensure character limits with strict enforcement
#             ideal_client = parsed_content.get("ideal_client", "")
#             if len(ideal_client) > 600:
#                 ideal_client = ideal_client[:597] + "..."
                
#             how_can_help = parsed_content.get("how_can_help", "")
#             if len(how_can_help) > 350:
#                 how_can_help = how_can_help[:347] + "..."
                
#             empathy_invitation = parsed_content.get("empathy_invitation", "")
#             if len(empathy_invitation) > 350:
#                 empathy_invitation = empathy_invitation[:347] + "..."
                
#             top_specialties = parsed_content.get("top_specialties", "")
#             if len(top_specialties) > 400:
#                 top_specialties = top_specialties[:397] + "..."
            
#             return {
#                 "ideal_client": ideal_client,
#                 "how_can_help": how_can_help,
#                 "empathy_invitation": empathy_invitation,
#                 "top_specialties": top_specialties,
#                 "raw_content": content
#             }
#         except json.JSONDecodeError:
#             # Fallback if JSON parsing fails
#             return {
#                 "ideal_client": f"My ideal client is someone seeking positive change in their life. They may be struggling with anxiety, depression, or relationship issues, and are looking for a compassionate {mental_health_role.lower()} who can provide a safe, non-judgmental space for healing and growth.",
#                 "how_can_help": f"As a {mental_health_role}, I help clients through evidence-based approaches tailored to their unique needs. I provide a supportive environment where you can explore your thoughts, develop healthy coping strategies, and work towards your personal goals.",
#                 "empathy_invitation": f"I understand that reaching out for help takes courage, and I want you to know that you don't have to do it alone. Whether you're feeling overwhelmed or simply want to understand yourself better, I'm here to support you on your journey to wellness.",
#                 "top_specialties": f"As a {mental_health_role}, I specialize in helping clients with anxiety, depression, and relationship issues. My treatment approach combines evidence-based techniques with personalized care to address your unique needs. You can expect a supportive, non-judgmental environment where we work together to develop healthy coping strategies and achieve lasting positive change.",
#                 "raw_content": content
#             }
        
#     except Exception as e:
#         logger.error(f"Error generating personal statement content for {mental_health_role}: {str(e)}")
        
#         # Fallback content
#         return {
#             "ideal_client": f"I work with individuals who are seeking positive change and personal growth. My ideal client is someone who is ready to explore their thoughts, feelings, and behaviors in a supportive therapeutic environment with a {mental_health_role.lower()}.",
#             "how_can_help": f"As a {mental_health_role}, I provide compassionate, evidence-based therapy to help you overcome challenges and achieve your goals. Using proven therapeutic techniques, I'll help you develop healthy coping strategies and build resilience.",
#             "empathy_invitation": f"Taking the first step towards therapy can feel overwhelming, but you don't have to do it alone. I'm here to provide a safe, non-judgmental space where you can feel heard and supported on your journey to wellness.",
#             "top_specialties": f"As a {mental_health_role}, I specialize in helping clients with anxiety, depression, and relationship issues. My treatment approach combines evidence-based techniques with personalized care to address your unique needs. You can expect a supportive, non-judgmental environment where we work together to develop healthy coping strategies and achieve lasting positive change.",
#             "raw_content": "Fallback content due to AI service error"
#         }



# if __name__ == "__main__":
#     print(_generate_random_zip_code("New York"))
#     print(_fallback_address_parsing("123 Main Street, Los Angeles, CA 90210"))
#     print(extract_address_components("123 Main Street, Los Angeles"))