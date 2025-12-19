"""
Validators for Fal.ai MiniMax Music v2.

Implements:
- Double Hash Protocol: Convert [Instrument] to ## Instrument ##
- Breath Protocol: Ensure proper spacing around section tags
- Prompt validation: Character limits and content checks
"""

import re
import logging
from typing import Tuple, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

INSTRUMENTAL_TOKENS = [
    "Guitar Solo", "Bass Solo", "Drum Solo", "Piano Solo",
    "Drop", "Bass Drop", "Beat Drop",
    "Silence", "Pause", "Stop",
    "Break", "Breakdown",
    "Drum Fill", "Fill",
    "Instrumental", "Interlude",
    "Solo", "Riff"
]

KEEP_BRACKET_TAGS = ["Intro", "Outro", "Verse", "Chorus", "Pre-Chorus", "Bridge", "Hook"]

TAG_STANDARDIZATION = {
    "(Verse)": "[Verse]",
    "Verse 1:": "[Verse]",
    "Verse 2:": "[Verse]",
    "V1": "[Verse]",
    "V2": "[Verse]",
    "(Chorus)": "[Chorus]",
    "Chorus:": "[Chorus]",
    "Refrain": "[Chorus]",
    "Hook": "[Chorus]",
    "(Hook)": "[Chorus]",
    "Pre": "[Pre-Chorus]",
    "Prechorus": "[Pre-Chorus]",
    "(Pre-Chorus)": "[Pre-Chorus]",
    "Middle 8": "[Bridge]",
    "(Bridge)": "[Bridge]",
    "(Intro)": "[Intro]",
    "(Outro)": "[Outro]",
}

TECHNICAL_PATTERNS = [
    r"(?i)(BPM|Tempo)\s*[:=]?\s*\d+",
    r"(?i)Key\s*[:=]?\s*[A-Ga-g][#b]?\s*(major|minor|m)?",
    r"(?i)(Mix|Mastering|Reverb|Delay|Volume|Gain)\s*[:=]?\s*\w+",
    r"(?i)Time\s*Signature\s*[:=]?\s*\d+/\d+",
]


@dataclass
class ValidationResult:
    """Result of validation with errors, warnings, and corrected text."""
    valid: bool
    text: str
    errors: List[str]
    warnings: List[str]
    corrections: List[str]


def validate_and_fix_lyrics(text: str) -> ValidationResult:
    """
    Validate and fix lyrics for Fal.ai MiniMax Music v2.
    
    Implements:
    - Double Hash Protocol
    - Breath Protocol
    - Tag Standardization
    - Technical Leakage Removal
    
    Args:
        text: Raw lyrics text from user.
        
    Returns:
        ValidationResult with corrected text and any issues found.
    """
    errors = []
    warnings = []
    corrections = []
    
    if len(text) > 3000:
        text = text[:2997] + "..."
        corrections.append("Truncated lyrics to 3000 characters")
    
    for pattern in TECHNICAL_PATTERNS:
        matches = re.findall(pattern, text)
        if matches:
            text = re.sub(pattern, '', text)
            corrections.append(f"Removed technical parameters: {matches}")
    
    for old, new in TAG_STANDARDIZATION.items():
        if old in text:
            text = text.replace(old, new)
            corrections.append(f"Standardized '{old}' to '{new}'")
    
    text = apply_double_hash_protocol(text)
    
    text = apply_breath_protocol(text)
    
    has_structure = any(f"[{tag}]" in text for tag in KEEP_BRACKET_TAGS)
    if not has_structure:
        warnings.append("Missing structure tags. Consider adding [Verse]/[Chorus].")
        if text.strip() and not text.strip().startswith('['):
            text = "[Verse]\n" + text
            corrections.append("Added [Verse] tag to beginning")
    
    text = re.sub(r'\n{4,}', '\n\n\n', text)
    
    valid = len(errors) == 0
    
    return ValidationResult(
        valid=valid,
        text=text.strip(),
        errors=errors,
        warnings=warnings,
        corrections=corrections
    )


def apply_double_hash_protocol(text: str) -> str:
    """
    Convert bracketed instrumental events to ## format.
    
    [Guitar Solo] -> ## Guitar Solo ##
    [Drop] -> ## Drop ##
    """
    for token in INSTRUMENTAL_TOKENS:
        patterns = [
            (f"[{token}]", f"## {token} ##"),
            (f"({token})", f"## {token} ##"),
            (f"[{token.lower()}]", f"## {token} ##"),
            (f"({token.lower()})", f"## {token} ##"),
        ]
        for old, new in patterns:
            text = text.replace(old, new)
    
    bracket_pattern = r'\[([^\]]+)\]'
    
    def replace_if_instrumental(match):
        content = match.group(1)
        if any(keep.lower() in content.lower() for keep in KEEP_BRACKET_TAGS):
            return match.group(0)
        if any(inst.lower() in content.lower() for inst in INSTRUMENTAL_TOKENS):
            return f"## {content} ##"
        return match.group(0)
    
    text = re.sub(bracket_pattern, replace_if_instrumental, text)
    
    return text


def apply_breath_protocol(text: str) -> str:
    """
    Ensure proper spacing around section tags and ## markers.
    
    Each [Section] and ## Tag ## should have \n\n before and after.
    """
    text = re.sub(r'([^\n])\s*(\[(?:Verse|Chorus|Intro|Outro|Bridge|Pre-Chorus|Hook)\])', r'\1\n\n\2', text)
    
    text = re.sub(r'(\[(?:Verse|Chorus|Intro|Outro|Bridge|Pre-Chorus|Hook)\])([^\n])', r'\1\n\2', text)
    
    text = re.sub(r'([^\n])\s*(## .+ ##)', r'\1\n\n\2', text)
    
    text = re.sub(r'(## .+ ##)([^\n])', r'\1\n\n\2', text)
    
    return text


def validate_prompt(text: str) -> ValidationResult:
    """
    Validate the style prompt for Fal.ai.
    
    Args:
        text: Style prompt text.
        
    Returns:
        ValidationResult with any issues found.
    """
    errors = []
    warnings = []
    corrections = []
    
    if len(text) < 10:
        errors.append("Style prompt too short. Add genre, mood, instrumentation (min 10 chars).")
    
    if len(text) > 300:
        text = text[:297] + "..."
        corrections.append("Truncated prompt to 300 characters")
    
    if '[' in text or ']' in text:
        bracket_content = re.findall(r'\[([^\]]+)\]', text)
        warnings.append(f"Structural tags detected in prompt: {bracket_content}. Move to lyrics_prompt.")
        text = re.sub(r'\[[^\]]+\]', '', text).strip()
        corrections.append("Removed structural tags from prompt")
    
    for pattern in TECHNICAL_PATTERNS:
        matches = re.findall(pattern, text)
        if matches:
            text = re.sub(pattern, '', text)
            corrections.append(f"Removed technical parameters: {matches}")
    
    filler_patterns = [
        r"(?i)^(Make|Generate|Create|I want|Please)\s+(a\s+)?",
        r"(?i)\b(song|track|audio|music)\s+(about|that|with)\b",
    ]
    for pattern in filler_patterns:
        if re.search(pattern, text):
            text = re.sub(pattern, '', text).strip()
            corrections.append("Removed filler phrases for efficiency")
    
    valid = len(errors) == 0
    
    return ValidationResult(
        valid=valid,
        text=text.strip(),
        errors=errors,
        warnings=warnings,
        corrections=corrections
    )


def validate_full_payload(prompt: str, lyrics: str) -> Tuple[str, str, List[str]]:
    """
    Validate both prompt and lyrics, returning corrected versions.
    
    Args:
        prompt: Style prompt
        lyrics: Lyrics text
        
    Returns:
        Tuple of (corrected_prompt, corrected_lyrics, all_issues)
    """
    prompt_result = validate_prompt(prompt)
    lyrics_result = validate_and_fix_lyrics(lyrics)
    
    all_issues = []
    all_issues.extend([f"[PROMPT ERROR] {e}" for e in prompt_result.errors])
    all_issues.extend([f"[PROMPT WARNING] {w}" for w in prompt_result.warnings])
    all_issues.extend([f"[LYRICS ERROR] {e}" for e in lyrics_result.errors])
    all_issues.extend([f"[LYRICS WARNING] {w}" for w in lyrics_result.warnings])
    
    return prompt_result.text, lyrics_result.text, all_issues
