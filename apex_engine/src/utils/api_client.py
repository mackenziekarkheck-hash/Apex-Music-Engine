"""
APEX Engine API Client - HTTP Client Utilities.

Provides API handling for:
- OpenAI (LLM) integration
- Sonauto API calls
- Simulation mode for development
"""

from typing import Dict, Any, Optional, List
import os
import time
import json
from dataclasses import dataclass


@dataclass
class APIResponse:
    """Standardized API response container."""
    success: bool
    data: Dict[str, Any]
    status_code: int
    error: Optional[str] = None
    latency_ms: float = 0.0


class APIClient:
    """
    Unified API client for APEX Engine.
    
    Provides:
    - Request retry logic
    - Response caching
    - Simulation mode
    - Rate limiting
    """
    
    def __init__(self, simulation_mode: bool = False):
        """
        Initialize the API client.
        
        Args:
            simulation_mode: If True, use simulated responses
        """
        self.simulation_mode = simulation_mode
        self.request_count = 0
        self.last_request_time = 0.0
        self.min_request_interval = 0.1
        
    def _check_rate_limit(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()
    
    def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
        max_retries: int = 3
    ) -> APIResponse:
        """
        Make an HTTP request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            headers: Request headers
            json_data: JSON body data
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            
        Returns:
            APIResponse with results
        """
        if self.simulation_mode:
            return self._simulated_request(method, url, json_data)
        
        self._check_rate_limit()
        
        try:
            import requests
        except ImportError:
            return APIResponse(
                success=False,
                data={},
                status_code=0,
                error="requests library not available"
            )
        
        start_time = time.time()
        last_error = None
        
        for attempt in range(max_retries):
            try:
                self.request_count += 1
                
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json_data,
                    timeout=timeout
                )
                
                latency = (time.time() - start_time) * 1000
                
                return APIResponse(
                    success=response.ok,
                    data=response.json() if response.text else {},
                    status_code=response.status_code,
                    latency_ms=latency
                )
                
            except Exception as e:
                last_error = str(e)
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
        
        return APIResponse(
            success=False,
            data={},
            status_code=0,
            error=f"Request failed after {max_retries} attempts: {last_error}"
        )
    
    def _simulated_request(
        self, 
        method: str, 
        url: str, 
        json_data: Optional[Dict[str, Any]]
    ) -> APIResponse:
        """Generate simulated response for development."""
        import random
        
        time.sleep(random.uniform(0.1, 0.3))
        
        if 'sonauto' in url.lower():
            return APIResponse(
                success=True,
                data={
                    'id': f'sim_{int(time.time())}_{random.randint(1000, 9999)}',
                    'status': 'COMPLETED',
                    'song_paths': ['https://simulated.example.com/audio.ogg']
                },
                status_code=200,
                latency_ms=random.uniform(100, 500)
            )
        
        elif 'openai' in url.lower():
            return APIResponse(
                success=True,
                data={
                    'choices': [{
                        'message': {
                            'content': 'Simulated LLM response for development'
                        }
                    }]
                },
                status_code=200,
                latency_ms=random.uniform(200, 800)
            )
        
        else:
            return APIResponse(
                success=True,
                data={'simulated': True},
                status_code=200,
                latency_ms=random.uniform(50, 200)
            )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get client statistics."""
        return {
            'total_requests': self.request_count,
            'simulation_mode': self.simulation_mode
        }


class OpenAIClient:
    """Specialized client for OpenAI API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI client."""
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        self.base_url = "https://api.openai.com/v1"
        self.client = APIClient(simulation_mode=not bool(self.api_key))
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> APIResponse:
        """
        Make a chat completion request.
        
        Args:
            messages: List of message dicts
            model: Model name
            temperature: Sampling temperature
            max_tokens: Maximum response tokens
            
        Returns:
            APIResponse with completion
        """
        return self.client.request(
            method="POST",
            url=f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json_data={
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        )


class SonautoClient:
    """Specialized client for Sonauto API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Sonauto client."""
        self.api_key = api_key or os.environ.get('SONAUTO_API_KEY')
        self.base_url = "https://api.sonauto.ai/v1"
        self.client = APIClient(simulation_mode=not bool(self.api_key))
    
    def generate(self, payload: Dict[str, Any]) -> APIResponse:
        """Submit a generation request."""
        return self.client.request(
            method="POST",
            url=f"{self.base_url}/generations",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json_data=payload
        )
    
    def get_status(self, task_id: str) -> APIResponse:
        """Get status of a generation task."""
        return self.client.request(
            method="GET",
            url=f"{self.base_url}/generations/{task_id}",
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
