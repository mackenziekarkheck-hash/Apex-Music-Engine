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


@dataclass
class LyricGenerationResult:
    """Result from lyric generation."""
    lyrics: str
    raw_response: Dict[str, Any]
    model: str
    tokens_used: int
    success: bool
    error: Optional[str] = None


LYRIC_GENERATION_SYSTEM_PROMPT = """You are an expert rap lyricist and flow architect. Your task is to generate rap lyrics that are:

1. **Rhythmically Precise**: Match syllable counts to the target BPM
   - At 90 BPM (boom bap): ~10-12 syllables per bar
   - At 140 BPM (trap): ~14-16 syllables per bar (half-time feel)
   - At 150+ BPM (phonk/drill): ~8-10 syllables per bar (double-time optional)

2. **Phonetically Rich**: Maximize rhyme density through:
   - Multisyllabic rhymes (e.g., "spectacular" / "vernacular")
   - Internal rhymes within bars
   - Assonance chains (matching vowel sounds)
   - Slant rhymes when perfect rhymes feel forced

3. **Structurally Formatted**: Use proper song structure:
   - [Intro], [Verse 1], [Chorus], [Verse 2], [Bridge], [Outro]
   - Line breaks for natural breath points
   - Ellipses (...) for pauses
   - CAPS for emphasis/intensity

4. **Flow-Conscious**: Consider how words will be delivered:
   - Plosive consonants (P, B, T, D, K, G) add punch
   - Sibilants (S, Z, SH) add texture
   - Avoid tongue-twisters unless intentional

Output ONLY the lyrics with structural tags. No explanations or commentary."""


LYRIC_ITERATION_SYSTEM_PROMPT = """You are an expert rap lyricist tasked with improving existing lyrics based on scoring feedback.

You will receive:
1. The current lyrics
2. Scoring metrics (rhyme density, flow consistency, syncopation, PVS)
3. Specific recommendations for improvement

Your job is to revise the lyrics to address the weak points while preserving the strong elements.

Rules:
- If rhyme density is low (<0.6): Add more internal rhymes and multisyllabic end rhymes
- If flow consistency is low (<0.7): Normalize syllable counts across bars
- If syncopation is off: Adjust emphasis placement with punctuation and line breaks
- Preserve the overall theme and narrative
- Maintain structural formatting ([Verse], [Chorus], etc.)

Output ONLY the revised lyrics. No explanations."""


class LLMClient:
    """GPT-4o client for lyric generation and iteration."""
    
    DEFAULT_MODEL = "gpt-4o"
    FALLBACK_MODEL = "gpt-4o-mini"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self._client = None
        
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not set. LLM features disabled.")
    
    @property
    def client(self):
        """Lazy initialization of OpenAI client."""
        if self._client is None and self.api_key and OPENAI_AVAILABLE:
            self._client = OpenAI(api_key=self.api_key)
        return self._client
    
    @property
    def is_available(self) -> bool:
        """Check if LLM is available."""
        return bool(self.api_key and OPENAI_AVAILABLE)
    
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
