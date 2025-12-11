"""
Sonauto Interface - API Client for Audio Generation.

This module provides the interface to the Sonauto API for:
- Song generation from prompts and lyrics
- Inpainting (surgical section regeneration)
- Status polling and asset retrieval
- "Black Magic" tag injection for quality optimization

Reference: Section 3.2 "The Sonauto Operator" from framework documentation
"""

from typing import Dict, Any, List, Optional
import os
import time
import json

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import requests

from ..agents.agent_base import GenerativeAgent, AgentRole, AgentResult


def _is_retryable_error(exception: Exception) -> bool:
    """Check if an exception should trigger a retry."""
    if isinstance(exception, requests.exceptions.Timeout):
        return True
    if isinstance(exception, requests.exceptions.ConnectionError):
        return True
    if isinstance(exception, requests.exceptions.HTTPError):
        if hasattr(exception, 'response') and exception.response is not None:
            return exception.response.status_code in (429, 500, 502, 503, 504)
    return False


class SonautoOperator(GenerativeAgent):
    """
    Sonauto Operator: The bridge to the generative engine.
    
    This agent manages all Sonauto API interactions:
    - Authentication and request signing
    - Payload construction with optimized prompts
    - Generation and inpainting requests
    - Polling for completion and asset retrieval
    
    Reference: Sonauto API documentation
    """
    
    BASE_URL = "https://api.sonauto.ai/v1"
    
    BLACK_MAGIC_TAGS = [
        "high fidelity", "studio quality", "mixed vocals",
        "professional production", "clear vocals"
    ]
    
    RAP_TAG_TAXONOMY = {
        'core': ['rap', 'hip hop'],
        'subgenre': ['trap', 'drill', 'boom bap', 'pop rap', 'cloud rap'],
        'era': ['90s', '2000s', 'old school', 'modern'],
        'mood': ['aggressive', 'chill', 'dark', 'energetic', 'emotional'],
        'instrumentation': ['piano', 'guitar', 'synth', '808', 'sample']
    }
    
    @property
    def role(self) -> AgentRole:
        return AgentRole.SONAUTO_OPERATOR
    
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
        Execute Sonauto generation or inpainting.
        
        Flow:
        1. Check if this is a new generation or inpainting
        2. Construct optimized payload
        3. Submit request to API
        4. Poll for completion
        5. Download and store audio asset
        """
        if state.get('fix_segments') and state.get('audio_url'):
            return self._execute_inpainting(state)
        else:
            return self._execute_generation(state)
    
    def _execute_generation(self, state: Dict[str, Any]) -> AgentResult:
        """Execute a new song generation."""
        self.logger.info("Triggering new generation...")
        
        payload = self._construct_generation_payload(state)
        
        api_key = os.environ.get('SONAUTO_API_KEY')
        
        if not api_key:
            self.logger.warning("No API key found, using simulated generation")
            return self._simulated_generation(state, payload)
        
        try:
            result = self._call_generation_api(payload, api_key)
            
            audio_path = self._download_audio(result['audio_url'])
            
            return AgentResult.success_result(
                state_updates={
                    'task_id': result['task_id'],
                    'audio_url': result['audio_url'],
                    'local_filepath': audio_path,
                    'seed': result.get('seed'),
                    'credits_used': state.get('credits_used', 0) + 100,
                    'iteration_count': state.get('iteration_count', 0) + 1,
                    'status': 'generated'
                },
                metadata={'api_response': result}
            )
            
        except Exception as e:
            self.logger.error(f"Generation failed: {e}")
            return AgentResult.failure_result(
                errors=[f"Generation failed: {str(e)}"]
            )
    
    def _execute_inpainting(self, state: Dict[str, Any]) -> AgentResult:
        """Execute surgical inpainting on specific segments."""
        self.logger.info(f"Triggering inpainting for segments: {state['fix_segments']}")
        
        payload = self._construct_inpainting_payload(state)
        
        api_key = os.environ.get('SONAUTO_API_KEY')
        
        if not api_key:
            self.logger.warning("No API key found, using simulated inpainting")
            return self._simulated_inpainting(state, payload)
        
        try:
            result = self._call_inpainting_api(payload, api_key)
            
            audio_path = self._download_audio(result['audio_url'])
            
            return AgentResult.success_result(
                state_updates={
                    'task_id': result['task_id'],
                    'audio_url': result['audio_url'],
                    'local_filepath': audio_path,
                    'fix_segments': [],
                    'credits_used': state.get('credits_used', 0) + 50,
                    'iteration_count': state.get('iteration_count', 0) + 1,
                    'status': 'inpainted'
                },
                metadata={'api_response': result}
            )
            
        except Exception as e:
            self.logger.error(f"Inpainting failed: {e}")
            return AgentResult.failure_result(
                errors=[f"Inpainting failed: {str(e)}"]
            )
    
    def _construct_generation_payload(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Construct optimized payload for generation.
        
        Includes:
        - Enhanced prompt with acoustic descriptors
        - Validated lyrics with structure tags
        - Optimized tag selection
        - Balance and strength parameters
        """
        plan = state.get('structured_plan', {})
        
        prompt = self._construct_prompt(state)
        
        tags = self._select_tags(plan)
        
        lyrics = state.get('lyrics_validated') or state.get('lyrics_draft', '')
        
        payload = {
            'prompt': prompt,
            'lyrics': lyrics,
            'tags': tags,
            'instrumental': plan.get('instrumental', False),
            'balance_strength': plan.get('balance_strength', 0.75),
            'num_songs': 2
        }
        
        if plan.get('bpm'):
            payload['bpm'] = plan['bpm']
            
        if state.get('seed'):
            payload['seed'] = state['seed']
            
        return payload
    
    def _construct_inpainting_payload(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Construct payload for inpainting request."""
        sections = []
        for segment in state.get('fix_segments', []):
            sections.append({
                'start': segment['start'],
                'end': segment['end']
            })
        
        return {
            'audio_url': state['audio_url'],
            'sections': sections,
            'prompt': state.get('sonauto_prompt', ''),
            'lyrics': state.get('lyrics_validated', ''),
            'instrumental': False
        }
    
    def _construct_prompt(self, state: Dict[str, Any]) -> str:
        """
        Construct an optimized prompt for generation.
        
        Combines user intent with "Black Magic" descriptors
        known to improve output quality.
        """
        plan = state.get('structured_plan', {})
        base_prompt = state.get('sonauto_prompt') or state.get('user_prompt', '')
        
        components = [base_prompt]
        
        if plan.get('subgenre'):
            components.append(f"{plan['subgenre']} style")
            
        if plan.get('mood'):
            components.append(f"{plan['mood']} atmosphere")
            
        if plan.get('instrumentation'):
            components.append(f"with {', '.join(plan['instrumentation'])}")
        
        components.extend(self.BLACK_MAGIC_TAGS[:2])
        
        return '. '.join(filter(None, components))
    
    def _select_tags(self, plan: Dict[str, Any]) -> List[str]:
        """
        Select optimal tags from the taxonomy.
        
        Prioritizes:
        1. Core genre tags (always include)
        2. Subgenre (from plan)
        3. Mood tags
        4. Era if specified
        """
        tags = list(self.RAP_TAG_TAXONOMY['core'])
        
        if plan.get('subgenre') and plan['subgenre'] in self.RAP_TAG_TAXONOMY['subgenre']:
            tags.append(plan['subgenre'])
        else:
            tags.append('trap')
            
        if plan.get('mood') and plan['mood'] in self.RAP_TAG_TAXONOMY['mood']:
            tags.append(plan['mood'])
            
        if plan.get('era') and plan['era'] in self.RAP_TAG_TAXONOMY['era']:
            tags.append(plan['era'])
        
        return tags[:5]
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((requests.exceptions.Timeout, requests.exceptions.ConnectionError)),
        reraise=True
    )
    def _call_generation_api(self, payload: Dict[str, Any], api_key: str) -> Dict[str, Any]:
        """Call the Sonauto generation API with retry logic."""
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f'{self.BASE_URL}/generations',
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        task_id = response.json().get('id') or response.json().get('task_id')
        
        return self._poll_for_completion(task_id, api_key)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((requests.exceptions.Timeout, requests.exceptions.ConnectionError)),
        reraise=True
    )
    def _call_inpainting_api(self, payload: Dict[str, Any], api_key: str) -> Dict[str, Any]:
        """Call the Sonauto inpainting API with retry logic."""
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f'{self.BASE_URL}/generations/inpaint',
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        task_id = response.json().get('id') or response.json().get('task_id')
        
        return self._poll_for_completion(task_id, api_key)
    
    def _poll_for_completion(self, task_id: str, api_key: str, timeout: int = 300) -> Dict[str, Any]:
        """Poll the API until generation completes."""
        import requests
        
        headers = {'Authorization': f'Bearer {api_key}'}
        url = f'{self.BASE_URL}/generations/{task_id}'
        
        start_time = time.time()
        wait_time = 5
        
        while (time.time() - start_time) < timeout:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            status = data.get('status', '').upper()
            
            if status in ('COMPLETED', 'SUCCESS'):
                return {
                    'task_id': task_id,
                    'audio_url': data.get('song_paths', [None])[0],
                    'status': status,
                    'seed': data.get('seed')
                }
            elif status in ('FAILED', 'FAILURE'):
                raise RuntimeError(f"Generation failed: {data.get('error_message', 'Unknown error')}")
            
            time.sleep(wait_time)
            wait_time = min(wait_time + 2, 15)
        
        raise TimeoutError(f"Generation timed out after {timeout} seconds")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((requests.exceptions.Timeout, requests.exceptions.ConnectionError)),
        reraise=True
    )
    def _download_audio(self, url: str) -> str:
        """Download audio from URL to local filesystem with retry logic."""
        if not url:
            return ''
        
        os.makedirs('./output', exist_ok=True)
        local_path = f'./output/generated_{int(time.time())}.ogg'
        
        response = requests.get(url, stream=True, timeout=60)
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
        
        task_id = f"sim_{int(time.time())}_{random.randint(1000, 9999)}"
        
        os.makedirs('./output', exist_ok=True)
        local_path = f'./output/simulated_{task_id}.ogg'
        
        with open(local_path, 'w') as f:
            f.write(f"# Simulated audio file\n# Payload: {json.dumps(payload, indent=2)}")
        
        return AgentResult.success_result(
            state_updates={
                'task_id': task_id,
                'audio_url': f'https://simulated.example.com/{task_id}.ogg',
                'local_filepath': local_path,
                'seed': random.randint(1, 1000000),
                'credits_used': state.get('credits_used', 0) + 100,
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
        
        task_id = f"sim_inpaint_{int(time.time())}_{random.randint(1000, 9999)}"
        
        return AgentResult.success_result(
            state_updates={
                'task_id': task_id,
                'audio_url': state.get('audio_url', ''),
                'local_filepath': state.get('local_filepath', ''),
                'fix_segments': [],
                'credits_used': state.get('credits_used', 0) + 50,
                'iteration_count': state.get('iteration_count', 0) + 1,
                'status': 'simulated_inpainting'
            },
            warnings=['Using simulated inpainting (no API key)'],
            metadata={'payload': payload, 'simulated': True}
        )
