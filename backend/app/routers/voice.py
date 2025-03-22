from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import io

from app.services.speech_proc import (
    transcribe_audio, 
    synthesize_speech,
    extract_legal_terms
)

router = APIRouter()

class TranscriptionResponse(BaseModel):
    text: str
    legal_terms: List[dict]
    confidence: float

class SpeechRequest(BaseModel):
    text: str
    voice_id: str = "default"
    optimize_for_legal: bool = True

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_negotiation(file: UploadFile = File(...)):
    """
    Transcribe negotiation audio and extract legal terms
    """
    try:
        # Read audio file
        audio_data = await file.read()
        
        # Transcribe with ElevenLabs
        transcription = await transcribe_audio(audio_data)
        
        # Extract legal terms
        legal_terms = await extract_legal_terms(transcription["text"])
        
        return {
            "text": transcription["text"],
            "legal_terms": legal_terms,
            "confidence": transcription.get("confidence", 0.95)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@router.post("/synthesize")
async def create_speech(request: SpeechRequest):
    """
    Synthesize speech from text using ElevenLabs
    """
    try:
        audio_content = await synthesize_speech(
            text=request.text,
            voice_id=request.voice_id,
            optimize_for_legal=request.optimize_for_legal
        )
        
        if not audio_content:
            raise HTTPException(status_code=500, detail="Speech synthesis returned empty result")
            
        return StreamingResponse(
            io.BytesIO(audio_content),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=response.mp3"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech synthesis failed: {str(e)}")
    
class EmotionalSpeechRequest(BaseModel):
    text: str
    voice_id: str = "default"
    emotion: str = "neutral"  # neutral, professional, empathetic, concerned, confident
    optimize_for_legal: bool = True

@router.post("/emotional-speech")
async def create_emotional_speech(request: EmotionalSpeechRequest):
    """
    Synthesize speech with specific emotional tone using ElevenLabs
    """
    try:
        audio_content = await synthesize_speech(
            text=request.text,
            voice_id=request.voice_id,
            optimize_for_legal=request.optimize_for_legal,
            emotion=request.emotion
        )
        
        if not audio_content:
            raise HTTPException(status_code=500, detail="Speech synthesis returned empty result")
            
        return StreamingResponse(
            io.BytesIO(audio_content),
            media_type="audio/mpeg",
            headers={"Content-Disposition": f"attachment; filename=speech_{request.emotion}.mp3"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Emotional speech synthesis failed: {str(e)}")
