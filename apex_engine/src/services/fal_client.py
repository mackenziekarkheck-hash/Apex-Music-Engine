"""
Fal.ai Client for MiniMax Music v2.

Implements async queue pattern:
1. Submit generation request
2. Poll for status with exponential backoff
3. Retrieve result when complete
"""

import os
import time
import logging
import requests
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

FAL_API_BASE = "https://queue.fal.run"
FAL_MODEL = "fal-ai/minimax-music/v2"

@dataclass
class FalGenerationResult:
    """Result from Fal.ai music generation."""
    request_id: str
    status: str
    audio_url: Optional[str] = None
    duration: Optional[float] = None
    error: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None


class FalMusicClient:
    """
    Client for Fal.ai MiniMax Music v2 API.
    
    Uses the async queue pattern:
    - POST to submit generation
    - GET /status to poll
    - GET /result to retrieve
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Fal.ai client.
        
        Args:
            api_key: Fal.ai API key. If not provided, reads from FAL_KEY env var.
        """
        self.api_key = api_key or os.environ.get('FAL_KEY')
        self.base_url = f"{FAL_API_BASE}/{FAL_MODEL}"
        self.simulation_mode = not self.api_key
        
        if self.simulation_mode:
            logger.warning("No FAL_KEY found. Running in simulation mode.")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        return {
            "Authorization": f"Key {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def submit_generation(self, payload: Dict[str, Any]) -> FalGenerationResult:
        """
        Submit a generation request to the Fal.ai queue.
        
        Args:
            payload: Generation payload with prompt, lyrics_prompt, etc.
            
        Returns:
            FalGenerationResult with request_id for polling.
        """
        if self.simulation_mode:
            return self._simulate_submit(payload)
        
        url = self.base_url
        
        try:
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                return FalGenerationResult(
                    request_id=data.get('request_id', ''),
                    status='IN_QUEUE',
                    raw_response=data
                )
            else:
                error_msg = f"Submit failed: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return FalGenerationResult(
                    request_id='',
                    status='FAILED',
                    error=error_msg
                )
                
        except Exception as e:
            logger.error(f"Submit exception: {e}")
            return FalGenerationResult(
                request_id='',
                status='FAILED',
                error=str(e)
            )
    
    def poll_status(
        self, 
        request_id: str,
        max_attempts: int = 60,
        initial_delay: float = 2.0,
        max_delay: float = 10.0
    ) -> FalGenerationResult:
        """
        Poll for generation status with exponential backoff.
        
        Args:
            request_id: The request ID from submit_generation
            max_attempts: Maximum polling attempts
            initial_delay: Initial delay between polls (seconds)
            max_delay: Maximum delay between polls (seconds)
            
        Returns:
            FalGenerationResult with final status and audio URL if complete.
        """
        if self.simulation_mode:
            return self._simulate_result(request_id)
        
        url = f"{self.base_url}/requests/{request_id}/status"
        delay = initial_delay
        
        for attempt in range(max_attempts):
            try:
                response = requests.get(url, headers=self._get_headers(), timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get('status', 'UNKNOWN')
                    
                    logger.info(f"Poll attempt {attempt + 1}: status={status}")
                    
                    if status == 'COMPLETED':
                        return self._get_result(request_id)
                    elif status in ['FAILED', 'CANCELLED']:
                        return FalGenerationResult(
                            request_id=request_id,
                            status=status,
                            error=data.get('error', 'Generation failed'),
                            raw_response=data
                        )
                    
                    time.sleep(delay)
                    delay = min(delay * 1.5, max_delay)
                    
                else:
                    logger.warning(f"Poll failed: {response.status_code}")
                    time.sleep(delay)
                    
            except Exception as e:
                logger.warning(f"Poll exception: {e}")
                time.sleep(delay)
        
        return FalGenerationResult(
            request_id=request_id,
            status='TIMEOUT',
            error='Polling timed out'
        )
    
    def _get_result(self, request_id: str) -> FalGenerationResult:
        """Retrieve the generation result."""
        url = f"{self.base_url}/requests/{request_id}"
        
        try:
            response = requests.get(url, headers=self._get_headers(), timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                audio_data = data.get('audio', {})
                
                return FalGenerationResult(
                    request_id=request_id,
                    status='COMPLETED',
                    audio_url=audio_data.get('url'),
                    duration=audio_data.get('duration'),
                    raw_response=data
                )
            else:
                return FalGenerationResult(
                    request_id=request_id,
                    status='FAILED',
                    error=f"Result fetch failed: {response.status_code}"
                )
                
        except Exception as e:
            return FalGenerationResult(
                request_id=request_id,
                status='FAILED',
                error=str(e)
            )
    
    def generate_music(self, payload: Dict[str, Any]) -> FalGenerationResult:
        """
        Full generation flow: submit, poll, and retrieve result.
        
        Args:
            payload: Generation payload
            
        Returns:
            FalGenerationResult with audio URL if successful.
        """
        submit_result = self.submit_generation(payload)
        
        if submit_result.status == 'FAILED':
            return submit_result
        
        return self.poll_status(submit_result.request_id)
    
    def _simulate_submit(self, payload: Dict[str, Any]) -> FalGenerationResult:
        """Simulate a submission for development."""
        import hashlib
        request_id = hashlib.md5(str(payload).encode()).hexdigest()[:16]
        logger.info(f"[SIMULATION] Submitted generation: {request_id}")
        return FalGenerationResult(
            request_id=request_id,
            status='IN_QUEUE',
            raw_response={'simulated': True, 'payload': payload}
        )
    
    def _simulate_result(self, request_id: str) -> FalGenerationResult:
        """Simulate a completed result for development."""
        time.sleep(1)
        logger.info(f"[SIMULATION] Generation complete: {request_id}")
        return FalGenerationResult(
            request_id=request_id,
            status='COMPLETED',
            audio_url=f"https://simulated.fal.ai/audio/{request_id}.mp3",
            duration=180.0,
            raw_response={'simulated': True}
        )


def build_fal_payload(
    prompt: str,
    lyrics_prompt: str,
    reference_audio_url: Optional[str] = None,
    sample_rate: int = 44100,
    bitrate: int = 256000,
    format: str = "mp3"
) -> Dict[str, Any]:
    """
    Build a validated Fal.ai payload for MiniMax Music v2.
    
    Args:
        prompt: Style/genre description (max 300 chars)
        lyrics_prompt: Lyrics with structure tags (max 3000 chars)
        reference_audio_url: Optional reference audio URL
        sample_rate: Audio sample rate
        bitrate: Audio bitrate
        format: Output format (mp3, wav, flac)
        
    Returns:
        Validated payload dict ready for API submission.
    """
    if len(prompt) > 300:
        logger.warning(f"Prompt too long ({len(prompt)} chars), truncating to 300")
        prompt = prompt[:297] + "..."
    
    if len(lyrics_prompt) > 3000:
        logger.warning(f"Lyrics too long ({len(lyrics_prompt)} chars), truncating to 3000")
        lyrics_prompt = lyrics_prompt[:2997] + "..."
    
    payload = {
        "input": {
            "prompt": prompt,
            "lyrics_prompt": lyrics_prompt,
            "audio_setting": {
                "sample_rate": str(sample_rate),
                "bitrate": str(bitrate),
                "format": format
            }
        }
    }
    
    if reference_audio_url:
        payload["input"]["reference_audio_url"] = reference_audio_url
    
    return payload
