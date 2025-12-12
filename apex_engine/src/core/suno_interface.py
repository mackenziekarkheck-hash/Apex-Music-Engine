"""
Sonauto Interface - Direct Sonauto API Client for Audio Generation.

This module provides the Neo-Apex interface to Sonauto API directly:
- Song generation with CFG scale control (prompt_strength)
- Inpainting with correct section format
- Extension with side and crop_duration parameters
- Uses standard requests library for REST API calls

Architecture: Uses direct REST API calls (requests library)
Reference: Sonauto API Refactoring Plan, Neo-Apex Architecture Documentation
"""

from typing import Dict, Any, List, Optional, Union, Tuple
import os
import time
import json
import hashlib
import hmac
import logging
import requests

from ..agents.agent_base import GenerativeAgent, AgentRole, AgentResult
from .fal_models import (
    SonautoGenerationRequest,
    SonautoInpaintRequest,
    SonautoExtendRequest,
    SonautoModel,
    OutputFormat,
    GENRE_CFG_DEFAULTS,
    COST_PER_GENERATION_USD,
    COST_PER_INPAINT_USD,
    COST_PER_EXTEND_USD,
    validate_tags_o1
)

logger = logging.getLogger(__name__)

SONAUTO_API_BASE = "https://api.sonauto.ai/v1"
SONAUTO_API_AVAILABLE = True


class SonautoOperator(GenerativeAgent):
    """
    Sonauto Operator: Neo-Apex bridge to the Sonauto API.
    
    Uses direct REST API calls for:
    - Song generation with CFG scale control
    - Inpainting for surgical audio fixes
    - Track extension
    - USD cost tracking (Shadow Ledger compatible)
    
    Reference: 
    - Sonauto API Refactoring Plan Section 2.2 "Canonical Endpoint Decision"
    - Sonauto API Design & Critique Section 4.1 "God-Mode Payload"
    """
    
    @property
    def role(self) -> AgentRole:
        return AgentRole.SONAUTO_OPERATOR
    
    def _get_api_key(self) -> Optional[str]:
        """Get Sonauto API key from environment."""
        return os.environ.get('SONAUTO_API_KEY')
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for Sonauto API requests."""
        api_key = self._get_api_key()
        return {
            'Authorization': f'Bearer {api_key}' if api_key else '',
            'Content-Type': 'application/json'
        }
    
    def _has_api_key(self) -> bool:
        """Check if Sonauto API key is configured."""
        return bool(self._get_api_key())
    
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
        3. Submit request via fal_client SDK
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
        """Execute a new song generation via Sonauto API."""
        self.logger.info("Triggering new generation via Sonauto API...")
        
        try:
            request = self._build_generation_request(state)
            payload = request.to_sonauto_payload()
            estimated_cost = request.estimate_cost()
        except Exception as e:
            self.logger.error(f"Payload validation failed: {e}")
            return AgentResult.failure_result(
                errors=[f"Invalid generation payload: {str(e)}"]
            )
        
        if not self._has_api_key():
            self.logger.warning("No API key found, using simulated generation")
            return self._simulated_generation(state, payload, estimated_cost)
        
        try:
            result = self._call_sonauto_api(SonautoModel.TEXT_TO_MUSIC, payload)
            
            audio_url = self._extract_audio_url(result)
            audio_path = self._download_audio(audio_url, output_format='wav')
            
            return AgentResult.success_result(
                state_updates={
                    'request_id': result.get('request_id', ''),
                    'task_id': result.get('request_id', ''),
                    'audio_url': audio_url,
                    'local_filepath': audio_path,
                    'seed': result.get('seed'),
                    'cost_usd': state.get('cost_usd', 0.0) + estimated_cost,
                    'iteration_count': state.get('iteration_count', 0) + 1,
                    'status': 'generated'
                },
                metadata={
                    'api_response': result, 
                    'payload': payload,
                    'estimated_cost': estimated_cost
                }
            )
            
        except Exception as e:
            self.logger.error(f"Generation failed: {e}")
            return AgentResult.failure_result(
                errors=[f"Generation failed: {str(e)}"]
            )
    
    def _execute_inpainting(self, state: Dict[str, Any]) -> AgentResult:
        """Execute surgical inpainting on specific segments."""
        self.logger.info(f"Triggering inpainting for segments: {state['fix_segments']}")
        
        try:
            request = self._build_inpaint_request(state)
            payload = request.to_sonauto_payload()
            estimated_cost = request.estimate_cost()
        except Exception as e:
            self.logger.error(f"Inpaint payload validation failed: {e}")
            return AgentResult.failure_result(
                errors=[f"Invalid inpaint payload: {str(e)}"]
            )
        
        if not self._has_api_key():
            self.logger.warning("No API key found, using simulated inpainting")
            return self._simulated_inpainting(state, payload, estimated_cost)
        
        try:
            result = self._call_sonauto_api(SonautoModel.INPAINT, payload)
            
            audio_url = self._extract_audio_url(result)
            audio_path = self._download_audio(audio_url, output_format='wav')
            
            return AgentResult.success_result(
                state_updates={
                    'request_id': result.get('request_id', ''),
                    'task_id': result.get('request_id', ''),
                    'audio_url': audio_url,
                    'local_filepath': audio_path,
                    'fix_segments': [],
                    'cost_usd': state.get('cost_usd', 0.0) + estimated_cost,
                    'iteration_count': state.get('iteration_count', 0) + 1,
                    'status': 'inpainted'
                },
                metadata={
                    'api_response': result, 
                    'payload': payload,
                    'estimated_cost': estimated_cost
                }
            )
            
        except Exception as e:
            self.logger.error(f"Inpainting failed: {e}")
            return AgentResult.failure_result(
                errors=[f"Inpainting failed: {str(e)}"]
            )
    
    def _execute_extension(self, state: Dict[str, Any]) -> AgentResult:
        """Execute track extension via Sonauto API."""
        self.logger.info("Triggering extension via Sonauto API...")
        
        try:
            request = self._build_extend_request(state)
            payload = request.to_sonauto_payload()
            estimated_cost = request.estimate_cost()
        except Exception as e:
            self.logger.error(f"Extension payload validation failed: {e}")
            return AgentResult.failure_result(
                errors=[f"Invalid extension payload: {str(e)}"]
            )
        
        if not self._has_api_key():
            self.logger.warning("No API key found, using simulated extension")
            return self._simulated_generation(state, payload, estimated_cost)
        
        try:
            result = self._call_sonauto_api(SonautoModel.EXTEND, payload)
            
            audio_url = self._extract_audio_url(result)
            audio_path = self._download_audio(audio_url, output_format='wav')
            
            return AgentResult.success_result(
                state_updates={
                    'request_id': result.get('request_id', ''),
                    'audio_url': audio_url,
                    'local_filepath': audio_path,
                    'cost_usd': state.get('cost_usd', 0.0) + estimated_cost,
                    'iteration_count': state.get('iteration_count', 0) + 1,
                    'status': 'extended'
                },
                metadata={
                    'api_response': result, 
                    'payload': payload,
                    'estimated_cost': estimated_cost
                }
            )
            
        except Exception as e:
            self.logger.error(f"Extension failed: {e}")
            return AgentResult.failure_result(
                errors=[f"Extension failed: {str(e)}"]
            )
    
    def _call_sonauto_api(self, model: SonautoModel, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call Sonauto API directly using requests library.
        
        Args:
            model: SonautoModel enum for the endpoint
            payload: Request payload
            
        Returns:
            API response as dict
        """
        endpoint = model.value
        url = f"{SONAUTO_API_BASE}/{endpoint}"
        
        self.logger.info(f"Calling Sonauto API: {endpoint}")
        
        response = requests.post(
            url,
            headers=self._get_headers(),
            json=payload,
            timeout=300
        )
        
        if response.status_code != 200:
            error_msg = f"Sonauto API error: {response.status_code} - {response.text}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
        
        return response.json()
    
    def _build_generation_request(self, state: Dict[str, Any]) -> SonautoGenerationRequest:
        """Build validated generation request with Pydantic model."""
        plan = state.get('structured_plan', {})
        
        prompt = self._construct_prompt(state)
        tags = self._select_validated_tags(plan, state)
        lyrics = state.get('lyrics_validated') or state.get('lyrics_draft', '')
        
        subgenre = plan.get('subgenre', 'default')
        prompt_strength = plan.get('prompt_strength') or GENRE_CFG_DEFAULTS.get(
            subgenre, GENRE_CFG_DEFAULTS.get(subgenre.replace(' ', '_'), GENRE_CFG_DEFAULTS['default'])
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
        """Build validated inpaint request."""
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
            seed=state.get('inpaint_seed'),
            selection_crop=False
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
        """Construct optimized prompt for diffusion model."""
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
        """Select tags validated against Tag Explorer database."""
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
            normalized = tag.lower().strip()
            if normalized not in seen:
                seen.add(normalized)
                unique_tags.append(normalized)
        
        return unique_tags[:8]
    
    def _extract_audio_url(self, result: Dict[str, Any]) -> str:
        """Extract audio URL from fal_client response."""
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
    
    def _download_audio(self, url: str, output_format: str = 'wav') -> str:
        """Download audio from fal.ai CDN."""
        if not url:
            return ''
        
        import requests
        
        os.makedirs('./output', exist_ok=True)
        local_path = f'./output/generated_{int(time.time())}.{output_format}'
        
        response = requests.get(url, stream=True, timeout=120)
        response.raise_for_status()
        
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        return local_path
    
    def _simulated_generation(
        self, 
        state: Dict[str, Any], 
        payload: Dict[str, Any],
        estimated_cost: float
    ) -> AgentResult:
        """Simulated generation for development without API key."""
        import random
        
        self.logger.info("Simulating generation (no API key)")
        
        time.sleep(0.5)
        
        request_id = f"sim_{int(time.time())}_{random.randint(1000, 9999)}"
        
        os.makedirs('./output', exist_ok=True)
        local_path = f'./output/simulated_{request_id}.wav'
        
        self._write_simulated_wav(local_path, payload)
        
        return AgentResult.success_result(
            state_updates={
                'request_id': request_id,
                'task_id': request_id,
                'audio_url': f'https://simulated.fal.ai/{request_id}.wav',
                'local_filepath': local_path,
                'seed': random.randint(1, 1000000),
                'cost_usd': state.get('cost_usd', 0.0) + estimated_cost,
                'iteration_count': state.get('iteration_count', 0) + 1,
                'status': 'simulated_generation'
            },
            warnings=['Using simulated generation (no API key)'],
            metadata={
                'payload': payload, 
                'simulated': True,
                'estimated_cost': estimated_cost
            }
        )
    
    def _simulated_inpainting(
        self, 
        state: Dict[str, Any], 
        payload: Dict[str, Any],
        estimated_cost: float
    ) -> AgentResult:
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
                'cost_usd': state.get('cost_usd', 0.0) + estimated_cost,
                'iteration_count': state.get('iteration_count', 0) + 1,
                'status': 'simulated_inpainting'
            },
            warnings=['Using simulated inpainting (no API key)'],
            metadata={
                'payload': payload, 
                'simulated': True,
                'estimated_cost': estimated_cost
            }
        )
    
    def _write_simulated_wav(self, filepath: str, payload: Dict[str, Any]) -> None:
        """Write a minimal valid WAV file for simulation."""
        import struct
        
        sample_rate = 44100
        duration = 1.0
        num_samples = int(sample_rate * duration)
        
        with open(filepath, 'wb') as f:
            f.write(b'RIFF')
            f.write(struct.pack('<I', 36 + num_samples * 2))
            f.write(b'WAVE')
            
            f.write(b'fmt ')
            f.write(struct.pack('<I', 16))
            f.write(struct.pack('<H', 1))
            f.write(struct.pack('<H', 1))
            f.write(struct.pack('<I', sample_rate))
            f.write(struct.pack('<I', sample_rate * 2))
            f.write(struct.pack('<H', 2))
            f.write(struct.pack('<H', 16))
            
            f.write(b'data')
            f.write(struct.pack('<I', num_samples * 2))
            
            for i in range(num_samples):
                sample = int(32767 * 0.1 * (i % 100) / 100)
                f.write(struct.pack('<h', sample))
    
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
