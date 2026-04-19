import os

try:
    import google.generativeai as genai
except ImportError:
    genai = None

def generate_report(prompt):
    """
    Calls the Gemini API to generate an analysis report based on the prompt.
    Fails gracefully if the API key or library is missing.
    """
    if genai is None:
        raise ImportError("google.generativeai not installed")
        
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
        
    genai.configure(api_key=api_key)
    # Recommended model for text generation
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(prompt)
    
    return response.text