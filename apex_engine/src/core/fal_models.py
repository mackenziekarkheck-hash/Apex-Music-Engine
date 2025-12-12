"""
Pydantic Models for Sonauto API Integration.

These models provide rigorous validation for all API payloads,
ensuring correct formatting before requests are sent.

Architecture: Uses direct Sonauto REST API calls
Reference: Neo-Apex Architecture Documentation
"""

from enum import Enum
from typing import List, Optional, Union, Tuple, Set, FrozenSet
from pydantic import BaseModel, Field, field_validator, model_validator
import json
import os
import logging

logger = logging.getLogger(__name__)


class OutputFormat(str, Enum):
    """Supported audio output formats."""
    WAV = "wav"
    MP3 = "mp3"
    OGG = "ogg"
    FLAC = "flac"


class ExtendSide(str, Enum):
    """Direction for song extension."""
    LEFT = "left"
    RIGHT = "right"


class SonautoModel(str, Enum):
    """Canonical Sonauto API endpoints."""
    TEXT_TO_MUSIC = "songs"
    INPAINT = "songs/inpaint"
    EXTEND = "songs/extend"


def _load_tag_database_once() -> Tuple[List[str], FrozenSet[str]]:
    """Load validated tags from sonauto_tags.json at module initialization."""
    config_path = os.path.join(
        os.path.dirname(__file__), 
        '..', '..', 'config', 'sonauto_tags.json'
    )
    try:
        with open(config_path, 'r') as f:
            data = json.load(f)
            tags_list = data.get('validated_tags', [])
            tags_set = frozenset(tag.lower() for tag in tags_list)
            return tags_list, tags_set
    except FileNotFoundError:
        logger.warning("sonauto_tags.json not found, tag validation disabled")
        return [], frozenset()


TAG_DATABASE, VALID_TAGS_SET = _load_tag_database_once()


def load_tag_database() -> List[str]:
    """Return cached tag list (for backwards compatibility)."""
    return TAG_DATABASE


GENRE_CFG_DEFAULTS = {
    'trap': 2.2,
    'drill': 2.5,
    'boom_bap': 1.8,
    'boom bap': 1.8,
    'pop_rap': 1.5,
    'pop rap': 1.5,
    'cloud_rap': 1.6,
    'cloud rap': 1.6,
    'phonk': 3.0,
    'aggressive': 2.8,
    'conscious': 1.7,
    'conscious rap': 1.7,
    'melodic': 1.5,
    'emo rap': 1.6,
    'jazz rap': 1.7,
    'default': 2.0
}


COST_PER_GENERATION_USD = 0.075
COST_PER_INPAINT_USD = 0.075
COST_PER_EXTEND_USD = 0.075


def validate_tags_o1(tags: List[str]) -> Tuple[List[str], List[str]]:
    """
    O(1) tag validation using cached frozenset.
    
    Returns:
        Tuple of (normalized_tags, invalid_tags)
    """
    normalized = []
    invalid = []
    
    for tag in tags:
        norm_tag = tag.lower().strip()
        normalized.append(norm_tag)
        if VALID_TAGS_SET and norm_tag not in VALID_TAGS_SET:
            invalid.append(tag)
    
    return normalized, invalid


class SonautoGenerationRequest(BaseModel):
    """
    Validated payload for Sonauto generation via fal.ai.
    
    Reference: Sonauto API Design & Critique Section 4.1 "God-Mode Payload"
    """
    prompt: str = Field(
        ..., 
        description="Descriptive prompt for the diffusion model. Use textural descriptors."
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Ordered list of style tags from Tag Explorer. Order matters - anchor genre first."
    )
    lyrics: Optional[str] = Field(
        None,
        description="Lyrics with structural formatting ([Verse], [Chorus], etc)."
    )
    prompt_strength: float = Field(
        2.0,
        ge=0.0,
        le=5.0,
        description="CFG Scale. 1.5-2.0 for natural genres, 2.5-4.0 for aggressive/phonk."
    )
    balance_strength: float = Field(
        0.7,
        ge=0.0,
        le=1.0,
        description="Mix balance. 0.0=Instrumental only, 1.0=Vocals only. Default 0.7."
    )
    bpm: Union[int, str] = Field(
        "auto",
        description="BPM as integer or 'auto' for model inference."
    )
    seed: Optional[int] = Field(
        None,
        description="Random seed for deterministic generation. Use for A/B testing."
    )
    num_songs: int = Field(
        1,
        ge=1,
        le=2,
        description="Number of variations to generate (1 or 2)."
    )
    output_format: OutputFormat = Field(
        OutputFormat.WAV,
        description="Audio format. WAV required for stem analysis."
    )
    instrumental: bool = Field(
        False,
        description="If true, generates instrumental only (ignores lyrics)."
    )
    webhook_url: Optional[str] = Field(
        None,
        description="URL for async webhook callbacks."
    )
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Validate tags against Tag Explorer database with O(1) lookup."""
        if not v:
            return v
        
        normalized, invalid = validate_tags_o1(v)
        
        if invalid:
            logger.warning(
                f"Tags not in Tag Explorer database (may still work): {invalid}"
            )
        
        return normalized
    
    @field_validator('bpm')
    @classmethod
    def validate_bpm(cls, v: Union[int, str]) -> Union[int, str]:
        """Validate BPM is either 'auto' or a reasonable integer."""
        if isinstance(v, str):
            if v.lower() != 'auto':
                raise ValueError("BPM string must be 'auto'")
            return 'auto'
        if isinstance(v, int):
            if not 40 <= v <= 240:
                raise ValueError("BPM must be between 40 and 240")
        return v
    
    def to_sonauto_payload(self) -> dict:
        """Convert to Sonauto API payload format."""
        payload = {
            'prompt': self.prompt,
            'tags': self.tags,
            'prompt_strength': self.prompt_strength,
            'balance_strength': self.balance_strength,
            'num_songs': self.num_songs,
            'output_format': self.output_format.value,
            'instrumental': self.instrumental,
        }
        
        if self.lyrics:
            payload['lyrics'] = self.lyrics
        if self.bpm != 'auto':
            payload['bpm'] = self.bpm
        if self.seed is not None:
            payload['seed'] = self.seed
            
        return payload
    
    def estimate_cost(self) -> float:
        """Estimate USD cost for this generation."""
        base_cost = COST_PER_GENERATION_USD
        if self.num_songs == 2:
            base_cost *= 1.5
        return base_cost


class SonautoInpaintRequest(BaseModel):
    """
    Validated payload for Sonauto inpainting via fal.ai.
    
    Reference: Sonauto API Design & Critique Section 5.2 "Structural Architect"
    Note: fal_client uses {"start": x, "end": y} format for sections
    """
    audio_url: str = Field(
        ...,
        description="CDN URL of the original track to inpaint."
    )
    sections: List[Tuple[float, float]] = Field(
        ...,
        description="Time windows to regenerate as (start, end) tuples in seconds."
    )
    lyrics: str = Field(
        "",
        description="Lyrics for the inpainted section. Required for vocal inpainting."
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Style tags for the inpainted section."
    )
    prompt: Optional[str] = Field(
        None,
        description="Optional prompt for inpainted section (e.g., 'Instrumental drop, heavy bass')."
    )
    prompt_strength: float = Field(
        2.0,
        ge=0.0,
        le=5.0,
        description="CFG scale for inpainting. Higher for more dramatic changes."
    )
    balance_strength: float = Field(
        0.7,
        ge=0.0,
        le=1.0,
        description="Mix balance for inpainted section."
    )
    seed: Optional[int] = Field(
        None,
        description="Seed for deterministic inpainting."
    )
    selection_crop: bool = Field(
        False,
        description="If True, return only the inpainted section. If False, return full song."
    )
    
    @field_validator('sections')
    @classmethod
    def validate_sections(cls, v: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """Validate section format and values."""
        if not v:
            raise ValueError("At least one section required for inpainting")
        
        for start, end in v:
            if start < 0:
                raise ValueError(f"Section start time cannot be negative: {start}")
            if end <= start:
                raise ValueError(f"Section end must be greater than start: [{start}, {end}]")
            if end - start > 30:
                logger.warning(
                    f"Large inpaint section ({end - start}s) may affect quality"
                )
        
        return v
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Validate tags with O(1) lookup."""
        if not v:
            return v
        normalized, invalid = validate_tags_o1(v)
        if invalid:
            logger.warning(f"Tags not in taxonomy: {invalid}")
        return normalized
    
    def to_sonauto_payload(self) -> dict:
        """
        Convert to Sonauto API payload format.
        
        Note: Sonauto uses {"start": x, "end": y} object format for sections
        """
        payload = {
            'audio_url': self.audio_url,
            'sections': [{"start": s[0], "end": s[1]} for s in self.sections],
            'tags': self.tags,
            'prompt_strength': self.prompt_strength,
            'balance_strength': self.balance_strength,
            'selection_crop': self.selection_crop,
        }
        
        if self.lyrics:
            payload['lyrics_prompt'] = self.lyrics
        if self.prompt:
            payload['prompt'] = self.prompt
        if self.seed is not None:
            payload['seed'] = self.seed
            
        return payload
    
    def estimate_cost(self) -> float:
        """Estimate USD cost for inpainting."""
        return COST_PER_INPAINT_USD


class SonautoExtendRequest(BaseModel):
    """
    Validated payload for Sonauto track extension via fal.ai.
    
    Reference: Sonauto API Design & Critique Section 6.2 "Extension Protocol"
    """
    audio_url: str = Field(
        ...,
        description="CDN URL of the original track to extend."
    )
    side: ExtendSide = Field(
        ExtendSide.RIGHT,
        description="Direction to extend: 'left' (prepend) or 'right' (append)."
    )
    crop_duration: Optional[float] = Field(
        None,
        ge=0.0,
        le=10.0,
        description="Seconds to trim from tail (for removing fade-outs before extension)."
    )
    prompt: Optional[str] = Field(
        None,
        description="Prompt for extended section."
    )
    lyrics: Optional[str] = Field(
        None,
        description="Lyrics for extended section."
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Style tags for extended section."
    )
    prompt_strength: float = Field(
        2.0,
        ge=0.0,
        le=5.0
    )
    balance_strength: float = Field(
        0.7,
        ge=0.0,
        le=1.0
    )
    seed: Optional[int] = Field(None)
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Validate tags with O(1) lookup."""
        if not v:
            return v
        normalized, _ = validate_tags_o1(v)
        return normalized
    
    def to_sonauto_payload(self) -> dict:
        """Convert to Sonauto API payload format."""
        payload = {
            'audio_url': self.audio_url,
            'side': self.side.value,
            'prompt_strength': self.prompt_strength,
            'balance_strength': self.balance_strength,
        }
        
        if self.crop_duration is not None:
            payload['crop_duration'] = self.crop_duration
        if self.prompt:
            payload['prompt'] = self.prompt
        if self.lyrics:
            payload['lyrics_prompt'] = self.lyrics
        if self.tags:
            payload['tags'] = self.tags
        if self.seed is not None:
            payload['seed'] = self.seed
            
        return payload
    
    def estimate_cost(self) -> float:
        """Estimate USD cost for extension."""
        return COST_PER_EXTEND_USD


class FalApiResponse(BaseModel):
    """Response model for fal.ai API calls."""
    request_id: str = Field(..., description="Unique request identifier for idempotency")
    status: str = Field(..., description="Request status (QUEUED, IN_PROGRESS, COMPLETED, FAILED)")
    audio: Optional[List[dict]] = Field(None, description="Audio results when completed")
    error: Optional[str] = Field(None, description="Error message if failed")
    seed: Optional[int] = Field(None, description="Seed used for generation")
    
    def get_audio_url(self, index: int = 0) -> Optional[str]:
        """Extract audio URL from response."""
        if self.audio and len(self.audio) > index:
            return self.audio[index].get('url')
        return None
