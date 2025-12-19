"""
Payload Factory for Fal.ai MiniMax Music v2.

Uses GPT-4o to intelligently translate UI fields into Fal.ai payload format,
implementing the Split Rule, Translation Rule, and Reference Rule.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

PAYLOAD_SYSTEM_PROMPT = """You are a Music Theory API Bridge. Transform user input into a Fal.ai MiniMax Music v2 payload.

## Input Fields
1. description: Texture, atmosphere, instrumentation
2. lyrics: Song lyrics with structure
3. neuro_effects: Neuropsychological effects (frisson, tension, release)
4. neurochemical_targets: Dopamine, serotonin, adrenaline targets
5. musical_effects: Production effects (can be Timbral OR Structural)

## Output Fields
1. prompt: Style/acoustic descriptors (max 300 chars, NO structural tags)
2. lyrics_prompt: Structured lyrics with ## tags ## for instrumental events (max 3000 chars)

## The Split Rule for Musical Effects
Analyze each effect and categorize:

TIMBRAL/GLOBAL → Goes to prompt:
- Lo-fi, Reverb, Dark Mix, Distortion, Wide Stereo, Warm, Crisp, Heavy Bass

STRUCTURAL/EVENT → Goes to lyrics_prompt as ## Tag ##:
- Guitar Solo, Drop, Silence, Break, Bass Drop, Drum Fill

## The Translation Rule

Neuropsychological Effects → Acoustic Descriptors:
- Frisson → "soaring dynamics, sudden crescendo"
- Tension → "building intensity, rising pitch"
- Release → "harmonic resolution, dynamic drop"

Neurochemical Targets → Rhythmic Descriptors:
- Dopamine → "catchy hooks, syncopated bass"
- Serotonin → "warm tones, steady rhythm"
- Adrenaline → "fast tempo, aggressive drums"

## Output Format
Return ONLY valid JSON:
{
  "prompt": "Genre, mood, translated effects (max 300 chars)",
  "lyrics_prompt": "[Verse]\\nLyrics...\\n\\n## Effect ##\\n\\n[Chorus]\\nMore lyrics..."
}

## CRITICAL RULES
1. NEVER put [Verse]/[Chorus] in prompt
2. ALWAYS use ## Tag ## for instrumental events in lyrics_prompt
3. Keep prompt under 300 characters
4. Ensure \\n\\n before/after each section tag in lyrics_prompt
5. If no lyrics provided, create minimal structure with ## Instrumental ## sections"""


class PayloadFactory:
    """
    Factory for building Fal.ai payloads from UI data.
    
    Uses GPT-4o to intelligently merge and translate fields.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the payload factory.
        
        Args:
            openai_api_key: OpenAI API key. Reads from OPENAI_API_KEY if not provided.
        """
        self.api_key = openai_api_key or os.environ.get('OPENAI_API_KEY')
        self.model = "gpt-4o"
        self.simulation_mode = not self.api_key
        
        if self.simulation_mode:
            logger.warning("No OPENAI_API_KEY found. PayloadFactory in simulation mode.")
    
    def construct_payload(self, ui_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Construct a Fal.ai payload from UI data using GPT-4o.
        
        Args:
            ui_data: Dictionary containing UI field values:
                - description: Prompt/description text
                - lyrics: Lyrics text
                - neuro_effects: Neuropsychological effects
                - neurochemical_targets: Neurochemical targets
                - musical_effects: Musical/production effects
                - seed_composition: Optional reference audio URL
                
        Returns:
            Fal.ai payload dict ready for submission.
        """
        if self.simulation_mode:
            return self._simulate_payload(ui_data)
        
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            
            user_prompt = self._build_user_prompt(ui_data)
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": PAYLOAD_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            prompt = result.get('prompt', '')[:300]
            lyrics_prompt = result.get('lyrics_prompt', '')[:3000]
            
            payload = {
                "input": {
                    "prompt": prompt,
                    "lyrics_prompt": lyrics_prompt,
                    "audio_setting": {
                        "sample_rate": "44100",
                        "bitrate": "256000",
                        "format": "mp3"
                    }
                }
            }
            
            seed_url = ui_data.get('seed_composition', '').strip()
            if seed_url and seed_url.startswith('http'):
                payload["input"]["reference_audio_url"] = seed_url
            
            return payload
            
        except Exception as e:
            logger.error(f"GPT-4o payload construction failed: {e}")
            return self._fallback_payload(ui_data)
    
    def _build_user_prompt(self, ui_data: Dict[str, Any]) -> str:
        """Build the user prompt for GPT-4o."""
        return f"""Transform this UI data into a Fal.ai payload:

DESCRIPTION: {ui_data.get('description', '')}

LYRICS: {ui_data.get('lyrics', '')}

NEUROPSYCHOLOGICAL EFFECTS: {ui_data.get('neuro_effects', '')}

NEUROCHEMICAL TARGETS: {ui_data.get('neurochemical_targets', '')}

MUSICAL EFFECTS: {ui_data.get('musical_effects', '')}

Return the JSON payload with "prompt" and "lyrics_prompt" fields."""
    
    def _simulate_payload(self, ui_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a simulated payload without API call."""
        description = ui_data.get('description', 'Aggressive trap, heavy 808s')
        lyrics = ui_data.get('lyrics', '[Verse]\nSimulated lyrics here\n\n[Chorus]\nHook line')
        neuro = ui_data.get('neuro_effects', '')
        chem = ui_data.get('neurochemical_targets', '')
        effects = ui_data.get('musical_effects', '')
        
        prompt_parts = [description[:150]]
        if neuro:
            prompt_parts.append(neuro[:50])
        if chem:
            prompt_parts.append(chem[:50])
        
        timbral_effects = []
        structural_effects = []
        
        if effects:
            for effect in effects.split(','):
                effect = effect.strip()
                if any(s in effect.lower() for s in ['solo', 'drop', 'break', 'silence', 'fill']):
                    structural_effects.append(effect)
                else:
                    timbral_effects.append(effect)
        
        if timbral_effects:
            prompt_parts.append(', '.join(timbral_effects[:3]))
        
        prompt = ', '.join(prompt_parts)[:300]
        
        lyrics_prompt = lyrics or '[Verse]\nInstrumental verse\n\n[Chorus]\nInstrumental hook'
        
        for struct in structural_effects:
            lyrics_prompt += f"\n\n## {struct} ##"
        
        payload = {
            "input": {
                "prompt": prompt,
                "lyrics_prompt": lyrics_prompt[:3000],
                "audio_setting": {
                    "sample_rate": "44100",
                    "bitrate": "256000",
                    "format": "mp3"
                }
            }
        }
        
        seed_url = ui_data.get('seed_composition', '').strip()
        if seed_url and seed_url.startswith('http'):
            payload["input"]["reference_audio_url"] = seed_url
        
        logger.info(f"[SIMULATION] Generated payload: prompt={len(prompt)} chars, lyrics={len(lyrics_prompt)} chars")
        return payload
    
    def _fallback_payload(self, ui_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback payload construction without GPT-4o."""
        return self._simulate_payload(ui_data)


def construct_payload_with_gpt(ui_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to construct payload using GPT-4o.
    
    Args:
        ui_data: UI field data dictionary.
        
    Returns:
        Fal.ai payload dict.
    """
    factory = PayloadFactory()
    return factory.construct_payload(ui_data)
