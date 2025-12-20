"""
LLM Client - GPT-4o integration for lyric generation and iteration.

Uses OpenAI API for:
- Seed-to-lyrics generation with syllable/rhyme constraints
- Lyric iteration based on agent scoring feedback
- Prompt optimization for Sonauto tags

Reference: Neo-Apex Architecture Documentation
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("openai package not installed. Run: pip install openai")

from apex_engine.config.prompts import (
    LYRIC_GENERATION_SYSTEM_PROMPT,
    LYRIC_ITERATION_SYSTEM_PROMPT,
    SEED_OPTIMIZATION_SYSTEM_PROMPT,
    MAGIC_FILL_SYSTEM_PROMPT,
    FIELD_OPTIMIZATION_SYSTEM_PROMPT,
    ANALYSIS_SYSTEM_PROMPT,
    ANALYSIS_PROMPTS
)


@dataclass
class LyricGenerationResult:
    """Result from lyric generation."""
    lyrics: str
    raw_response: Dict[str, Any]
    model: str
    tokens_used: int
    success: bool
    error: Optional[str] = None


FIELD_AGENT_MAPPING = {
    'prompt_text': {
        'description': 'Production texture, atmosphere, instrumentation',
        'agents': ['spectral', 'timbre'],
        'metrics': ['spectral_brightness', 'timbral_clarity', 'production_quality'],
        'optimization_focus': 'Enhance textural descriptors for latent diffusion model control'
    },
    'lyrics_text': {
        'description': 'Rhyme density, flow, structure',
        'agents': ['bars', 'flow', 'vowel', 'meme'],
        'metrics': ['rhyme_factor', 'multisyllabic_rhymes', 'assonance_chains', 'syllable_velocity', 
                   'plosive_density_index', 'flow_consistency', 'earworm_score', 'quotable_lines'],
        'optimization_focus': 'Maximize rhyme density, flow consistency, and quotability'
    },
    'neuro_effects': {
        'description': 'Frisson triggers, tension/release dynamics',
        'agents': ['frisson'],
        'metrics': ['dynamic_surge', 'spectral_expansion', 'expectation_violation'],
        'optimization_focus': 'Engineer psychoacoustic moments that trigger chills and emotional peaks'
    },
    'neurochemical_effects': {
        'description': 'Syncopation, groove, dopamine optimization',
        'agents': ['groove'],
        'metrics': ['syncopation_index', 'pocket_alignment', 'groove_quality'],
        'optimization_focus': 'Optimize rhythmic prediction error for dopaminergic engagement'
    },
    'musical_effects': {
        'description': 'Production techniques, mixing, arrangement',
        'agents': ['flow', 'mix'],
        'metrics': ['pdi_rating', 'breath_points', 'balance_strength'],
        'optimization_focus': 'Specify production techniques and mixing notes for Sonauto'
    }
}


class LLMClient:
    """GPT-4o client for lyric generation and iteration.
    
    Uses Replit AI Integrations for OpenAI-compatible API access.
    This does not require your own API key - charges are billed to Replit credits.
    """
    
    # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
    # do not change this unless explicitly requested by the user
    DEFAULT_MODEL = "gpt-5"
    FALLBACK_MODEL = "gpt-4o"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
        self.base_url = os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")
        self._client = None
        
        if self.base_url:
            logger.info("Using Replit AI Integrations for OpenAI access")
        elif not self.api_key:
            logger.warning("No OpenAI API key configured. LLM features disabled.")
    
    @property
    def client(self):
        """Lazy initialization of OpenAI client with Replit AI Integrations support."""
        if self._client is None and OPENAI_AVAILABLE:
            if self.base_url and self.api_key:
                self._client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
            elif self.api_key:
                self._client = OpenAI(api_key=self.api_key)
        return self._client
    
    @property
    def is_available(self) -> bool:
        """Check if LLM is available."""
        has_replit_integration = bool(self.base_url and self.api_key)
        has_direct_key = bool(self.api_key and not self.base_url)
        return OPENAI_AVAILABLE and (has_replit_integration or has_direct_key)
    
    def _get_field_knowledge_context(self, field_name: str) -> str:
        """
        Get comprehensive knowledge base context for a field from attached documentation.
        This injects examples and best practices from the documentation into AI prompts.
        """
        try:
            from apex_engine.config.knowledge_base import (
                PROMPT_ENGINEERING, LYRICS_STRUCTURE, NEUROPSYCHOLOGICAL_EFFECTS,
                NEUROCHEMICAL_TARGETS, MUSICAL_EFFECTS, RAPLYZER_PROTOCOL,
                FLOW_ANALYSIS, MEME_QUOTABILITY, SONAUTO_TAG_TAXONOMY
            )
        except ImportError:
            return "(Knowledge base not available)"
        
        context_parts = []
        
        if field_name == 'prompt_text':
            context_parts.append("=== PROMPT ENGINEERING FOR SONAUTO ===")
            context_parts.append(PROMPT_ENGINEERING.get('overview', ''))
            context_parts.append("\nINSTRUMENTATION TERMS:")
            context_parts.append(", ".join(PROMPT_ENGINEERING.get('instrumentation_examples', [])))
            context_parts.append("\nVOCAL DELIVERY TERMS:")
            context_parts.append(", ".join(PROMPT_ENGINEERING.get('vocal_delivery_examples', [])))
            context_parts.append("\nATMOSPHERE DESCRIPTORS:")
            context_parts.append(", ".join(PROMPT_ENGINEERING.get('atmosphere_examples', [])))
            context_parts.append("\nPRODUCTION QUALIFIERS:")
            context_parts.append(", ".join(PROMPT_ENGINEERING.get('production_qualifiers', [])))
            context_parts.append("\nFULL PROMPT EXAMPLES:")
            for ex in PROMPT_ENGINEERING.get('full_examples', [])[:3]:
                context_parts.append(f"- {ex.get('style', '')}: {ex.get('prompt', '')}")
        
        elif field_name == 'lyrics_text':
            context_parts.append("=== LYRICS STRUCTURE & RHYME OPTIMIZATION ===")
            context_parts.append(LYRICS_STRUCTURE.get('overview', ''))
            context_parts.append("\nSTRUCTURAL TAGS:")
            for tag, desc in LYRICS_STRUCTURE.get('structural_tags', {}).items():
                context_parts.append(f"  {tag}: {desc}")
            context_parts.append("\nSYLLABLES PER BAR BY BPM:")
            for bpm, syl in LYRICS_STRUCTURE.get('length_guidelines', {}).get('syllables_per_bar', {}).items():
                context_parts.append(f"  {bpm}: {syl}")
            context_parts.append("\n=== RAPLYZER RHYME PROTOCOL ===")
            context_parts.append("Rhyme Factor targets:")
            for tier, desc in RAPLYZER_PROTOCOL.get('rhyme_factor', {}).get('interpretation', {}).items():
                context_parts.append(f"  {tier}: {desc}")
            context_parts.append("\nMultisyllabic rhymes (multis) = rhymes matching 2+ vowels")
            context_parts.append("Assonance chains = repeated vowel sounds creating internal rhyme patterns")
            context_parts.append("\n=== QUOTABILITY CRITERIA ===")
            for criterion in MEME_QUOTABILITY.get('criteria', []):
                context_parts.append(f"- {criterion.get('name', '')}: {criterion.get('description', '')}")
        
        elif field_name == 'neuro_effects':
            context_parts.append("=== NEUROPSYCHOLOGICAL EFFECTS (FRISSON) ===")
            context_parts.append(NEUROPSYCHOLOGICAL_EFFECTS.get('overview', ''))
            context_parts.append("\nFRISSON TRIGGERS:")
            for trigger in NEUROPSYCHOLOGICAL_EFFECTS.get('frisson_triggers', []):
                context_parts.append(f"- {trigger.get('name', '')}: {trigger.get('description', '')}. Example: {trigger.get('example', '')}")
            context_parts.append("\nDROP MECHANICS:")
            drop = NEUROPSYCHOLOGICAL_EFFECTS.get('drop_mechanics', {})
            context_parts.append(f"{drop.get('description', '')}. {drop.get('technique', '')}")
            context_parts.append("\nEXAMPLES:")
            for ex in NEUROPSYCHOLOGICAL_EFFECTS.get('examples', []):
                context_parts.append(f"- {ex}")
        
        elif field_name == 'neurochemical_effects':
            context_parts.append("=== NEUROCHEMICAL TARGETS (DOPAMINE/GROOVE) ===")
            context_parts.append(NEUROCHEMICAL_TARGETS.get('overview', ''))
            sync = NEUROCHEMICAL_TARGETS.get('syncopation_index', {})
            context_parts.append(f"\nSYNCOPATION INDEX GOLDILOCKS ZONE:")
            for zone, desc in sync.get('goldilocks_zone', {}).items():
                context_parts.append(f"  {zone}: {desc}")
            context_parts.append("\nGROOVE ELEMENTS:")
            for elem in NEUROCHEMICAL_TARGETS.get('groove_elements', []):
                context_parts.append(f"- {elem.get('name', '')}: {elem.get('description', '')}. Example: {elem.get('example', '')}")
            context_parts.append("\nEARWORM MECHANICS:")
            for mech in NEUROCHEMICAL_TARGETS.get('earworm_mechanics', {}).get('elements', []):
                context_parts.append(f"- {mech}")
            context_parts.append("\nEXAMPLES:")
            for ex in NEUROCHEMICAL_TARGETS.get('examples', []):
                context_parts.append(f"- {ex}")
        
        elif field_name == 'musical_effects':
            context_parts.append("=== MUSICAL EFFECTS & SONAUTO PARAMETERS ===")
            context_parts.append(MUSICAL_EFFECTS.get('overview', ''))
            context_parts.append("\nBALANCE_STRENGTH (Vocal/Instrumental Mix):")
            for range_val, desc in MUSICAL_EFFECTS.get('balance_strength', {}).get('recommendations', {}).items():
                context_parts.append(f"  {range_val}: {desc}")
            context_parts.append("\nPROMPT_STRENGTH (CFG Scale):")
            for range_val, desc in MUSICAL_EFFECTS.get('prompt_strength', {}).get('recommendations', {}).items():
                context_parts.append(f"  {range_val}: {desc}")
            context_parts.append("\nTAG ORDERING (Higher weight first):")
            for i, tag_type in enumerate(MUSICAL_EFFECTS.get('tag_ordering', {}).get('recommended_order', []), 1):
                context_parts.append(f"  {i}. {tag_type}")
            context_parts.append("\n=== SONAUTO TAG TAXONOMY ===")
            for cat_key, cat_data in list(SONAUTO_TAG_TAXONOMY.items())[:4]:
                context_parts.append(f"{cat_data.get('title', '')}: {', '.join(cat_data.get('tags', []))}")
            context_parts.append("\nEXAMPLES:")
            for ex in MUSICAL_EFFECTS.get('examples', []):
                context_parts.append(f"- {ex}")
        
        else:
            context_parts.append("(No specific knowledge context for this field)")
        
        return "\n".join(context_parts)
    
    def generate_lyrics(
        self,
        seed_text: str,
        genre: str = "trap",
        bpm: int = 140,
        mood: str = "aggressive",
        tags: Optional[List[str]] = None,
        model: Optional[str] = None
    ) -> LyricGenerationResult:
        """
        Generate lyrics from a seed/creative brief.
        
        Args:
            seed_text: Creative brief or concept for the song
            genre: Target genre (trap, boom bap, phonk, etc.)
            bpm: Target BPM for syllable calculation
            mood: Emotional tone (aggressive, melancholic, hype, etc.)
            tags: Additional style tags
            model: Override default model
        
        Returns:
            LyricGenerationResult with lyrics and metadata
        """
        if not self.is_available:
            return self._simulated_generation(seed_text, genre, bpm, mood)
        
        syllable_guidance = self._get_syllable_guidance(bpm)
        tags_str = ", ".join(tags) if tags else genre
        
        user_prompt = f"""Create rap lyrics based on this concept:

**Concept/Theme**: {seed_text}

**Genre**: {genre}
**BPM**: {bpm}
**Mood**: {mood}
**Style Tags**: {tags_str}

{syllable_guidance}

Generate a complete song with at least 2 verses and a chorus. Make it authentic to the {genre} style."""

        try:
            response = self.client.chat.completions.create(
                model=model or self.DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": LYRIC_GENERATION_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,
                max_tokens=2000
            )
            
            lyrics = response.choices[0].message.content.strip()
            
            return LyricGenerationResult(
                lyrics=lyrics,
                raw_response={
                    "id": response.id,
                    "model": response.model,
                    "created": response.created,
                    "prompt": user_prompt
                },
                model=response.model,
                tokens_used=response.usage.total_tokens if response.usage else 0,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Lyric generation failed: {e}")
            return LyricGenerationResult(
                lyrics="",
                raw_response={"error": str(e)},
                model=model or self.DEFAULT_MODEL,
                tokens_used=0,
                success=False,
                error=str(e)
            )
    
    def iterate_lyrics(
        self,
        current_lyrics: str,
        scores: Dict[str, Any],
        recommendations: List[str],
        genre: str = "trap",
        bpm: int = 140,
        model: Optional[str] = None
    ) -> LyricGenerationResult:
        """
        Iterate on lyrics based on scoring feedback.
        
        Args:
            current_lyrics: The lyrics to improve
            scores: Dict with rhyme_factor, flow_consistency, syncopation_index, pvs_score
            recommendations: List of specific improvements to make
            genre: Target genre
            bpm: Target BPM
            model: Override default model
        
        Returns:
            LyricGenerationResult with revised lyrics
        """
        if not self.is_available:
            return LyricGenerationResult(
                lyrics=current_lyrics,
                raw_response={"simulated": True, "note": "LLM not available"},
                model="simulated",
                tokens_used=0,
                success=True
            )
        
        scores_summary = f"""
**Current Scores**:
- Rhyme Density: {scores.get('rhyme_factor', 'N/A')}
- Flow Consistency: {scores.get('flow_consistency', 'N/A')}
- Syncopation Index: {scores.get('syncopation_index', 'N/A')}
- Predicted Virality Score: {scores.get('pvs_score', 'N/A')}
"""
        
        recs_text = "\n".join(f"- {rec}" for rec in recommendations)
        
        user_prompt = f"""**Current Lyrics**:
{current_lyrics}

{scores_summary}

**Recommendations for Improvement**:
{recs_text}

**Target Genre**: {genre}
**Target BPM**: {bpm}

Revise these lyrics to address the weak points. {self._get_syllable_guidance(bpm)}"""

        try:
            response = self.client.chat.completions.create(
                model=model or self.DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": LYRIC_ITERATION_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            revised_lyrics = response.choices[0].message.content.strip()
            
            return LyricGenerationResult(
                lyrics=revised_lyrics,
                raw_response={
                    "id": response.id,
                    "model": response.model,
                    "created": response.created,
                    "input_scores": scores,
                    "recommendations": recommendations
                },
                model=response.model,
                tokens_used=response.usage.total_tokens if response.usage else 0,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Lyric iteration failed: {e}")
            return LyricGenerationResult(
                lyrics=current_lyrics,
                raw_response={"error": str(e)},
                model=model or self.DEFAULT_MODEL,
                tokens_used=0,
                success=False,
                error=str(e)
            )
    
    def _get_syllable_guidance(self, bpm: int) -> str:
        """Get syllable count guidance based on BPM."""
        if bpm <= 95:
            return "Target ~10-12 syllables per bar for this boom bap tempo."
        elif bpm <= 130:
            return "Target ~12-14 syllables per bar for this mid-tempo flow."
        elif bpm <= 150:
            return "Target ~14-16 syllables per bar for this trap tempo (half-time feel)."
        else:
            return "Target ~8-10 syllables per bar for this high-tempo drill/phonk (or double-time for 16-20)."
    
    def _simulated_generation(
        self,
        seed_text: str,
        genre: str,
        bpm: int,
        mood: str
    ) -> LyricGenerationResult:
        """Simulated generation when API is not available."""
        simulated_lyrics = f"""[Intro]
Yeah... let's go
{genre.title()} vibes, {bpm} BPM

[Verse 1]
{seed_text[:50]}... that's the vision clear
Moving through the motion, no fear
Every bar precise, every rhyme sincere
Watch me demonstrate, make it all appear

Stack the syllables, watch the flow align
Every word intentional, by design
Rhythm and the rhyme intertwine
{mood.title()} energy, that's the sign

[Chorus]
This is {genre}, feel the wave
Every bar we spit, we engrave
From the booth to the stage we pave
The path forward, never be a slave

[Verse 2]
Back again with the second verse
Curse reversed, we rehearsed first
Multisyllabic, never terse
Flow immersive like we're immersed

Complex patterns in the cadence
Patience paid, now we're cashing payments
Statement made, demonstration
{mood.title()} domination

[Outro]
{genre.title()}... out."""

        return LyricGenerationResult(
            lyrics=simulated_lyrics,
            raw_response={
                "simulated": True,
                "seed": seed_text,
                "genre": genre,
                "bpm": bpm,
                "mood": mood
            },
            model="simulated",
            tokens_used=0,
            success=True
        )
    
    def optimize_seed(
        self,
        prompt_text: str = "",
        lyrics_text: str = "",
        neuro_effects: str = "",
        neurochemical_effects: str = "",
        musical_effects: str = "",
        genre: str = "trap",
        mood: str = "aggressive",
        bpm: int = 140,
        tags: str = "",
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Optimize seed composition fields using GPT-4o.
        
        References the Neo-Apex documentation to enhance prompts for latent diffusion.
        
        Returns:
            Dict with optimized field values
        """
        if not self.is_available:
            return {
                "success": True,
                "prompt_text": prompt_text,
                "lyrics_text": lyrics_text,
                "neuro_effects": neuro_effects,
                "neurochemical_effects": neurochemical_effects,
                "musical_effects": musical_effects,
                "tags": tags,
                "note": "LLM not available - returned original values"
            }
        
        user_prompt = f"""Optimize these seed composition fields for a {genre} track at {bpm} BPM with {mood} mood:

**Current Prompt/Description** (max 500 chars):
{prompt_text or "(empty)"}

**Current Lyrics** (max 1500 chars):
{lyrics_text or "(empty)"}

**Current Neuropsychological Effects** (max 300 chars):
{neuro_effects or "(empty)"}

**Current Neurochemical Targets** (max 300 chars):
{neurochemical_effects or "(empty)"}

**Current Musical Effects** (max 300 chars):
{musical_effects or "(empty)"}

**Current Tags**:
{tags or "(empty)"}

Enhance each non-empty field for optimal Sonauto generation. Make the prompt more textural/atmospheric, 
improve lyrics structure and flow, and ensure tags are properly ordered. 

Return JSON with keys: prompt_text, lyrics_text, neuro_effects, neurochemical_effects, musical_effects, tags
Only include keys that had meaningful input content."""
        
        try:
            response = self.client.chat.completions.create(
                model=model or self.DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": SEED_OPTIMIZATION_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=3000,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content.strip()
            result = json.loads(content)
            result["success"] = True
            result["model"] = response.model
            result["tokens_used"] = response.usage.total_tokens if response.usage else 0
            
            return result
            
        except Exception as e:
            logger.error(f"Seed optimization failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def magic_fill(
        self,
        partial_inputs: Dict[str, Any],
        context_text: str = "",
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Magic Fill - Auto-populate all form fields using GPT-4o.
        
        Reads partial inputs and optional context (from attached assets)
        to generate a complete song configuration.
        
        Args:
            partial_inputs: Any fields the user has already filled
            context_text: Additional context from attached files
            model: Override default model
        
        Returns:
            Dict with all form fields populated
        """
        if not self.is_available:
            return {
                "success": False,
                "error": "GPT-4o not available. Please set OPENAI_API_KEY.",
                "simulated": True
            }
        
        existing = partial_inputs or {}
        user_prompt = f"""Generate a complete song configuration based on these inputs:

**Existing Inputs**:
{json.dumps(existing, indent=2) if existing else "(No existing inputs)"}

**Additional Context**:
{context_text or "(No additional context)"}

Fill in ALL missing fields. If the user provided a theme or concept, build the entire song around it.
Make the lyrics authentic, with proper rhyme schemes and flow. Include at least 2 verses and a chorus.

Return complete JSON configuration."""

        try:
            response = self.client.chat.completions.create(
                model=model or self.DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": MAGIC_FILL_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content.strip()
            result = json.loads(content)
            result["success"] = True
            result["model"] = response.model
            result["tokens_used"] = response.usage.total_tokens if response.usage else 0
            
            return result
            
        except Exception as e:
            logger.error(f"Magic fill failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def analyze_with_gpt(
        self,
        lyrics: str,
        analysis_type: str = "comprehensive",
        scores: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Use GPT-4o to provide intelligent analysis and recommendations.
        
        This supplements algorithmic analysis with LLM-powered insights.
        
        Args:
            lyrics: The lyrics to analyze
            analysis_type: Type of analysis (rhyme, flow, meme, trend, comprehensive)
            scores: Existing algorithmic scores to contextualize
            model: Override default model
        
        Returns:
            Dict with analysis results and recommendations
        """
        if not self.is_available:
            return {
                "success": False,
                "error": "GPT-4o not available",
                "recommendations": ["Enable GPT-4o for AI-powered analysis"]
            }
        
        prompt_intro = ANALYSIS_PROMPTS.get(analysis_type, ANALYSIS_PROMPTS["comprehensive"])
        
        scores_context = ""
        if scores:
            scores_context = f"""

**Algorithmic Scores** (for context):
- Rhyme Factor: {scores.get('rhyme_factor', 'N/A')}
- Flow Consistency: {scores.get('flow_consistency', 'N/A')}
- PVS Score: {scores.get('pvs_score', 'N/A')}"""
        
        user_prompt = f"""{prompt_intro}
{scores_context}

**Lyrics**:
{lyrics}

Provide analysis as JSON with keys: score (1-10), analysis (string), strengths (list), improvements (list), recommendations (list)"""

        try:
            response = self.client.chat.completions.create(
                model=model or self.DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.6,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content.strip()
            result = json.loads(content)
            result["success"] = True
            result["analysis_type"] = analysis_type
            result["model"] = response.model
            
            return result
            
        except Exception as e:
            logger.error(f"GPT analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "recommendations": ["Analysis failed - check API key and try again"]
            }
    
    def optimize_field(
        self,
        field_name: str,
        current_value: str,
        analysis_context: Dict[str, Any],
        project_context: Dict[str, Any],
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Optimize a specific form field using GPT with agent analysis context.
        
        This method takes the accumulated console logs from algorithmic analysis
        and uses them to provide targeted, incremental improvements to a single field.
        Now includes comprehensive knowledge base context from attached documentation.
        
        Args:
            field_name: Name of the field to optimize (e.g., 'lyrics_text', 'prompt_text')
            current_value: Current content of the field
            analysis_context: Dict with console_logs and agent metrics
            project_context: Dict with genre, bpm, mood, etc.
            model: Override default model
        
        Returns:
            Dict with optimized_value, changes_made, and reasoning
        """
        if not self.is_available:
            return {
                "success": False,
                "error": "AI not available",
                "optimized_value": current_value
            }
        
        field_config = FIELD_AGENT_MAPPING.get(field_name, {})
        optimization_focus = field_config.get('optimization_focus', 'General improvement')
        relevant_metrics = field_config.get('metrics', [])
        
        knowledge_context = self._get_field_knowledge_context(field_name)
        
        metrics_text = ""
        if analysis_context.get('metrics'):
            metrics_text = "\n".join([
                f"- {k}: {v}" for k, v in analysis_context['metrics'].items()
                if k in relevant_metrics or not relevant_metrics
            ])
        
        console_logs_text = ""
        if analysis_context.get('console_logs'):
            console_logs_text = "\n".join([
                f"[{log.get('type', 'info').upper()}] {log.get('message', '')}"
                for log in analysis_context['console_logs'][-20:]
            ])
        
        system_prompt = f"""You are an expert music producer optimizing rap lyrics and production settings for the Sonauto API.

Your task: Optimize the "{field_name}" field based on the analysis context and knowledge base.

**Optimization Focus**: {optimization_focus}

**Relevant Metrics to Improve**:
{', '.join(relevant_metrics) if relevant_metrics else 'General quality metrics'}

**KNOWLEDGE BASE CONTEXT**:
{knowledge_context}

Rules:
1. Make targeted, incremental improvements - don't rewrite everything
2. Reference specific metric deficiencies when making changes
3. Preserve the artist's voice and intent
4. Use SPECIFIC EXAMPLES from the knowledge base context above
5. For lyrics: maximize rhyme density using Raplyzer protocol, add multis, assonance chains
6. For prompt_text: use instrumentation terms, vocal delivery, atmosphere descriptors from knowledge base
7. For neuro_effects: target frisson triggers (dynamic surges, spectral expansion, expectation violation)
8. For neurochemical_effects: optimize syncopation index (target 15-30), groove elements, earworm mechanics
9. For musical_effects: use balance_strength/prompt_strength guidance, tag ordering from knowledge base

Return JSON with:
- optimized_value: The improved content
- changes_made: List of specific changes with references to knowledge base concepts
- reasoning: Why each change improves the target metrics"""

        user_prompt = f"""**Field**: {field_name}

**Current Value**:
{current_value or "(empty)"}

**Project Context**:
- Genre: {project_context.get('genre', 'trap')}
- BPM: {project_context.get('bpm', 140)}
- Mood: {project_context.get('mood', 'aggressive')}

**Current Metrics**:
{metrics_text or "(No metrics yet)"}

**Analysis Console Logs**:
{console_logs_text or "(No analysis run yet)"}

Optimize this field using the knowledge base examples and best practices. Make targeted improvements that directly address any issues shown in the console logs."""

        try:
            response = self.client.chat.completions.create(
                model=model or self.DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_completion_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content.strip()
            result = json.loads(content)
            result["success"] = True
            result["field_name"] = field_name
            result["model"] = response.model
            
            return result
            
        except Exception as e:
            logger.error(f"Field optimization failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "optimized_value": current_value
            }
