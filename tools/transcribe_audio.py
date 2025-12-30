import os
import sys
import argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

def transcribe_audio(file_path):
    # api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    # if not api_key:
    #     print("Warning: API Key not found in env, attempting default credentials...")
    
    # Let the client attempt to find credentials automatically (Env, ADC, etc.)
    try:
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    except Exception:
        # Fallback to no-arg constructor which uses default lookups
        client = genai.Client()

    print(f"Uploading file: {file_path}...")
    
    # Upload the file to the File API
    # The new SDK handles file uploads for prompting
    try:
        with open(file_path, "rb") as f:
            file_content = f.read()
        
        # Depending on SDK version, we might send bytes directly or upload.
        # For large files, uploads are better.
        # We will try the upload_file pattern if available in this SDK version,
        # otherwise we might encode inline relative to size constraints.
        # But 'google-genai' usually wraps the API well.
        # Let's try the recommended flow for querying with media.
        
        # For simplicity with the newer SDK:
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=[
                types.Part.from_bytes(data=file_content, mime_type="audio/mp3"),
                "この音声を日本語で詳細に書き起こしてください。話者分離は不要ですが、段落を適切に分けて読みやすくしてください。"
            ]
        )
        
        print("\n--- Transcription ---\n")
        print(response.text)
        return response.text

    except Exception as e:
        print(f"Error during transcription: {e}")
        # Fallback query about the error
        try:
             # Just in case the bytes method failed or file is too large (20MB+), 
             # we implies we should use the file API explicit upload.
             # Note: For this first pass, we assume the file fits in the limit or the SDK handles it.
             pass
        except:
            pass
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe audio file using Gemini.")
    parser.add_argument("file_path", help="Path to the audio file")
    args = parser.parse_args()

    if not os.path.exists(args.file_path):
        print(f"Error: File not found: {args.file_path}")
        sys.exit(1)

    transcribe_audio(args.file_path)
