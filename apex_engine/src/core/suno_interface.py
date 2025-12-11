"""
Sonauto Interface - Fal.ai API Client for Audio Generation.

This module provides the Neo-Apex interface to Sonauto via fal.ai endpoints:
- Song generation with CFG scale control (prompt_strength)
- Inpainting with correct [[start, end]] section format
- Extension with side and crop_duration parameters
- Webhook-first async pattern with polling fallback

Architecture: fal.ai/models/sonauto/v2 (NOT api.sonauto.ai/v1)
Reference: Sonauto API Refactoring Plan, Neo-Apex Architecture Documentation
"""

from typing import Dict, Any, List, Optional, Union, Tuple
import os
import time
import json
import hashlib
import hmac
import warnings

from tenacity import (
    retry, 
    stop_after_attempt, 
    wait_exponential, 
    retry_if_exception_type,
    wait_chain,
    wait_fixed
)
import requests

from ..agents.agent_base import GenerativeAgent, AgentRole, AgentResult
from .fal_models import (
    SonautoGenerationRequest,
    SonautoInpaintRequest,
    SonautoExtendRequest,
    OutputFormat,
    GENRE_CFG_DEFAULTS,
    COST_PER_GENERATION_USD,
    COST_PER_INPAINT_USD,
    load_tag_database
)


class RateLimitError(Exception):
    """Raised when API returns 429 Too Many Requests."""
    def __init__(self, retry_after: Optional[int] = None):
        self.retry_after = retry_after
        super().__init__(f"Rate limited. Retry after: {retry_after}s")


def _is_retryable_error(exception: Exception) -> bool:
    """Check if an exception should trigger a retry."""
    if isinstance(exception, requests.exceptions.Timeout):
        return True
    if isinstance(exception, requests.exceptions.ConnectionError):
        return True
    if isinstance(exception, RateLimitError):
        return True
    if isinstance(exception, requests.exceptions.HTTPError):
        if hasattr(exception, 'response') and exception.response is not None:
            return exception.response.status_code in (429, 500, 502, 503, 504)
    return False


class SonautoOperator(GenerativeAgent):
    """
    Sonauto Operator: Neo-Apex bridge to the fal.ai generative engine.
    
    This agent manages all Sonauto API interactions via fal.ai:
    - Authentication via FAL_KEY (Key header format)
    - Pydantic-validated payload construction
    - Generation, inpainting, and extension requests
    - Webhook-first with polling fallback
    - USD cost tracking (Shadow Ledger compatible)
    
    Reference: 
    - Sonauto API Refactoring Plan Section 2.2 "Canonical Endpoint Decision"
    - Sonauto API Design & Critique Section 4.1 "God-Mode Payload"
    """
    
    FAL_BASE_URL = "https://fal.run/fal-ai/sonauto/v2"
    FAL_QUEUE_URL = "https://queue.fal.run/fal-ai/sonauto/v2"
    
    ENDPOINTS = {
        'generate': '/text-to-music',
        'inpaint': '/inpaint',
        'extend': '/extend'
    }
    
    SUPPORTED_ENV_KEYS = ['FAL_KEY', 'SONAUTO_API_KEY']
    
    @property
    def role(self) -> AgentRole:
        return AgentRole.SONAUTO_OPERATOR
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment, preferring FAL_KEY."""
        for key_name in self.SUPPORTED_ENV_KEYS:
            key = os.environ.get(key_name)
            if key:
                return key
        return None
    
    def _get_auth_headers(self, api_key: str) -> Dict[str, str]:
        """
        Construct authentication headers for fal.ai.
        
        Reference: Refactoring Plan Section 2.3 - Key <FAL_KEY> format
        """
        return {
            'Authorization': f'Key {api_key}',
            'Content-Type': 'application/json'
        }
    
    def _validate_input(self, state: Dict[str, Any]) -> List[str]:
        """Validate that we have necessary inputs for generation."""
        errors = []
        
        if not state.get('lyrics_validated') and not state.get('lyrics_draft'):
            if not state.get('structured_plan', {}).get('instrumental', False):
                errors.append("Lyrics required for vocal generation")
                
        if not state.get('structured_plan') and not state.get('sonauto_prompt'):
            errors.append("Structured plan or prompt required")
            
        return errors
    
    def _execute(self, state: Dict[str, Any]) -> AgentResult:
        """
        Execute Sonauto generation, inpainting, or extension.
        
        Flow:
        1. Check operation type (new generation, inpaint, or extend)
        2. Construct Pydantic-validated payload
        3. Submit request to fal.ai
        4. Handle async completion (webhook or polling)
        5. Download and store audio asset (WAV format)
        """
        if state.get('extend_request'):
            return self._execute_extension(state)
        elif state.get('fix_segments') and state.get('audio_url'):
            return self._execute_inpainting(state)
        else:
            return self._execute_generation(state)
    
    def _execute_generation(self, state: Dict[str, Any]) -> AgentResult:
        """Execute a new song generation via fal.ai."""
        self.logger.info("Triggering new generation via fal.ai...")
        
        try:
            request = self._build_generation_request(state)
            payload = request.to_fal_payload()
        except Exception as e:
            self.logger.error(f"Payload validation failed: {e}")
            return AgentResult.failure_result(
                errors=[f"Invalid generation payload: {str(e)}"]
            )
        
        api_key = self._get_api_key()
        
        if not api_key:
            self.logger.warning("No API key found, using simulated generation")
            return self._simulated_generation(state, payload)
        
        try:
            result = self._call_fal_api('generate', payload, api_key)
            
            audio_url = self._extract_audio_url(result)
            audio_path = self._download_audio(audio_url, output_format='wav')
            
            return AgentResult.success_result(
                state_updates={
                    'request_id': result.get('request_id'),
                    'task_id': result.get('request_id'),
                    'audio_url': audio_url,
                    'local_filepath': audio_path,
                    'seed': result.get('seed'),
                    'cost_usd': state.get('cost_usd', 0.0) + COST_PER_GENERATION_USD,
                    'iteration_count': state.get('iteration_count', 0) + 1,
                    'status': 'generated'
                },
                metadata={'api_response': result, 'payload': payload}
            )
            
        except Exception as e:
            self.logger.error(f"Generation failed: {e}")
            return AgentResult.failure_result(
                errors=[f"Generation failed: {str(e)}"]
            )
    
    def _execute_inpainting(self, state: Dict[str, Any]) -> AgentResult:
        """
        Execute surgical inpainting on specific segments.
        
        Reference: Design & Critique Section 5.2 - Structural Architect
        Critical: Uses [[start, end]] format, NOT [{start, end}]
        """
        self.logger.info(f"Triggering inpainting for segments: {state['fix_segments']}")
        
        try:
            request = self._build_inpaint_request(state)
            payload = request.to_fal_payload()
        except Exception as e:
            self.logger.error(f"Inpaint payload validation failed: {e}")
            return AgentResult.failure_result(
                errors=[f"Invalid inpaint payload: {str(e)}"]
            )
        
        api_key = self._get_api_key()
        
        if not api_key:
            self.logger.warning("No API key found, using simulated inpainting")
            return self._simulated_inpainting(state, payload)
        
        try:
            result = self._call_fal_api('inpaint', payload, api_key)
            
            audio_url = self._extract_audio_url(result)
            audio_path = self._download_audio(audio_url, output_format='wav')
            
            return AgentResult.success_result(
                state_updates={
                    'request_id': result.get('request_id'),
                    'task_id': result.get('request_id'),
                    'audio_url': audio_url,
                    'local_filepath': audio_path,
                    'fix_segments': [],
                    'cost_usd': state.get('cost_usd', 0.0) + COST_PER_INPAINT_USD,
                    'iteration_count': state.get('iteration_count', 0) + 1,
                    'status': 'inpainted'
                },
                metadata={'api_response': result, 'payload': payload}
            )
            
        except Exception as e:
            self.logger.error(f"Inpainting failed: {e}")
            return AgentResult.failure_result(
                errors=[f"Inpainting failed: {str(e)}"]
            )
    
    def _execute_extension(self, state: Dict[str, Any]) -> AgentResult:
        """
        Execute track extension via fal.ai.
        
        Reference: Design & Critique Section 6.2 - Extension Protocol
        Supports 'left' (prepend) and 'right' (append) with crop_duration
        """
        self.logger.info("Triggering extension via fal.ai...")
        
        try:
            request = self._build_extend_request(state)
            payload = request.to_fal_payload()
        except Exception as e:
            self.logger.error(f"Extension payload validation failed: {e}")
            return AgentResult.failure_result(
                errors=[f"Invalid extension payload: {str(e)}"]
            )
        
        api_key = self._get_api_key()
        
        if not api_key:
            self.logger.warning("No API key found, using simulated extension")
            return self._simulated_generation(state, payload)
        
        try:
            result = self._call_fal_api('extend', payload, api_key)
            
            audio_url = self._extract_audio_url(result)
            audio_path = self._download_audio(audio_url, output_format='wav')
            
            return AgentResult.success_result(
                state_updates={
                    'request_id': result.get('request_id'),
                    'audio_url': audio_url,
                    'local_filepath': audio_path,
                    'cost_usd': state.get('cost_usd', 0.0) + COST_PER_GENERATION_USD,
                    'iteration_count': state.get('iteration_count', 0) + 1,
                    'status': 'extended'
                },
                metadata={'api_response': result, 'payload': payload}
            )
            
        except Exception as e:
            self.logger.error(f"Extension failed: {e}")
            return AgentResult.failure_result(
                errors=[f"Extension failed: {str(e)}"]
            )
    
    def _build_generation_request(self, state: Dict[str, Any]) -> SonautoGenerationRequest:
        """
        Build validated generation request with Pydantic model.
        
        Includes:
        - Enhanced prompt with textural descriptors (NOT Black Magic tags)
        - Validated tags from Tag Explorer
        - Genre-appropriate CFG scale (prompt_strength)
        - balance_strength for vocal/instrumental mix
        """
        plan = state.get('structured_plan', {})
        
        prompt = self._construct_prompt(state)
        tags = self._select_validated_tags(plan, state)
        lyrics = state.get('lyrics_validated') or state.get('lyrics_draft', '')
        
        subgenre = plan.get('subgenre', 'default')
        prompt_strength = plan.get('prompt_strength') or GENRE_CFG_DEFAULTS.get(
            subgenre, GENRE_CFG_DEFAULTS['default']
        )
        
        return SonautoGenerationRequest(
            prompt=prompt,
            lyrics=lyrics if lyrics else None,
            tags=tags,
            prompt_strength=prompt_strength,
            balance_strength=plan.get('balance_strength', 0.75),
            bpm=plan.get('bpm', 'auto'),
            seed=state.get('seed'),
            num_songs=plan.get('num_songs', 1),
            output_format=OutputFormat.WAV,
            instrumental=plan.get('instrumental', False)
        )
    
    def _build_inpaint_request(self, state: Dict[str, Any]) -> SonautoInpaintRequest:
        """
        Build validated inpaint request with correct section format.
        
        Critical: sections are [[start, end]] tuples, NOT [{start, end}] objects
        Reference: Design & Critique Section 5.2
        """
        sections: List[Tuple[float, float]] = []
        for segment in state.get('fix_segments', []):
            if isinstance(segment, dict):
                sections.append((segment['start'], segment['end']))
            elif isinstance(segment, (list, tuple)):
                sections.append((segment[0], segment[1]))
        
        plan = state.get('structured_plan', {})
        tags = self._select_validated_tags(plan, state)
        
        return SonautoInpaintRequest(
            audio_url=state['audio_url'],
            sections=sections,
            lyrics=state.get('lyrics_validated', ''),
            tags=tags,
            prompt=state.get('inpaint_prompt', state.get('sonauto_prompt', '')),
            prompt_strength=plan.get('prompt_strength', 2.5),
            balance_strength=plan.get('balance_strength', 0.7),
            seed=state.get('inpaint_seed')
        )
    
    def _build_extend_request(self, state: Dict[str, Any]) -> SonautoExtendRequest:
        """Build validated extension request."""
        extend_config = state.get('extend_request', {})
        plan = state.get('structured_plan', {})
        tags = self._select_validated_tags(plan, state)
        
        return SonautoExtendRequest(
            audio_url=state['audio_url'],
            side=extend_config.get('side', 'right'),
            crop_duration=extend_config.get('crop_duration'),
            prompt=extend_config.get('prompt'),
            lyrics=extend_config.get('lyrics'),
            tags=tags,
            prompt_strength=plan.get('prompt_strength', 2.0),
            balance_strength=plan.get('balance_strength', 0.7),
            seed=extend_config.get('seed')
        )
    
    def _construct_prompt(self, state: Dict[str, Any]) -> str:
        """
        Construct optimized prompt for diffusion model.
        
        Uses textural descriptors (NOT "Black Magic" tags which are 
        autoregressive-model superstitions).
        Reference: Design & Critique Section 3.3
        """
        plan = state.get('structured_plan', {})
        base_prompt = state.get('sonauto_prompt') or state.get('user_prompt', '')
        
        components = [base_prompt]
        
        if plan.get('subgenre'):
            components.append(f"{plan['subgenre']} style")
            
        if plan.get('mood'):
            components.append(f"{plan['mood']} atmosphere")
            
        if plan.get('instrumentation'):
            instr = plan['instrumentation']
            if isinstance(instr, dict):
                primary = instr.get('primary', [])
                if primary:
                    components.append(f"featuring {', '.join(primary)}")
            elif isinstance(instr, list):
                components.append(f"with {', '.join(instr)}")
        
        if plan.get('vocal_texture'):
            components.append(f"{plan['vocal_texture']} vocal delivery")
        
        return '. '.join(filter(None, components))
    
    def _select_validated_tags(self, plan: Dict[str, Any], state: Dict[str, Any]) -> List[str]:
        """
        Select tags validated against Tag Explorer database.
        
        Tag order matters - anchor genre first, then subgenre, mood, era, production.
        Reference: Design & Critique Section 4.2 - Tag ordering
        """
        tags = []
        
        if plan.get('genre_tags'):
            tags.extend(plan['genre_tags'])
        else:
            tags.extend(['hip hop', 'rap'])
        
        if plan.get('subgenre'):
            tags.append(plan['subgenre'])
        
        if plan.get('mood'):
            tags.append(plan['mood'])
        
        if plan.get('era'):
            tags.append(plan['era'])
        
        if plan.get('production_tags'):
            tags.extend(plan['production_tags'])
        
        if plan.get('tags'):
            tags.extend(plan['tags'])
        
        seen = set()
        unique_tags = []
        for tag in tags:
            if tag.lower() not in seen:
                seen.add(tag.lower())
                unique_tags.append(tag)
        
        return unique_tags[:8]
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type((
            requests.exceptions.Timeout, 
            requests.exceptions.ConnectionError,
            RateLimitError
        )),
        reraise=True
    )
    def _call_fal_api(
        self, 
        endpoint_type: str, 
        payload: Dict[str, Any], 
        api_key: str,
        use_queue: bool = True
    ) -> Dict[str, Any]:
        """
        Call fal.ai API with enhanced retry logic.
        
        Handles 429 rate limits by parsing Retry-After header.
        Reference: Refactoring Plan Section 7.2
        """
        headers = self._get_auth_headers(api_key)
        endpoint = self.ENDPOINTS.get(endpoint_type, '/text-to-music')
        
        if use_queue:
            url = f'{self.FAL_QUEUE_URL}{endpoint}'
        else:
            url = f'{self.FAL_BASE_URL}{endpoint}'
        
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 429:
            retry_after = response.headers.get('Retry-After')
            retry_seconds = int(retry_after) if retry_after else 30
            self.logger.warning(f"Rate limited. Waiting {retry_seconds}s...")
            raise RateLimitError(retry_after=retry_seconds)
        
        response.raise_for_status()
        
        data = response.json()
        
        if use_queue and 'request_id' in data:
            return self._poll_for_completion(data['request_id'], api_key, endpoint_type)
        
        return data
    
    def _poll_for_completion(
        self, 
        request_id: str, 
        api_key: str,
        endpoint_type: str,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Poll fal.ai queue for completion.
        
        Reference: Refactoring Plan Section 5.1 - Generation takes 30-90 seconds
        """
        headers = self._get_auth_headers(api_key)
        endpoint = self.ENDPOINTS.get(endpoint_type, '/text-to-music')
        status_url = f'{self.FAL_QUEUE_URL}{endpoint}/requests/{request_id}/status'
        result_url = f'{self.FAL_QUEUE_URL}{endpoint}/requests/{request_id}'
        
        start_time = time.time()
        wait_time = 5
        
        while (time.time() - start_time) < timeout:
            response = requests.get(status_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            status_data = response.json()
            status = status_data.get('status', '').upper()
            
            if status in ('COMPLETED', 'OK'):
                result_response = requests.get(result_url, headers=headers, timeout=30)
                result_response.raise_for_status()
                result = result_response.json()
                result['request_id'] = request_id
                return result
                
            elif status == 'FAILED':
                error = status_data.get('error', 'Unknown error')
                raise RuntimeError(f"Generation failed: {error}")
            
            elif status == 'IN_QUEUE':
                position = status_data.get('queue_position', 'unknown')
                self.logger.info(f"In queue, position: {position}")
            
            time.sleep(wait_time)
            wait_time = min(wait_time + 2, 15)
        
        raise TimeoutError(f"Generation timed out after {timeout} seconds")
    
    def _extract_audio_url(self, result: Dict[str, Any]) -> str:
        """Extract audio URL from fal.ai response, handling num_songs > 1."""
        if 'audio' in result:
            audio_list = result['audio']
            if isinstance(audio_list, list) and audio_list:
                return audio_list[0].get('url', '')
            elif isinstance(audio_list, dict):
                return audio_list.get('url', '')
        
        if 'audio_url' in result:
            return result['audio_url']
        
        if 'song_paths' in result:
            paths = result['song_paths']
            if paths:
                return paths[0]
        
        return ''
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((
            requests.exceptions.Timeout, 
            requests.exceptions.ConnectionError
        )),
        reraise=True
    )
    def _download_audio(self, url: str, output_format: str = 'wav') -> str:
        """
        Download audio from fal.ai CDN.
        
        Reference: Design & Critique Section 4.2 - WAV required for stem analysis
        """
        if not url:
            return ''
        
        os.makedirs('./output', exist_ok=True)
        local_path = f'./output/generated_{int(time.time())}.{output_format}'
        
        response = requests.get(url, stream=True, timeout=120)
        response.raise_for_status()
        
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        return local_path
    
    def _simulated_generation(self, state: Dict[str, Any], payload: Dict[str, Any]) -> AgentResult:
        """Simulated generation for development without API key."""
        import random
        
        self.logger.info("Simulating generation (no API key)")
        
        time.sleep(0.5)
        
        request_id = f"sim_{int(time.time())}_{random.randint(1000, 9999)}"
        
        os.makedirs('./output', exist_ok=True)
        local_path = f'./output/simulated_{request_id}.wav'
        
        with open(local_path, 'w') as f:
            f.write(f"# Simulated audio file (WAV)\n# Payload: {json.dumps(payload, indent=2)}")
        
        return AgentResult.success_result(
            state_updates={
                'request_id': request_id,
                'task_id': request_id,
                'audio_url': f'https://simulated.fal.ai/{request_id}.wav',
                'local_filepath': local_path,
                'seed': random.randint(1, 1000000),
                'cost_usd': state.get('cost_usd', 0.0) + COST_PER_GENERATION_USD,
                'iteration_count': state.get('iteration_count', 0) + 1,
                'status': 'simulated_generation'
            },
            warnings=['Using simulated generation (no API key)'],
            metadata={'payload': payload, 'simulated': True}
        )
    
    def _simulated_inpainting(self, state: Dict[str, Any], payload: Dict[str, Any]) -> AgentResult:
        """Simulated inpainting for development."""
        import random
        
        self.logger.info("Simulating inpainting (no API key)")
        
        time.sleep(0.3)
        
        request_id = f"sim_inpaint_{int(time.time())}_{random.randint(1000, 9999)}"
        
        return AgentResult.success_result(
            state_updates={
                'request_id': request_id,
                'task_id': request_id,
                'audio_url': state.get('audio_url', ''),
                'local_filepath': state.get('local_filepath', ''),
                'fix_segments': [],
                'cost_usd': state.get('cost_usd', 0.0) + COST_PER_INPAINT_USD,
                'iteration_count': state.get('iteration_count', 0) + 1,
                'status': 'simulated_inpainting'
            },
            warnings=['Using simulated inpainting (no API key)'],
            metadata={'payload': payload, 'simulated': True}
        )
    
    @staticmethod
    def verify_webhook_signature(
        request_body: bytes,
        signature: str,
        timestamp: str,
        request_id: str,
        secret_key: str
    ) -> bool:
        """
        Verify fal.ai webhook signature for security.
        
        Reference: Refactoring Plan Section 5.3 - Webhook Verification
        
        Steps:
        1. Check timestamp is within 5 minutes (prevent replay attacks)
        2. Construct string: request_id + timestamp + body
        3. Compute HMAC-SHA256 with secret
        4. Compare with provided signature
        """
        try:
            ts = int(timestamp)
            now = int(time.time())
            if abs(now - ts) > 300:
                return False
        except (ValueError, TypeError):
            return False
        
        message = f"{request_id}{timestamp}{request_body.decode('utf-8')}"
        expected = hmac.new(
            secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected, signature)
