"""
UI Text Configuration - Help strings and tooltips for all input fields.

This file contains contextual help text for every input field in the APEX Engine UI.
Each entry provides clear explanations of what the parameter does to audio generation.

Reference: Attached requirements - "Contextual Help System (UI/UX)"
"""

FIELD_HELP = {
    "project_name": {
        "label": "Project Name",
        "tooltip": "A unique name for your song project. This helps you organize and find your work later.",
        "placeholder": "e.g., Dark Trap Banger, Summer Vibes"
    },
    
    "genre": {
        "label": "Genre",
        "tooltip": "The primary musical style. This affects the BPM range, instrumentation, and overall sound. Trap uses heavy 808s and hi-hats, Boom Bap has classic sample-based production, Phonk features distorted Memphis-style beats.",
        "options": {
            "trap": "Modern trap with heavy 808s, rolling hi-hats, and dark melodies",
            "boom_bap": "Classic hip-hop with sample-based production and vinyl warmth",
            "phonk": "Memphis-style with distorted bass, cowbells, and aggressive energy",
            "drill": "UK/Chicago drill with sliding 808s and dark, minimal production",
            "melodic": "Melodic rap with singing hooks and atmospheric production",
            "conscious": "Lyric-focused with thoughtful production and social themes"
        }
    },
    
    "bpm": {
        "label": "BPM (Beats Per Minute)",
        "tooltip": "The tempo of the track. This affects syllable count targets and flow style. Lower BPM (80-100) suits boom bap, higher BPM (140-160) suits trap/drill.",
        "ranges": {
            "slow": "60-80 BPM: Slow, heavy feel. Good for dark, atmospheric tracks.",
            "boom_bap": "80-100 BPM: Classic boom bap tempo. 10-12 syllables per bar.",
            "mid": "100-130 BPM: Versatile mid-tempo. Good for melodic rap.",
            "trap": "130-150 BPM: Standard trap tempo. 14-16 syllables per bar (half-time).",
            "drill": "140-160 BPM: Drill/phonk territory. High energy.",
            "fast": "160+ BPM: Very fast. Use double-time flow."
        }
    },
    
    "mood": {
        "label": "Mood",
        "tooltip": "The emotional tone of the track. This influences vocal delivery, instrumentation choices, and overall atmosphere.",
        "options": {
            "aggressive": "Hard-hitting, confrontational energy with intense delivery",
            "melancholic": "Sad, introspective vibes with emotional depth",
            "hype": "High-energy, party-ready with crowd-moving appeal",
            "dark": "Ominous, atmospheric with mysterious undertones",
            "confident": "Self-assured swagger without being overly aggressive",
            "introspective": "Thoughtful, personal reflections on life"
        }
    },
    
    "prompt_text": {
        "label": "Prompt / Description",
        "tooltip": "Describe the texture, atmosphere, and instrumentation you want. Use specific descriptors like 'heavy 808 bass', 'rolling hi-hats', 'dark synth pads'. Avoid commands like '[add drums]' - describe the sound naturally.",
        "placeholder": "e.g., Dark, dystopian trap with heavy distorted 808s, eerie synth melodies, and aggressive vocal delivery. High-fidelity studio production.",
        "max_chars": 500,
        "tips": [
            "Be specific about instrumentation: 'sampled jazz piano' not just 'piano'",
            "Describe atmosphere: 'nocturnal', 'dystopian', 'wide stereo imaging'",
            "Include production quality: 'high-fidelity', 'CD-quality', 'studio-grade'"
        ]
    },
    
    "lyrics_text": {
        "label": "Lyrics",
        "tooltip": "The actual lyrics with structural tags like [Verse 1], [Chorus], [Bridge]. Use line breaks for natural breath points, CAPS for intensity, and ellipses (...) for dramatic pauses.",
        "placeholder": "[Verse 1]\nYour lyrics here...\n\n[Chorus]\nHook lyrics...",
        "max_chars": 1500,
        "formatting": {
            "tags": "[Intro], [Verse 1], [Chorus], [Bridge], [Outro]",
            "emphasis": "Use CAPS for intensity shifts",
            "pauses": "Use ... for dramatic pauses",
            "adlibs": "Use (parentheses) for ad-libs"
        }
    },
    
    "tags": {
        "label": "Style Tags",
        "tooltip": "Additional style descriptors that fine-tune the sound. Order matters: anchor genre first, then subgenre, mood, era, production style. Example: 'trap, dark, aggressive, 2020s, heavy bass'",
        "placeholder": "trap, dark, aggressive, heavy 808s",
        "tips": [
            "Order: genre > subgenre > mood > era > production",
            "Use the Tag Explorer to find valid tags",
            "Don't repeat tags that contradict each other"
        ]
    },
    
    "neuro_effects": {
        "label": "Neuropsychological Effects",
        "tooltip": "Target specific emotional/physical responses. Frisson (chills) is triggered by dynamic surges, spectral expansion, and expectation violations. These guide the AI to create emotionally impactful moments.",
        "placeholder": "e.g., Build tension through verse, release at chorus drop. Frisson trigger at 1:30 with dynamic surge.",
        "max_chars": 300,
        "examples": [
            "Dynamic surge at chorus entry for frisson",
            "Tension build through verse with release at hook",
            "Spectral expansion (brightness increase) at drop"
        ]
    },
    
    "neurochemical_effects": {
        "label": "Neurochemical Targets",
        "tooltip": "Target dopamine release through rhythmic prediction error (syncopation), groove quality, and earworm hooks. These create the 'head-nodding' and 'can't get it out of my head' effects.",
        "placeholder": "e.g., Strong syncopation for groove, repetitive hook for earworm, micro-timing swing",
        "max_chars": 300,
        "examples": [
            "Syncopation for rhythmic prediction error",
            "Repetition + novelty for earworm potential",
            "Micro-timing variations for groove"
        ]
    },
    
    "musical_effects": {
        "label": "Musical Effects",
        "tooltip": "Production techniques, mixing preferences, and reference tracks. Be specific about effects like reverb, delay, distortion, and stereo width.",
        "placeholder": "e.g., Heavy sidechain compression on 808, wide stereo chorus, tape saturation on vocals",
        "max_chars": 300,
        "examples": [
            "Sidechain compression for pumping effect",
            "Tape saturation for warmth",
            "Wide stereo imaging on synths"
        ]
    },
    
    "prompt_strength": {
        "label": "Prompt Strength (CFG Scale)",
        "tooltip": "Controls how closely the AI follows your prompt vs. its own creativity. Lower values (1.5-2.0) are more natural for pop/melodic, higher values (2.5-4.0) create more intense/aggressive sounds.",
        "ranges": {
            "1.5-2.0": "Natural: Pop rap, melodic, acoustic, jazz rap",
            "2.0-2.5": "Balanced: Trap, hip hop, boom bap, conscious rap",
            "2.5-4.0": "Aggressive: Phonk, drill, industrial - artifacts become aesthetic"
        },
        "default": 2.0
    },
    
    "balance_strength": {
        "label": "Balance Strength",
        "tooltip": "Controls the balance between vocals and instrumental. Lower values emphasize instrumental, higher values emphasize vocals. 0.7 is a good default for balanced rap tracks.",
        "range": "0.0 - 1.0",
        "default": 0.7
    }
}


AGENT_DESCRIPTIONS = {
    "rhyme_analyzer": {
        "name": "Rhyme Density Analyzer",
        "description": "Analyzes phonetic rhyme patterns using the CMU Pronouncing Dictionary. Detects perfect rhymes, slant rhymes, multisyllabic chains, and assonance.",
        "metrics": ["Rhyme Factor (RF)", "Perfect Rhymes", "Slant Rhymes", "Multisyllabic Count"],
        "thresholds": {
            "elite": "RF > 1.0 - Every word in a rhyme chain",
            "lyrical": "RF > 0.4 - Strong lyrical content",
            "vibe": "RF > 0.2 - Good for vibe/melodic rap",
            "low": "RF < 0.2 - Consider adding more rhymes"
        }
    },
    
    "syllable_analyzer": {
        "name": "Syllable Count Analyzer",
        "description": "Counts syllables per line and calculates variance. Consistent syllable counts create smoother flow.",
        "metrics": ["Syllable Counts", "Variance", "Flow Consistency"],
        "targets": {
            "80-100 BPM": "10-12 syllables per bar",
            "100-130 BPM": "12-14 syllables per bar",
            "130-150 BPM": "14-16 syllables per bar",
            "150+ BPM": "8-10 syllables (or 16-20 double-time)"
        }
    },
    
    "flow_analyzer": {
        "name": "Flow Consistency Analyzer",
        "description": "Evaluates how consistent the rhythmic flow is across bars. Low variance means smoother, more predictable flow.",
        "metrics": ["Flow Consistency Score", "Syllable Variance"],
        "interpretation": {
            "high": "> 0.8 - Very consistent, smooth flow",
            "medium": "0.6-0.8 - Good flow with some variation",
            "low": "< 0.6 - Inconsistent, may sound choppy"
        }
    },
    
    "meme_analyzer": {
        "name": "Quotability Analyzer",
        "description": "Identifies lines with high meme/quote potential. Looks for standalone punchlines, caption-friendly phrases, and clever wordplay.",
        "metrics": ["Meme Score", "Quotable Lines", "Punchline Count"],
        "criteria": [
            "Optimal length (5-15 words)",
            "Self-contained meaning",
            "Strong imagery or metaphor",
            "Wordplay or surprise"
        ]
    },
    
    "trend_analyzer": {
        "name": "Trend Alignment Analyzer",
        "description": "Evaluates how well the track aligns with current trends. Balances commercial viability with originality.",
        "metrics": ["Trend Score", "BPM Positioning", "Derivative Rate"],
        "positioning": {
            "ahead": "BPM higher than genre average - experimental",
            "on_trend": "BPM matches genre average - commercial",
            "behind": "BPM lower than genre average - retro"
        }
    },
    
    "frisson_analyzer": {
        "name": "Frisson Detector",
        "description": "Analyzes audio for 'chills' potential using psychoacoustic features. Requires audio file.",
        "metrics": ["Frisson Score", "Dynamic Surge", "Spectral Brightness", "Surprise Events"],
        "triggers": [
            "Dynamic surges (sudden loudness)",
            "Spectral expansion (brightness increase)",
            "Rhythmic surprises (off-beat accents)"
        ]
    }
}


CONSOLE_MESSAGES = {
    "analysis_start": "Starting {agent_name} analysis...",
    "analysis_complete": "{agent_name} complete",
    "analysis_failed": "{agent_name} failed: {error}",
    
    "score_pass": "PASS: {metric} = {value:.2f} (threshold: {threshold})",
    "score_warn": "WARN: {metric} = {value:.2f} (below recommended: {threshold})",
    "score_fail": "FAIL: {metric} = {value:.2f} (minimum: {threshold})",
    
    "recommendation": "TIP: {message}",
    "error": "ERROR: {message}",
    
    "generation_queued": "Audio generation queued (estimated cost: ${cost:.3f})",
    "generation_complete": "Audio generated successfully: {filename}",
    "generation_failed": "Audio generation failed: {error}"
}


MAGIC_FILL_PROMPT = """You are an expert music producer and AI prompt engineer specializing in rap/hip-hop production.

Given the user's partial inputs and any context from attached assets, generate a complete song configuration.

Your output must be valid JSON with these fields:
- genre: One of [trap, boom_bap, phonk, drill, melodic, conscious]
- bpm: Integer between 60-180
- mood: One of [aggressive, melancholic, hype, dark, confident, introspective]
- prompt_text: Textural description (max 500 chars)
- lyrics_text: Full lyrics with [Verse], [Chorus] tags (max 1500 chars)
- tags: Comma-separated style tags
- neuro_effects: Neuropsychological targets (max 300 chars)
- neurochemical_effects: Dopamine/groove targets (max 300 chars)
- musical_effects: Production techniques (max 300 chars)
- prompt_strength: Float 1.5-4.0 based on genre
- balance_strength: Float 0.5-0.9

Use the Sonauto best practices:
1. Tags order: anchor genre > subgenre > mood > era > production
2. Prompt should describe texture/atmosphere, not commands
3. Lyrics should use proper structural tags
4. Match BPM to genre conventions
5. CFG scale (prompt_strength) should match genre intensity"""
