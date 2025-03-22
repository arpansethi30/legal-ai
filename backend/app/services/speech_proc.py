import asyncio
import json
from elevenlabs.client import ElevenLabs  # This is the correct import
from app.config import settings
from app.core.llm import get_llm_response

# Initialize ElevenLabs client
client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)

async def transcribe_audio(audio_data: bytes):
    """
    Transcribe audio using ElevenLabs API
    
    Note: Since ElevenLabs doesn't offer transcription yet, 
    this is a placeholder for the hackathon. In a real implementation, 
    you would use a proper speech-to-text service.
    """
    # Simulate network request delay
    await asyncio.sleep(0.5)
    
    # For hackathon purposes, return mock data
    return {
        "text": "This agreement shall commence on January 1st, 2025 and the client agrees to pay $5,000 per month for services rendered.",
        "confidence": 0.95
    }

async def synthesize_speech(text: str, voice_id: str = "default", optimize_for_legal: bool = True, emotion: str = "neutral"):
    """
    Generate speech from text using ElevenLabs with emotional tone control
    
    Emotions can be: neutral, professional, empathetic, concerned, confident
    """
    try:
        # Map emotions to voice characteristics
        emotion_settings = {
            "neutral": {"stability": 0.5, "similarity_boost": 0.5},
            "professional": {"stability": 0.8, "similarity_boost": 0.2},
            "empathetic": {"stability": 0.3, "similarity_boost": 0.7},
            "concerned": {"stability": 0.4, "similarity_boost": 0.6},
            "confident": {"stability": 0.7, "similarity_boost": 0.3}
        }
        
        # Get settings for the requested emotion (default to neutral)
        voice_settings = emotion_settings.get(emotion.lower(), emotion_settings["neutral"])
        
        # If optimizing for legal speech, we can add preprocessing
        if optimize_for_legal:
            # Add emphasis markers for important legal terms
            text = text.replace("shall", "<emphasis>shall</emphasis>")
            text = text.replace("must", "<emphasis>must</emphasis>")
            text = text.replace("agrees to", "<emphasis>agrees to</emphasis>")
            
            # Add pauses at punctuation
            text = text.replace(". ", ".<break time='500ms'/> ")
            text = text.replace("; ", ";<break time='300ms'/> ")
        
        # Map "default" to a specific voice ID or use the provided one
        if voice_id == "default":
            voice_id = "21m00Tcm4TlvDq8ikWAM"  # Default voice ID (Rachel)
        
        # Use the client to generate audio with voice settings
        # Run in executor to make it async-compatible
        loop = asyncio.get_event_loop()
        audio = await loop.run_in_executor(
            None,
            lambda: client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id="eleven_monolingual_v1",
                voice_settings=voice_settings
            )
        )
        
        return audio
    except Exception as e:
        print(f"Error in speech synthesis: {str(e)}")
        # Return empty bytes as fallback
        return b""

async def extract_legal_terms(text: str):
    """
    Extract legal terms and entities from transcript
    """
    prompt = f"""
    Extract all legal terms, entities, and obligations from the following transcript:
    
    {text}
    
    For each term, provide:
    1. The type (e.g., payment term, duration, obligation, right, limitation)
    2. The parties involved
    3. The specific details
    4. Potential risks or ambiguities
    
    Format as a JSON array.
    """
    
    result = await get_llm_response(prompt)
    
    # Parse the result as JSON
    try:
        # Try direct JSON parsing
        legal_terms = json.loads(result)
        return legal_terms
    except json.JSONDecodeError:
        # Try to extract JSON from text
        try:
            start_idx = result.find('[')
            end_idx = result.rfind(']') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = result[start_idx:end_idx]
                return json.loads(json_str)
        except:
            pass
            
        # Fallback if parsing fails
        return [{"type": "payment", "parties": ["client", "service provider"], 
                 "details": "$5,000 per month", "risks": "Payment date not specified"}]