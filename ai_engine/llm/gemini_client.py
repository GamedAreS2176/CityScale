import os

try:
    from google import genai
except ImportError:
    genai = None

def generate_report(prompt):
    """
    Calls the Gemini API to generate an analysis report based on the prompt.
    Fails gracefully if the API key or library is missing.
    """
    if genai is None:
        raise ImportError("google.genai not installed")
        
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
        
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    
    return response.text