import os
import io
import librosa
import soundfile as sf
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from fastapi import HTTPException
from pydub import AudioSegment

# Load environment variables
load_dotenv()

# Get API key from environment
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    print("Warning: GOOGLE_API_KEY not found in environment variables.")
    print("Gemini AI functionality will not be available")

# Initialize Google Generative AI client
try:
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    print(f"Error initializing Gemini client: {e}")
    client = None

# Audio settings
INPUT_SAMPLE_RATE = 16000
OUTPUT_SAMPLE_RATE = 24000

# Model configuration
MODEL = "gemini-2.0-flash-live-001"
VOICE = "Kore"

def convert_mp3_to_pcm_bytes(mp3_bytes: bytes) -> bytes | None:
    """Convert MP3 bytes to PCM format suitable for Gemini"""
    print("Converting MP3 to PCM format...")
    try:
        # Create a temporary file-like object
        mp3_buffer = io.BytesIO(mp3_bytes)
        
        # Load audio file with librosa
        y, sr = librosa.load(mp3_buffer, sr=INPUT_SAMPLE_RATE, mono=True)
        
        # Create a BytesIO buffer for the PCM data
        buffer = io.BytesIO()
        
        # Write raw PCM data
        sf.write(buffer, y, INPUT_SAMPLE_RATE, format='RAW', subtype='PCM_16')
        
        # Reset buffer position and read
        buffer.seek(0)
        audio_bytes = buffer.read()
        
        print(f"MP3 to PCM conversion successful: {len(audio_bytes)} bytes")
        return audio_bytes
    
    except Exception as e:
        print(f"Error converting MP3 to PCM: {e}")
        return None

def convert_wav_to_pcm_bytes(wav_bytes: bytes) -> bytes | None:
    """Convert WAV bytes to PCM format suitable for Gemini"""
    print("Converting WAV to PCM format...")
    try:
        # Create a temporary file-like object
        wav_buffer = io.BytesIO(wav_bytes)
        
        # Load audio file with librosa
        y, sr = librosa.load(wav_buffer, sr=INPUT_SAMPLE_RATE, mono=True)
        
        # Create a BytesIO buffer for the PCM data
        buffer = io.BytesIO()
        
        # Write raw PCM data
        sf.write(buffer, y, INPUT_SAMPLE_RATE, format='RAW', subtype='PCM_16')
        
        # Reset buffer position and read
        buffer.seek(0)
        audio_bytes = buffer.read()
        
        print(f"WAV to PCM conversion successful: {len(audio_bytes)} bytes")
        return audio_bytes
    
    except Exception as e:
        print(f"Error converting WAV to PCM: {e}")
        return None

def convert_pcm_to_mp3_bytes(pcm_data: bytes, sample_rate: int) -> bytes:
    """Convert PCM data (bytes) to MP3 bytes"""
    print("Converting PCM to MP3 format...")
    try:
        audio = AudioSegment(data=pcm_data, sample_width=2, frame_rate=sample_rate, channels=1)
        mp3_buffer = io.BytesIO()
        audio.export(mp3_buffer, format="mp3")
        mp3_buffer.seek(0)
        print("PCM to MP3 conversion successful")
        return mp3_buffer.read()
    except Exception as e:
        print(f"Error converting PCM to MP3: {e}")
        raise HTTPException(status_code=500, detail=f"Error converting PCM to MP3: {e}")

def _get_system_instruction_for_user(user=None, db=None):
    """Generate a system instruction that includes farmer context if available"""
    # Base system instruction
    system_instruction = "You are a helpful assistant for Ecofy, a platform that supports sustainable farming. "
    system_instruction += "Respond in either English or Swahili, matching the language of the input. "
    system_instruction += "Be concise, helpful, and provide farming advice when relevant."
    
    # If user is available, add user context
    if user and db:
        try:
            # Get user's preferred language
            lang = user.preferred_language if user.preferred_language else "en"
            system_instruction += f" Communicate primarily in {lang}."
            
            # Get user's farms if they're a farmer
            if user.role == "farmer":
                from app.models.farm import Farm
                farms = db.query(Farm).filter(Farm.user_id == user.id).all()
                
                if farms:
                    system_instruction += " Here is information about the user's farm(s):"
                    
                    for farm in farms:
                        system_instruction += f"\n- Farm: {farm.name}"
                        system_instruction += f"\n  Location: {farm.location}"
                        system_instruction += f"\n  Size: {farm.size}"
                        if farm.topography:
                            system_instruction += f"\n  Topography: {farm.topography}"
                        system_instruction += f"\n  Soil Parameters: {farm.soil_params}"
                        
                        if farm.crop_history and len(farm.crop_history) > 0:
                            system_instruction += "\n  Crop History:"
                            for crop in farm.crop_history:
                                system_instruction += f"\n    - {crop.get('crop_type', 'Unknown')}"
                                system_instruction += f" ({crop.get('planting_date', 'Unknown')} to {crop.get('harvest_date', 'Ongoing')})"
        
        except Exception as e:
            print(f"Error generating system instruction with user context: {e}")
            # Fall back to the basic instruction
    
    return system_instruction

async def process_text_message(text_input: str, user=None, db=None):
    """Process a text message with Gemini and return a text response"""
    if not client:
        return "AI service is currently unavailable. Please try again later."
    
    system_instruction = _get_system_instruction_for_user(user, db)
    
    config = {
        "response_modalities": ["TEXT"],
        "system_instruction": system_instruction,
    }
    conversation_history = [
        {"role": "user", "parts": [{"text": text_input}]}
    ]

    print("Connecting to Gemini for text processing...")
    try:
        async with client.aio.live.connect(model=MODEL, config=config) as session:
            print("Connected to Gemini (text)!")
            
            await session.send_client_content(
                turns=conversation_history,
                turn_complete=True
            )
            print(f"Sent text to Gemini: '{text_input}'")
            
            print("Waiting for text response from Gemini...")
            full_response_text = ""
            async for response in session.receive():
                if response.text is not None:
                    full_response_text += response.text
            
            if full_response_text:
                print(f"Received text response from Gemini")
                return full_response_text
            else:
                print("No text in Gemini response.")
                return "Sorry, I couldn't generate a response. Please try again."
    except Exception as e:
        print(f"Error during Gemini text session: {e}")
        return "An error occurred while processing your message. Please try again later."

async def process_audio_message(audio_bytes: bytes, content_type: str, user=None, db=None):
    """Process an audio message with Gemini and return an audio response"""
    if not client:
        raise HTTPException(status_code=503, detail="AI service is currently unavailable")
    
    # Convert audio based on content type
    if content_type == "audio/mpeg":
        print("Processing MP3 file...")
        pcm_audio_bytes = convert_mp3_to_pcm_bytes(audio_bytes)
    elif content_type == "audio/wav" or content_type == "audio/x-wav" or content_type == "audio/wave":
        print("Processing WAV file...")
        pcm_audio_bytes = convert_wav_to_pcm_bytes(audio_bytes)
    else:
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an MP3 or WAV file.")
    
    # Check conversion success
    if not pcm_audio_bytes:
        raise HTTPException(status_code=500, detail="Failed to convert audio to PCM format.")
    
    system_instruction = _get_system_instruction_for_user(user, db)
    
    # Process with Gemini
    config = {
        "response_modalities": ["AUDIO"],
        "system_instruction": system_instruction,
        "speech_config": {
            "voice_config": {"prebuilt_voice_config": {"voice_name": VOICE}}
        },
    }
    
    print("Connecting to Gemini for audio processing...")
    try:
        async with client.aio.live.connect(model=MODEL, config=config) as session:
            print("Connected to Gemini (audio)!")
            
            print("Sending audio...")
            await session.send_realtime_input(
                audio=types.Blob(data=pcm_audio_bytes, mime_type="audio/pcm;rate=16000")
            )
            await session.send_realtime_input(audio_stream_end=True)
            
            print("Audio sent to Gemini")
            print("Waiting for response...")
            
            audio_bytes = bytearray()
            
            async for response in session.receive():
                if response.data is not None:
                    audio_bytes.extend(response.data)
                
                if (hasattr(response, 'server_content') and 
                    hasattr(response.server_content, 'generation_complete') and 
                    response.server_content.generation_complete):
                    break
            
            # Return the collected audio bytes if any
            if audio_bytes:
                print(f"Received audio response: {len(audio_bytes)} bytes")
                return convert_pcm_to_mp3_bytes(bytes(audio_bytes), OUTPUT_SAMPLE_RATE)
            else:
                print("No audio response received")
                raise HTTPException(status_code=500, detail="No audio response from Gemini.")
    except Exception as e:
        print(f"Error during Gemini audio session: {e}")
        raise HTTPException(status_code=500, detail=f"Gemini API error: {e}") 