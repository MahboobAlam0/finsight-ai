import os
from gtts import gTTS
import uuid
from pathlib import Path

from deep_translator import GoogleTranslator

def generate_hindi_tts(text: str, output_dir: str = "outputs/audio") -> str:
    """
    Convert text to Hindi speech using gTTS.
    Returns the path to the generated audio file.
    """
    try:
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Translate to Hindi
        translated_text = GoogleTranslator(source='auto', target='hi').translate(text)
        
        # Generate unique filename
        filename = f"tts_{uuid.uuid4()}.mp3"
        filepath = os.path.join(output_dir, filename)
        
        # Initialize gTTS
        # lang='hi' for Hindi
        tts = gTTS(text=translated_text, lang='hi', slow=False)
        
        # Save to file
        tts.save(filepath)
        
        return filepath
    except Exception as e:
        print(f"Error generating TTS: {e}")
        return ""

if __name__ == "__main__":
    # Test
    sample_text = "टेस्ला के शेयर आज रिकॉर्ड ऊंचाई पर पहुंच गए। निवेशकों में उत्साह है।"
    path = generate_hindi_tts(sample_text)
    print(f"Generated audio at: {path}")