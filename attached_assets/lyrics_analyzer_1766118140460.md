# Minimax Music v2: Prompt Analyzer & Optimization Framework

## 1. Executive Overview
This document serves as the technical specification for the "Prompt Analyzer," a validation layer designed to sit between the user interface and the Fal.ai `minimax-music/v2` endpoint. 

**Objective:** To mitigate the model's known "Vocal Bias," enforce strict schema compliance, and mathematically optimize prompt density for high-fidelity audio generation.

---

## 2. Hard Constraint Validation ("The Gatekeeper")
*These rules define the absolute boundaries of the API. Requests failing these checks must be rejected before transmission to save inference costs.*

### 2.1 Character Length Constraints
The v2 model has rigid context windows. Violating these results in immediate API 400 errors or model hallucination.

| Parameter | Min Chars | Max Chars | Severity | Logic Description |
| :--- | :--- | :--- | :--- | :--- |
| **Style Prompt** (`prompt`) | 10 | 300 | **CRITICAL** | < 10: Model lacks acoustic context. > 300: Truncate required. |
| **Lyrics Prompt** (`lyrics_prompt`) | 10 | 3000 | **CRITICAL** | < 10: Triggers instability/hallucination. > 3000: Exceeds context window. |

### 2.2 Schema & Parameter Compliance
* **Reference Audio:** `reference_audio_url` is **FORBIDDEN** on the standard v2 endpoint.
    * *Action:* If detected, strip parameter and issue warning: *"Reference audio is ignored by this endpoint. Use TextToMusicRequest or Voice Clone schemas instead."*
* **Negative Prompt:** `negative_prompt` is **UNSUPPORTED**.
    * *Action:* If detected, attempt to move keywords to the main prompt using exclusionary positive phrasing (e.g., convert "No Drums" to "Ambient, Beatless").

### 2.3 Audio Configuration Enums
The analyzer must validate `audio_settings` against specific distinct values to prevent validation errors.
* **Valid Sample Rates:** `{8000, 16000, 22050, 24000, 32000, 44100}`
    * *Optimization:* Default to `44100` (CD Quality).
* **Valid Bitrate:** Up to `256000`.
    * *Optimization:* Force `256000` for production renders.

---

## 3. Structural Optimization ("The Architect")
*These rules analyze the topology of the `lyrics_prompt` to ensure musical coherence and correct phrasing.*

### 3.1 Newline Density Analysis
The model uses `\n` tokens to determine breath control and musical phrasing.
* **Metric:** `Density_Score = Total_Characters / Total_Newlines`
* **Threshold:** If `Density_Score > 80`:
    * *Flag:* "Wall of Text Detected."
    * *Recommendation:* "Insert line breaks every 4–8 words to define musical bars."
* **Pause Detection:** Scan for `\n\n`.
    * *Logic:* If count == 0, warn: *"No instrumental pauses detected. Use double newlines to create breathing room between sections."*

### 3.2 Tagging Topology
The model requires state-change triggers to manage the energy curve.
* **Required Tags:** `[Verse]`, `[Chorus]`
* **Optional Tags:** `[Intro]`, `[Outro]`, `[Bridge]`
* **Validation Logic:**
    1.  Scan `lyrics_prompt` for bracketed tags.
    2.  **Error:** If 0 tags found -> *"Critical: Song lacks structure. Add [Verse]/[Chorus] markers."*
    3.  **Warning:** If `[Verse]` exists but `[Chorus]` is missing -> *"Linear structure detected. A Chorus is recommended for pop/rap structures."*

### 3.3 The Accompaniment Marker (`##`)
* **Syntax:** `## [Instrumental Description] ##`
* **Usage:** Validates that the user is attempting to force instrumental breaks correctly.
* **Check:** Ensure `##` markers are on their own lines or clearly separating sections.

---

## 4. Semantic Analysis ("The Producer")
*These rules analyze the `prompt` (style) content to maximize token efficiency and acoustic selection.*

### 4.1 The "Instrumental Paradox"
Minimax v2 is a vocal-centric model. Pure instrumental requests often fail.
* **Trigger:** Style prompt contains: `["Instrumental", "No vocals", "Karaoke", "Background music"]`
* **Conflict Check:** * IF (Trigger found) AND (Lyrics contain standard text words):
    * **CRITICAL WARNING:** *"Conflict Detected: You requested an Instrumental style but provided lyrics. The model will likely sing the lyrics. To achieve an instrumental, replace lyrics with non-lexical sounds or use '## Instrumental ##' tags."*

### 4.2 Token Efficiency & Stop-Word Removal
The 300-character limit demands high information density.
* **Stop-Words (Filler):** `["Make a", "Generate", "I want a", "song about", "track", "style", "audio"]`
* **Action:** Highlight these words for removal.
* **Heuristic:** Calculate `Descriptor_Density`.
    * *Goal:* High ratio of Adjectives/Nouns (Genre, Mood, Instruments) to Verbs/Articles.
    * *Prompt Start Check:* Ensure the first 5 words are **Descriptors** (e.g., "Fast, Aggressive, Trap") not **Requests** (e.g., "Please make a fast...").

---

## 5. Operational Workflow Recommendations
* **Queue vs. Subscribe:**
    * Due to generation times (~60s), the Analyzer recommends implementing `fal.queue` with a polling mechanism rather than `fal.subscribe` to avoid HTTP timeouts.
* **File Formats:**
    * **MP3:** Recommended for rapid iteration/drafting.
    * **FLAC:** Recommended only for final "Cherry-picked" exports for post-processing in DAWs.

---

## 6. Implementation Pseudo-Code
```python
def analyze_request(style_prompt, lyrics_prompt):
    # 1. HARD CONSTRAINTS
    if len(style_prompt) < 10 or len(style_prompt) > 300:
        return Error("Style prompt length invalid.")
    if len(lyrics_prompt) < 10 or len(lyrics_prompt) > 3000:
        return Error("Lyrics prompt length invalid.")

    # 2. SEMANTIC CHECKS
    if "instrumental" in style_prompt.lower() and len(lyrics_prompt) > 50:
        if "##" not in lyrics_prompt:
             return Warning("Instrumental Paradox: Use ## tags or remove lyrics.")

    # 3. STRUCTURAL CHECKS
    newlines = lyrics_prompt.count('\n')
    if len(lyrics_prompt) / (newlines + 1) > 80:
        return Advisory("Lyrics too dense. Add line breaks.")
    
    required_tags = ["[Verse]", "[Chorus]"]
    if not any(tag in lyrics_prompt for tag in required_tags):
        return Advisory("Missing structure tags ([Verse]/[Chorus]).")

    return Success("Prompt Validated.")