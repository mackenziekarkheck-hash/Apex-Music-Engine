Replit Agent Prompt
Role: Expert Backend Architect & AI Systems Engineer Objective: Migrate an existing music generation backend from Sonauto to Fal.ai (MiniMax Music 2.0). Context: We are switching providers to leverage better musical fidelity. Our frontend sends a complex JSON object with fields for "Seed Composition", "Description", "Neuropsychological Effects", "Neurochemical Targets", "Musical Effects", and "Lyrics". We need a new backend layer that uses OpenAI GPT-4o to intelligently map these fields into the strict schema required by Fal.ai.
Task: Generate a complete, multi-file implementation plan and code structure in Python (FastAPI/Flask compatible). You must also generate specific Markdown documentation for our autonomous agents to use as tools.

Part 1: Architecture & Logic Requirements
1. Semantic Orchestration (The "Translator")
We cannot simply map fields 1:1. You must implement a PayloadBuilder class that uses OpenAI GPT-4o to transform user intent into Fal.ai parameters.
Input: User UI JSON (Description, Neuro effects, Lyrics, etc.)
Output: Valid Fal.ai JSON payload.
Logic Rules for GPT-4o:
The "Split" Rule: "Musical Effects" from the UI must be analyzed.
If the effect is Timbral/Global (e.g., "Lo-fi", "Reverb", "Dark Mix"), it goes to prompt.
If the effect is Structural/Event-based (e.g., "Guitar Solo", "Drop", "Silence"), it goes to lyrics_prompt.
The "Translation" Rule:
Neuropsychological Effects (e.g., "Frisson") must be translated to acoustic descriptors (e.g., "dynamic crescendo, soaring harmony") and appended to prompt.
Neurochemical Targets (e.g., "Dopamine") must be translated to rhythmic descriptors (e.g., "repetitive hooks, syncopated bass") and appended to prompt.
The "Reference" Rule:
"Seed Composition" maps to reference_audio_url. This field is optional. If provided, it MUST be a valid HTTP URL pointing to an MP3/WAV file >15 seconds long.
2. Fal.ai API Implementation
Implement a robust client for fal-ai/minimax-music/v2.
Authentication: Use FAL_KEY environment variable.
Method: Async Queue Pattern (Submit -> Poll -> Retrieve).
Endpoints:
POST: https://queue.fal.run/fal-ai/minimax-music/v2
GET (Status): https://queue.fal.run/fal-ai/minimax-music/v2/requests/{request_id}/status
GET (Result): https://queue.fal.run/fal-ai/minimax-music/v2/requests/{request_id}
Constraints:
prompt: String, < 2000 chars (Optimize for < 500).
lyrics_prompt: String, < 3000 chars. Supports [Verse], [Chorus], and ## Instrumental ## syntax.
reference_audio_url: Optional.

Part 2: Deliverables (Code & Files)
Please generate the following files with the exact content described:
1. fal_client.py
A Python module containing:
A FalMusicClient class.
submit_generation(payload): Handles the POST request.
poll_status(request_id): Handles the exponential backoff polling logic.
Error handling for 4xx/5xx responses.
2. payload_factory.py
A Python module containing:
A function construct_payload_with_gpt(ui_data) that calls OpenAI API.
Include the System Prompt for GPT-4o within this file. The system prompt must explicitly enforce the "Split" and "Translation" rules defined above.
3. Agent Tool: tools/prompt_analyzer.md
A markdown file serving as a "System Instruction" for a validation agent. It must list:
Valid Content: Genre, Mood, Instrumentation, Timbre, BPM.
Invalid Content: Structural tags (Verse/Chorus), specific lyrics.
Validation Logic: "If the prompt contains square brackets ``, reject it and move tags to lyrics."
4. Agent Tool: tools/lyrics_validator.md
A markdown file serving as a "System Instruction" for a validation agent. It must list:
Required Syntax: At least one `` tag (Verse, Chorus, Intro).
Instrumental Syntax: Rules for using ## (e.g., ## Guitar Solo ##).
Pause Syntax: Rules for using double newlines \n\n for pauses.
Length Check: Max 3000 characters.

Part 3: Detailed API Specifications (Reference)
POST Request Schema (fal-ai/minimax-music/v2):
JSON
{
  "input": {
    "prompt": "String. Genre + translated Neuro effects + Timbral effects.",
    "lyrics_prompt": "String. [Verse] Lyrics... \n\n ## Instrumental Effect ##",
    "reference_audio_url": "String (URL). Optional. Must be > 15s.",
    "audio_setting": {
      "sample_rate": "44100",
      "bitrate": "256000",
      "format": "mp3"
    }
  },
  "webhookUrl": "Optional callback URL"
}

GPT-4o Logic for Field Merging: You must provide the exact prompt to be sent to GPT-4o. It should look like this:
"You are a Music Theory API Bridge.
ANALYZE 'Musical Effects': separate them into Timbre (Style) and Structure (Arrangement).
TRANSLATE 'Neuropsychological Effects' into acoustic descriptors (e.g., Frisson -> 'soaring dynamics').
TRANSLATE 'Neurochemical Targets' into rhythmic descriptors (e.g., Dopamine -> 'catchy hook').
MERGE Timbre + Translated Neuro Fields + Description into prompt.
MERGE Structure + Lyrics into lyrics_prompt using ## syntax for effects."

