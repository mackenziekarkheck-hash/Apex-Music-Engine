"""
Field Optimizer Service for APEX Engine.

Uses GPT-4o to optimize individual UI fields based on context files.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

CONTEXT_DIR = Path(__file__).parent.parent.parent / "context"

FIELD_CONTEXT_MAPPING = {
    "prompt_text": "prompt_analyzer.md",
    "description": "prompt_analyzer.md",
    "lyrics_text": "lyrics_validator.md",
    "lyrics": "lyrics_validator.md",
    "neuro_effects": "neurochemical_translator.md",
    "neurochemical_effects": "neurochemical_translator.md",
    "neurochemical_targets": "neurochemical_translator.md",
    "musical_effects": "prompt_analyzer.md",
}

OPTIMIZATION_PROMPTS = {
    "prompt_text": """You are optimizing a music style prompt for MiniMax Music v2.
The prompt should be:
- Under 300 characters
- Dense with descriptors (genre, mood, instrumentation, timbre)
- No filler words ("make a", "generate", "song about")
- No structural tags ([Verse], [Chorus])

Current text: {text}

Return ONLY the optimized text, nothing else.""",

    "lyrics_text": """You are optimizing song lyrics for MiniMax Music v2.
The lyrics should:
- Have [Verse] and [Chorus] structure tags
- Use ## Tag ## for instrumental events (not brackets)
- Have proper line breaks for phrasing
- Have \\n\\n between sections

Current text: {text}

Return ONLY the optimized lyrics, nothing else.""",

    "neuro_effects": """You are a music psychologist. Translate these neuropsychological effect descriptions into concrete musical descriptors.

Translate concepts like:
- Frisson → "soaring dynamics, sudden crescendo"
- Tension → "building intensity, rising pitch"
- Release → "harmonic resolution, dynamic drop"

Current text: {text}

Return the musical descriptors that would achieve these effects. Be concise and specific.""",

    "neurochemical_effects": """You are a music psychologist. Translate these neurochemical targets into rhythmic/melodic descriptors.

Translate concepts like:
- Dopamine → "catchy hooks, syncopated bass, repetitive patterns"
- Serotonin → "warm tones, steady rhythm, major progressions"
- Adrenaline → "fast tempo, aggressive drums, distorted bass"

Current text: {text}

Return the musical descriptors that would trigger these neurochemicals. Be concise and specific.""",

    "musical_effects": """You are optimizing musical effect descriptions for MiniMax Music v2.

Separate effects into:
1. TIMBRAL (for style prompt): Lo-fi, Reverb, Dark, Wide Stereo, Heavy Bass
2. STRUCTURAL (for lyrics as ## Tag ##): Guitar Solo, Drop, Break, Silence

Current text: {text}

Return the optimized effects description. Format structural effects like: "## Guitar Solo ##".""",
}


class FieldOptimizer:
    """
    Optimizer for individual UI fields using GPT-4o.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the field optimizer.
        
        Args:
            openai_api_key: OpenAI API key. Reads from OPENAI_API_KEY if not provided.
        """
        self.api_key = openai_api_key or os.environ.get('OPENAI_API_KEY')
        self.model = "gpt-4o"
        self.simulation_mode = not self.api_key
        
        if self.simulation_mode:
            logger.warning("No OPENAI_API_KEY found. FieldOptimizer in simulation mode.")
    
    def optimize_field(self, field_name: str, text: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Optimize a specific field using GPT-4o.
        
        Args:
            field_name: Name of the field to optimize
            text: Current field text
            context: Optional additional context
            
        Returns:
            Dict with optimized text and metadata.
        """
        if not text.strip():
            return {
                "success": False,
                "error": "No text provided to optimize",
                "original": text,
                "optimized": text
            }
        
        if self.simulation_mode:
            return self._simulate_optimization(field_name, text)
        
        prompt_template = OPTIMIZATION_PROMPTS.get(field_name)
        if not prompt_template:
            prompt_template = OPTIMIZATION_PROMPTS.get("prompt_text")
        
        system_context = self._load_context_file(field_name)
        
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            
            messages = []
            if system_context:
                messages.append({"role": "system", "content": system_context})
            
            messages.append({
                "role": "user", 
                "content": prompt_template.format(text=text)
            })
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.4,
                max_tokens=1000
            )
            
            optimized = response.choices[0].message.content.strip()
            
            return {
                "success": True,
                "original": text,
                "optimized": optimized,
                "field": field_name,
                "model": self.model
            }
            
        except Exception as e:
            logger.error(f"Field optimization failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "original": text,
                "optimized": text
            }
    
    def _load_context_file(self, field_name: str) -> Optional[str]:
        """Load the context file for a given field."""
        context_file = FIELD_CONTEXT_MAPPING.get(field_name)
        if not context_file:
            return None
        
        context_path = CONTEXT_DIR / context_file
        if context_path.exists():
            try:
                return context_path.read_text()
            except Exception as e:
                logger.warning(f"Failed to load context file {context_path}: {e}")
        
        return None
    
    def _simulate_optimization(self, field_name: str, text: str) -> Dict[str, Any]:
        """Simulate optimization without API call."""
        optimized = text
        
        if field_name in ["prompt_text", "description"]:
            optimized = text[:250]
            filler = ["make a", "generate", "create", "i want", "please"]
            for f in filler:
                optimized = optimized.lower().replace(f, "").strip()
            optimized = optimized.capitalize()
            
        elif field_name in ["lyrics_text", "lyrics"]:
            if "[Verse]" not in text and "[Chorus]" not in text:
                optimized = "[Verse]\n" + text
            optimized = optimized.replace("[Guitar Solo]", "## Guitar Solo ##")
            optimized = optimized.replace("[Drop]", "## Drop ##")
            
        elif field_name in ["neuro_effects"]:
            translations = {
                "frisson": "soaring dynamics, sudden crescendo",
                "tension": "building intensity, rising pitch",
                "release": "harmonic resolution, dynamic drop",
                "chills": "ethereal harmonies, unexpected modulation"
            }
            for key, val in translations.items():
                if key in text.lower():
                    optimized = optimized.replace(key, val, 1)
                    optimized = optimized.replace(key.capitalize(), val, 1)
                    
        elif field_name in ["neurochemical_effects", "neurochemical_targets"]:
            translations = {
                "dopamine": "catchy hooks, syncopated bass",
                "serotonin": "warm tones, steady rhythm",
                "adrenaline": "fast tempo, aggressive drums",
                "endorphin": "euphoric build, triumphant drops"
            }
            for key, val in translations.items():
                if key in text.lower():
                    optimized = optimized.replace(key, val, 1)
                    optimized = optimized.replace(key.capitalize(), val, 1)
        
        logger.info(f"[SIMULATION] Optimized {field_name}: {len(text)} -> {len(optimized)} chars")
        
        return {
            "success": True,
            "original": text,
            "optimized": optimized,
            "field": field_name,
            "model": "simulation"
        }


def optimize_field(field_name: str, text: str) -> Dict[str, Any]:
    """
    Convenience function to optimize a field.
    
    Args:
        field_name: Name of the field
        text: Current text value
        
    Returns:
        Optimization result dict.
    """
    optimizer = FieldOptimizer()
    return optimizer.optimize_field(field_name, text)
