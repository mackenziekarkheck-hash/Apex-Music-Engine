"""
Knowledge Base - Comprehensive documentation from attached assets for help modals and AI optimization.

This module extracts and organizes all the key information from the documentation
to provide rich context for help buttons and AI field optimization.

Sources:
- Autonomous Aural Architectures (Agentic Framework)
- Sonauto API Rap Music Generation Plan
- Music AI Analysis and Algorithm Extraction
- Sonauto API Design and Critique
"""

SONAUTO_TAG_TAXONOMY = {
    "core_genre": {
        "title": "Core Genre",
        "description": "Fundamental rhythmic structure. Always include at least one.",
        "tags": ["rap", "hip hop"],
        "acoustic_implication": "Establishes the foundational beat pattern and vocal style"
    },
    "sub_genre": {
        "title": "Sub-Genre",
        "description": "Specific style that defines drum patterns and production approach.",
        "tags": ["trap", "drill", "boom bap", "pop rap", "cloud rap", "emo rap", "phonk", "drift phonk", "memphis rap", "conscious rap", "jazz rap", "lo-fi hip hop", "experimental hip hop"],
        "acoustic_implication": {
            "trap": "Fast hi-hats, heavy 808s, dark melodies",
            "drill": "Sliding 808s, minimal production, aggressive energy",
            "boom_bap": "Swing drums, sample-based, vinyl warmth",
            "cloud_rap": "Atmospheric, dreamy, reverb-heavy",
            "phonk": "Distorted bass, cowbells, Memphis-style vocals",
            "emo_rap": "Melodic, emotional, guitar-influenced"
        }
    },
    "era": {
        "title": "Era",
        "description": "Time period that affects mixing style and sonic character.",
        "tags": ["90s", "2000s", "2010s", "2020s", "old school", "modern", "retro", "futuristic"],
        "acoustic_implication": {
            "90s": "Lo-fi warmth, boom bap drums, jazz samples",
            "2000s": "Polished production, synth-heavy",
            "modern": "Clean, loud, maximalist",
            "retro": "Intentionally dated production"
        }
    },
    "mood": {
        "title": "Mood",
        "description": "Emotional tone that guides harmonic progression and delivery.",
        "tags": ["aggressive", "chill", "dark", "energetic", "emotional", "melancholic", "introspective", "triumphant", "hype", "nocturnal", "dystopian"],
        "acoustic_implication": "Influences key choice, tempo feel, and vocal intensity"
    },
    "instrumentation": {
        "title": "Instrumentation",
        "description": "Specific timbral and instrumental choices.",
        "tags": ["piano", "guitar", "synth", "808", "sample", "strings", "brass", "choir", "bells", "cowbell", "vinyl", "tape"],
        "acoustic_implication": "Direct control over which instruments appear in the mix"
    },
    "production": {
        "title": "Production Quality",
        "description": "Mixing and mastering characteristics.",
        "tags": ["high fidelity", "lo-fi", "studio quality", "polished", "raw", "atmospheric", "layered vocals", "backing vocals", "wide stereo"],
        "acoustic_implication": "Affects overall clarity, depth, and spatial characteristics"
    }
}

PROMPT_ENGINEERING = {
    "overview": """Unlike image generation where abstract concepts work well, audio diffusion models thrive on specific musical terminology. The prompt describes the 'texture' and 'atmosphere' of the track.""",
    
    "principles": [
        "Describe texture and atmosphere, not commands",
        "Use specific musical terminology",
        "Include production quality descriptors",
        "Order matters: prioritize anchor concepts first"
    ],
    
    "instrumentation_examples": [
        "heavy 808 bass",
        "rolling hi-hats",
        "sampled jazz piano",
        "cinematic strings",
        "vinyl crackle",
        "distorted 808 basslines",
        "cowbell melodies",
        "rapid-fire hi-hat triplets",
        "sliding 808s",
        "synth melody",
        "chopped samples"
    ],
    
    "vocal_delivery_examples": [
        "aggressive flow",
        "mumble rap",
        "fast-paced delivery",
        "melodic hook",
        "staccato delivery",
        "Memphis rap flow",
        "chopped and screwed effects",
        "UK Drill vocal style"
    ],
    
    "atmosphere_examples": [
        "dark",
        "triumphant",
        "melancholic",
        "hype",
        "nocturnal",
        "dystopian",
        "menacing",
        "introspective",
        "ethereal"
    ],
    
    "production_qualifiers": [
        "high-fidelity",
        "studio-quality",
        "CD-quality",
        "wide stereo imaging",
        "industrial textures",
        "polished production",
        "lo-fi warmth"
    ],
    
    "full_examples": [
        {
            "style": "Drill",
            "prompt": "A high-energy drill track with sliding 808 bass, rapid-fire hi-hat triplets, and a menacing synth melody. The vocal delivery is aggressive and staccato, typical of UK Drill."
        },
        {
            "style": "Phonk",
            "prompt": "A high-fidelity, studio-quality production of a Cyberpunk Phonk track. The instrumentation features heavy distorted 808 basslines, cowbell melodies, and rapid-fire hi-hat triplets. The vocal delivery is aggressive, utilizing a Memphis rap flow with chopped and screwed effects. The atmosphere is dark, dystopian, and nocturnal, with wide stereo imaging and industrial textures."
        },
        {
            "style": "Boom Bap",
            "prompt": "A nostalgic boom bap track with jazzy piano samples, crispy snares with vinyl crackle, and a smooth bass groove. The vocal delivery is confident and flowing, reminiscent of 90s golden era hip-hop. Lo-fi warmth throughout."
        },
        {
            "style": "Cloud Rap",
            "prompt": "An ethereal cloud rap production with dreamy synth pads, reverb-soaked 808s, and atmospheric textures. The vocal delivery is melodic and introspective with layered harmonies and autotune effects."
        },
        {
            "style": "Trap",
            "prompt": "A hard-hitting trap anthem with booming 808s, rolling hi-hats, and dark orchestral stabs. The production is polished and loud with aggressive vocal delivery and ad-libs throughout."
        }
    ]
}

LYRICS_STRUCTURE = {
    "overview": """Sonauto parses specific meta-tags enclosed in square brackets to determine song structure. These are not vocalized but act as state-switching triggers for the generator.""",
    
    "structural_tags": {
        "[Intro]": "Usually instrumental or spoken word ad-libs. Sets the tone.",
        "[Verse 1]": "Main lyrical body. Model expects consistent rhyme scheme.",
        "[Verse 2]": "Second verse, can introduce new themes.",
        "[Chorus]": "The hook. Model increases melodic complexity or layering.",
        "[Pre-Chorus]": "Build-up section before the hook.",
        "[Bridge]": "Change in flow or beat intensity.",
        "[Drop]": "High energy section, useful for Trap/EDM crossovers.",
        "[Outro]": "Fading out or final ad-libs."
    },
    
    "formatting_rules": [
        "Every block of text must be preceded by a structural tag",
        "Standard generation is ~90-95 seconds",
        "A typical 16-bar verse and 8-bar chorus fits well",
        "Providing too many lyrics causes rushing or truncation"
    ],
    
    "special_formatting": {
        "ad_libs": "(parenthetical text) is interpreted as background vocals or ad-libs",
        "emphasis": "CAPITALIZATION signals intensity shifts",
        "pauses": "Ellipses ... indicate dramatic pauses or phrasing breaks",
        "line_breaks": "Line breaks help indicate natural breath points"
    },
    
    "length_guidelines": {
        "verse_bars": "16 bars typical for a verse",
        "chorus_bars": "8 bars typical for a chorus",
        "total_duration": "~90-95 seconds per generation",
        "syllables_per_bar": {
            "80-100 BPM": "10-12 syllables per bar",
            "100-130 BPM": "12-14 syllables per bar",
            "130-150 BPM": "14-16 syllables per bar (half-time feel)",
            "150+ BPM": "8-10 syllables (or 16-20 double-time)"
        }
    },
    
    "example": """[Intro]
(Yeah)
Mic check one two
We live from the cloud

[Verse 1]
Digital signals moving through the wire
My logic gates open spitting pure fire
Algorithmic flow, synthetic desire
Watch the metrics climb ever higher

[Chorus]
This is the future sound
Automated underground
Breaking every bound
APEX ENGINE CROWNED"""
}

NEUROPSYCHOLOGICAL_EFFECTS = {
    "overview": """Frisson is a psychophysiological response characterized by shivers, goosebumps, and pupil dilation. Research indicates it is triggered by specific acoustic features.""",
    
    "frisson_triggers": [
        {
            "name": "Dynamic Surge (ΔRMS)",
            "description": "Sudden increases in loudness trigger a brainstem reflex",
            "example": "Entry of full instrumentation at chorus, post-silence explosions",
            "implementation": "Calculate RMS energy, measure first derivative peaks"
        },
        {
            "name": "Spectral Brightness (Centroid Expansion)",
            "description": "Rapid increase in high-frequency content creates high emotional arousal",
            "example": "Riser sounds, filter sweeps opening up before drops",
            "implementation": "Detect rapid spectral centroid increases"
        },
        {
            "name": "Spectral Contrast",
            "description": "Energy difference between peaks and valleys - high contrast sounds 'clear' and 'powerful'",
            "example": "Clean separation between vocals and instruments",
            "implementation": "Librosa spectral contrast analysis"
        },
        {
            "name": "Expectation Violation (Surprise)",
            "description": "Prediction error when rhythm or melody defies expectations",
            "example": "Off-beat accents, unexpected key changes, omitted strong beats",
            "implementation": "IDyOM-style onset analysis, autocorrelation for pulse strength"
        }
    ],
    
    "drop_mechanics": {
        "description": "The 'drop' maximizes reward prediction error",
        "technique": "Period of low rhythmic stability (buildup) followed by hyper-stability (the drop)",
        "pre_drop_gap": "Brief silence before transition acts as tension-builder",
        "timing": "Silence duration should align with BPM (e.g., exactly 1 bar)"
    },
    
    "tension_release_patterns": [
        "Build: Increasing complexity, rising frequencies, adding layers",
        "Peak: Maximum tension just before release",
        "Release: Sudden simplification, bass drop, beat entry",
        "Resolution: Return to groove with added energy"
    ],
    
    "examples": [
        "Dynamic surge at chorus entry - full beat drops in after stripped intro",
        "Spectral expansion with riser leading to drop at 1:30",
        "Tension build through verse with syncopated drums, release on hook",
        "Brief silence (1 bar) before explosive chorus entry",
        "Unexpected beat drop on weak beat for surprise factor"
    ]
}

NEUROCHEMICAL_TARGETS = {
    "overview": """Dopaminergic engagement is mediated by rhythmic prediction error. The brain rewards correct predictions but is most engaged when predictions are slightly violated (syncopation).""",
    
    "syncopation_index": {
        "description": "Quantifies the balance between predictability and complexity using the Longuet-Higgins model",
        "algorithm": {
            "step_1": "Quantize audio to 16th-note grid",
            "step_2": "Assign metric weights (Downbeat=0, Quarter=-1, Eighth=-2, Sixteenth=-3)",
            "step_3": "Syncopation occurs when onset at weak position is followed by silent strong position",
            "step_4": "Score = sum of weight differences for syncopated pairs"
        },
        "goldilocks_zone": {
            "optimal": "15-30 - Perfect balance of groove and complexity",
            "too_low": "<5 - Monotonous, no dopamine response",
            "too_high": ">50 - Chaotic, cognitive overload"
        }
    },
    
    "groove_elements": [
        {
            "name": "Micro-timing variations",
            "description": "Slight timing deviations from grid create 'human' feel",
            "example": "Dilla swing - snares slightly behind the beat"
        },
        {
            "name": "Hi-hat patterns",
            "description": "Syncopated hi-hat triplets create rhythmic tension",
            "example": "Trap rolling hi-hats with velocity variation"
        },
        {
            "name": "Bass-drum interplay",
            "description": "Alternation between kick and bass notes",
            "example": "808 slides between kick hits"
        }
    ],
    
    "earworm_mechanics": {
        "description": "Repetition with novelty creates 'sticky' hooks",
        "elements": [
            "Simple, memorable melodic phrases",
            "Call-and-response patterns",
            "Slight variations on repeated phrases",
            "Unexpected rhythmic or melodic twists"
        ]
    },
    
    "examples": [
        "Syncopated hi-hat triplets for rhythmic prediction error",
        "Micro-timing swing on snares (Dilla-style)",
        "808 slides that 'chase' the beat",
        "Repetitive hook with small melodic variations",
        "Off-grid kick placements for groove",
        "Target syncopation index 15-25 for optimal groove"
    ]
}

MUSICAL_EFFECTS = {
    "overview": """Production techniques that affect the final sonic character. The Sonauto API exposes key parameters for mixing control.""",
    
    "balance_strength": {
        "description": "Controls the ratio of vocal presence to instrumental volume",
        "range": "0.0 to 1.0",
        "default": "0.7",
        "recommendations": {
            "0.75-0.80": "High vocal clarity, ideal for technical rap with dense lyrics",
            "0.65-0.70": "Balanced mix, standard for most rap",
            "0.50-0.65": "Instrumental-forward, vocals blend with beat",
            "<0.50": "Buried vocals, atmospheric/mumble rap aesthetic"
        },
        "use_cases": [
            "Increase to 0.75-0.80 when lyrics have high syllable density",
            "Lower to 0.65 for phonk where instrumental texture is key",
            "Adjust based on vocal clarity in test generations"
        ]
    },
    
    "prompt_strength": {
        "description": "Classifier-Free Guidance (CFG) scale - how strictly model follows prompt",
        "range": "1.5 to 4.0+",
        "default": "2.0",
        "recommendations": {
            "1.5-2.0": "Natural, pop rap, melodic, acoustic - minimal artifacts",
            "2.0-2.5": "Balanced, trap, hip hop, boom bap - good adherence",
            "2.5-3.5": "Strong adherence, phonk, drill - artifacts become aesthetic",
            "3.5-4.0+": "Extreme, industrial, experimental - significant artifacts"
        },
        "warning": "Too high causes audio artifacts, but for distorted genres this fits the aesthetic"
    },
    
    "output_format": {
        "wav": "Essential for accurate spectral analysis - no compression artifacts",
        "mp3": "Lossy compression introduces artifacts that confuse analysis",
        "recommendation": "Always use WAV for analysis and inpainting workflows"
    },
    
    "tag_ordering": {
        "description": "Tags at the top of the list have higher weight in the diffusion process",
        "recommended_order": [
            "Anchor Genre (phonk, trap, boom bap)",
            "Sub-Genre (drift phonk, emo rap)",
            "Mood (aggressive, dark, emotional)",
            "Era (2020s, 90s, modern)",
            "Production (high fidelity, lo-fi)",
            "Specific instruments (808, synth, piano)"
        ]
    },
    
    "examples": [
        "balance_strength: 0.75 for clear vocal articulation in technical rap",
        "prompt_strength: 2.5 for strict genre adherence in phonk",
        "Tags ordered: trap, dark, aggressive, 2020s, heavy bass, distorted 808",
        "WAV output for any track going through flow analysis",
        "Lower balance_strength to 0.65 for instrumental-focused phonk",
        "Increase prompt_strength to 3.0+ for industrial/experimental"
    ]
}

RAPLYZER_PROTOCOL = {
    "overview": """The Raplyzer protocol quantifies lyrical technicality through phonetic analysis, moving beyond simple end-rhymes to detect complex assonance chains and multisyllabic rhymes.""",
    
    "rhyme_factor": {
        "description": "Average length of rhyme chains per word",
        "formula": "RF = Σ(Length of LCS matches) / Total word count",
        "interpretation": {
            ">1.0": "Elite - every word participates in a multisyllabic rhyme chain (MF DOOM, Eminem)",
            "0.6-1.0": "Lyrical - strong technical content",
            "0.4-0.6": "Good - solid rhyme schemes",
            "0.2-0.4": "Standard - basic rhyming",
            "<0.2": "Minimal - consider adding more rhymes"
        }
    },
    
    "multisyllabic_rhymes": {
        "description": "Rhymes matching 2+ vowels are 'multis' - hallmark of technical rap",
        "example": "'stack' and 'back' share AE vowel (single). 'digital' and 'critical' share IH-IH-AH (multi)",
        "target": "Higher multi count = more impressive technical display"
    },
    
    "assonance_chains": {
        "description": "Repeated vowel sounds creating internal rhyme patterns",
        "example": "'My vision is clear' -> AY IH IH IH (repeated IH creates chain)",
        "implementation": "Strip consonants, analyze vowel stream for patterns"
    },
    
    "phonetic_algorithm": {
        "steps": [
            "1. Normalize text (lowercase, remove punctuation)",
            "2. Deduplicate repeated choruses (they inflate scores artificially)",
            "3. Convert to phonemes using CMU Dictionary or G2P model",
            "4. Isolate vowel stream (rap flow is vowel-driven)",
            "5. For each word, scan lookback window (15-20 words) for LCS matches",
            "6. Count matches of 2+ vowels as valid rhymes"
        ]
    }
}

FLOW_ANALYSIS = {
    "overview": """Flow is the interaction of lyrics with time. Consistent syllable counts create smoother flow, while controlled variance creates dynamic interest.""",
    
    "syllable_targets": {
        "description": "Target syllables per bar based on tempo",
        "80-100 BPM": "10-12 syllables (boom bap comfort zone)",
        "100-130 BPM": "12-14 syllables (mid-tempo versatility)",
        "130-150 BPM": "14-16 syllables half-time, 8-10 double-time",
        "150+ BPM": "8-10 syllables or 16-20 double-time"
    },
    
    "variance_interpretation": {
        "low_variance": "Consistent, smooth flow (choppy/Dr. Seuss style)",
        "controlled_variance": "Complex, syncopated flow (intentional variation)",
        "high_variance": "Free verse or poor writing (unintentional)",
        "goal": "Either very low (smooth) or intentionally varied (dynamic)"
    },
    
    "stress_patterns": {
        "description": "Metrical feet analysis using CMU stress markers",
        "0": "Unstressed syllable",
        "1": "Primary stress",
        "2": "Secondary stress",
        "common_patterns": {
            "iambic": "0-1-0-1 (da-DUM da-DUM)",
            "trochaic": "1-0-1-0 (DUM-da DUM-da)",
            "dactylic": "1-0-0 (DUM-da-da)"
        }
    },
    
    "pdi_calculation": {
        "name": "Phonetic Density Index",
        "description": "Measures complexity of sound patterns per line",
        "factors": [
            "Consonant cluster density",
            "Vowel variety",
            "Phoneme count per syllable"
        ]
    }
}

MEME_QUOTABILITY = {
    "overview": """Lines with high meme/quote potential have specific characteristics that make them memorable and shareable.""",
    
    "criteria": [
        {
            "name": "Optimal Length",
            "description": "5-15 words - fits in a tweet, caption, or quote",
            "example": "'Started from the bottom now we're here' (7 words)"
        },
        {
            "name": "Self-Contained Meaning",
            "description": "Makes sense without context",
            "example": "'I got 99 problems but a beat ain't one'"
        },
        {
            "name": "Strong Imagery",
            "description": "Vivid metaphors or concrete images",
            "example": "'Diamonds dancing on my wrist like ballerinas'"
        },
        {
            "name": "Wordplay or Surprise",
            "description": "Clever double meanings or unexpected twists",
            "example": "'Real G's move in silence like lasagna'"
        },
        {
            "name": "Universal Truth",
            "description": "Relatable sentiment many people can apply",
            "example": "'Mo money mo problems'"
        }
    ],
    
    "punchline_techniques": [
        "Setup-Punchline structure within a bar",
        "Subverted expectations",
        "Homophones and double entendres",
        "Cultural references with twist",
        "Alliteration for memorability"
    ],
    
    "examples": [
        "'I didn't choose the thug life, the thug life chose me'",
        "'Started from the bottom now we're here'",
        "'Real G's move in silence like lasagna'",
        "'I got 99 problems but a beat ain't one'",
        "'Mo money mo problems'"
    ]
}

FIELD_AGENT_MAPPING = {
    "prompt_text": {
        "relevant_knowledge": ["PROMPT_ENGINEERING", "SONAUTO_TAG_TAXONOMY", "MUSICAL_EFFECTS"],
        "agents": ["trend_analyzer"],
        "optimization_focus": "Textural descriptors, instrumentation specificity, atmosphere"
    },
    "lyrics_text": {
        "relevant_knowledge": ["LYRICS_STRUCTURE", "RAPLYZER_PROTOCOL", "FLOW_ANALYSIS", "MEME_QUOTABILITY"],
        "agents": ["rhyme_analyzer", "flow_analyzer", "meme_analyzer"],
        "optimization_focus": "Rhyme density, syllable flow, quotable lines, structure"
    },
    "neuro_effects": {
        "relevant_knowledge": ["NEUROPSYCHOLOGICAL_EFFECTS"],
        "agents": ["frisson_analyzer"],
        "optimization_focus": "Frisson triggers, tension-release, dynamic surges"
    },
    "neurochemical_effects": {
        "relevant_knowledge": ["NEUROCHEMICAL_TARGETS"],
        "agents": ["flow_analyzer"],
        "optimization_focus": "Syncopation, groove, earworm potential"
    },
    "musical_effects": {
        "relevant_knowledge": ["MUSICAL_EFFECTS", "SONAUTO_TAG_TAXONOMY"],
        "agents": ["trend_analyzer"],
        "optimization_focus": "Production parameters, balance_strength, prompt_strength, tag ordering"
    }
}

def get_field_context(field_name: str) -> dict:
    """
    Get comprehensive context for a field including all relevant documentation.
    Used to inject knowledge into AI optimization prompts.
    """
    mapping = FIELD_AGENT_MAPPING.get(field_name, {})
    context = {
        "field_name": field_name,
        "optimization_focus": mapping.get("optimization_focus", ""),
        "knowledge_sections": []
    }
    
    for section_name in mapping.get("relevant_knowledge", []):
        section_data = globals().get(section_name, {})
        if section_data:
            context["knowledge_sections"].append({
                "name": section_name,
                "data": section_data
            })
    
    return context

def get_tag_explorer_data() -> dict:
    """Return full tag taxonomy for the Tag Explorer modal."""
    return SONAUTO_TAG_TAXONOMY

def get_field_help_content(field_name: str) -> dict:
    """
    Get comprehensive help content for a field including all examples.
    Returns structured data for rich help modals.
    """
    help_content = {
        "field_name": field_name,
        "sections": []
    }
    
    if field_name == "prompt_text":
        help_content["sections"] = [
            {
                "title": "Overview",
                "content": PROMPT_ENGINEERING["overview"],
                "type": "text"
            },
            {
                "title": "Key Principles",
                "content": PROMPT_ENGINEERING["principles"],
                "type": "list"
            },
            {
                "title": "Instrumentation Examples",
                "content": PROMPT_ENGINEERING["instrumentation_examples"],
                "type": "tags"
            },
            {
                "title": "Vocal Delivery Terms",
                "content": PROMPT_ENGINEERING["vocal_delivery_examples"],
                "type": "tags"
            },
            {
                "title": "Atmosphere Descriptors",
                "content": PROMPT_ENGINEERING["atmosphere_examples"],
                "type": "tags"
            },
            {
                "title": "Production Qualifiers",
                "content": PROMPT_ENGINEERING["production_qualifiers"],
                "type": "tags"
            },
            {
                "title": "Full Prompt Examples",
                "content": PROMPT_ENGINEERING["full_examples"],
                "type": "examples"
            }
        ]
    
    elif field_name == "lyrics_text":
        help_content["sections"] = [
            {
                "title": "Overview",
                "content": LYRICS_STRUCTURE["overview"],
                "type": "text"
            },
            {
                "title": "Structural Tags",
                "content": LYRICS_STRUCTURE["structural_tags"],
                "type": "key_value"
            },
            {
                "title": "Formatting Rules",
                "content": LYRICS_STRUCTURE["formatting_rules"],
                "type": "list"
            },
            {
                "title": "Special Formatting",
                "content": LYRICS_STRUCTURE["special_formatting"],
                "type": "key_value"
            },
            {
                "title": "Syllables Per Bar by BPM",
                "content": LYRICS_STRUCTURE["length_guidelines"]["syllables_per_bar"],
                "type": "key_value"
            },
            {
                "title": "Rhyme Factor Targets",
                "content": RAPLYZER_PROTOCOL["rhyme_factor"]["interpretation"],
                "type": "key_value"
            },
            {
                "title": "Example Lyrics",
                "content": LYRICS_STRUCTURE["example"],
                "type": "code"
            }
        ]
    
    elif field_name == "neuro_effects":
        help_content["sections"] = [
            {
                "title": "Overview",
                "content": NEUROPSYCHOLOGICAL_EFFECTS["overview"],
                "type": "text"
            },
            {
                "title": "Frisson Triggers",
                "content": [
                    f"**{t['name']}**: {t['description']}. Example: {t['example']}"
                    for t in NEUROPSYCHOLOGICAL_EFFECTS["frisson_triggers"]
                ],
                "type": "list"
            },
            {
                "title": "Drop Mechanics",
                "content": f"{NEUROPSYCHOLOGICAL_EFFECTS['drop_mechanics']['description']}. {NEUROPSYCHOLOGICAL_EFFECTS['drop_mechanics']['technique']}",
                "type": "text"
            },
            {
                "title": "Tension-Release Patterns",
                "content": NEUROPSYCHOLOGICAL_EFFECTS["tension_release_patterns"],
                "type": "list"
            },
            {
                "title": "Examples",
                "content": NEUROPSYCHOLOGICAL_EFFECTS["examples"],
                "type": "list"
            }
        ]
    
    elif field_name == "neurochemical_effects":
        help_content["sections"] = [
            {
                "title": "Overview",
                "content": NEUROCHEMICAL_TARGETS["overview"],
                "type": "text"
            },
            {
                "title": "Syncopation Index",
                "content": f"The Goldilocks Zone: {NEUROCHEMICAL_TARGETS['syncopation_index']['goldilocks_zone']['optimal']}. Too low (<5) is monotonous, too high (>50) is chaotic.",
                "type": "text"
            },
            {
                "title": "Groove Elements",
                "content": [
                    f"**{g['name']}**: {g['description']}. Example: {g['example']}"
                    for g in NEUROCHEMICAL_TARGETS["groove_elements"]
                ],
                "type": "list"
            },
            {
                "title": "Earworm Mechanics",
                "content": NEUROCHEMICAL_TARGETS["earworm_mechanics"]["elements"],
                "type": "list"
            },
            {
                "title": "Examples",
                "content": NEUROCHEMICAL_TARGETS["examples"],
                "type": "list"
            }
        ]
    
    elif field_name == "musical_effects":
        help_content["sections"] = [
            {
                "title": "Overview",
                "content": MUSICAL_EFFECTS["overview"],
                "type": "text"
            },
            {
                "title": "Balance Strength (Vocal/Instrumental Mix)",
                "content": MUSICAL_EFFECTS["balance_strength"]["recommendations"],
                "type": "key_value"
            },
            {
                "title": "Prompt Strength (CFG Scale)",
                "content": MUSICAL_EFFECTS["prompt_strength"]["recommendations"],
                "type": "key_value"
            },
            {
                "title": "Tag Ordering",
                "content": MUSICAL_EFFECTS["tag_ordering"]["recommended_order"],
                "type": "list"
            },
            {
                "title": "Examples",
                "content": MUSICAL_EFFECTS["examples"],
                "type": "list"
            }
        ]
    
    return help_content
