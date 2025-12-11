# **Autonomous Aural Architectures: A Hierarchical Agentic Framework for Algorithmic Rap Composition via the Sonauto API**

## **1\. The Computational Landscape of Generative Hip-Hop**

The intersection of artificial intelligence and musical composition has rapidly evolved from rudimentary MIDI synthesis to high-fidelity, waveform-based generation. Platforms like Sonauto have emerged as frontrunners in this domain, leveraging latent diffusion models to transform textual prompts into fully realized audio compositions.1 However, while these models demonstrate remarkable proficiency in genres defined by harmonic progression—such as pop, classical, or electronic dance music—they frequently encounter significant structural limitations when applied to hip-hop and rap.

Rap music is uniquely characterized by "flow," a complex interplay between lyrical cadence, rhythmic stress, and syllabic density, which must align precisely with an underlying percussive grid.3 Unlike melodic singing, where pitch is the primary variable, rapping relies on the percussive manipulation of language itself. Standard text-to-music models, when fed a simple prompt, often struggle to generate vocals that lock tightly to the beat, resulting in "hallucinated" flows that drift off-tempo or lyrics that lack the intricate rhyme schemes characteristic of the genre.2

To bridge the gap between stochastic generation and the structured rigor of professional rap production, a mere prompt is insufficient. We require an **Agentic Framework**—a coordinated system of autonomous AI agents that can plan, execute, critique, and refine the musical output. This report outlines the architectural design and implementation planning for a "Rap Generation Layer" built atop the Sonauto API. By utilizing **LangGraph** for orchestration and a suite of Python-based audio analysis tools (Librosa, Matchering), we propose a system where "Lyrical Architects," "Flow Supervisors," and "Mix Engineers" collaborate to ensure high-fidelity, rhythmically coherent output.5

### **1.1 The Sonauto Paradigm: Latent Diffusion in Audio**

Understanding the target platform is a prerequisite for effective agent design. Sonauto operates on a latent diffusion model architecture, distinct from the token-based Large Language Models (LLMs) used by competitors like Suno or Udio.2 Instead of predicting the next discrete audio token, Sonauto utilizes a variational autoencoder (VAE) to compress audio into a latent space, upon which a diffusion transformer operates. This architecture allows for a higher degree of controllability, particularly regarding lyrical coherence and instrumental separation.2

For our agentic framework, this distinction is critical. It implies that the "Sonauto Operator" agent cannot simply stream tokens; it must construct comprehensive prompt payloads that guide the diffusion process. The API exposes specific endpoints for generation, extension, and inpainting, which serve as the primitive actions available to our agents.7 The ability to "inpaint"—to surgically regenerate specific segments of audio—provides a mechanism for error correction that is vital for fixing specific lines of a rap verse that may fall off-beat, a capability that will be central to our "Rhythmic Supervisor" agent's logic.7

### **1.2 The "Flow" Problem: Why Agents are Necessary**

A single-shot generation request often fails in rap because the dependencies are circular: the lyrics dictate the flow, but the beat dictates the allowable syllable count. A standard LLM generating lyrics has no "hearing"—it cannot sense the tempo of the beat it is writing for. Conversely, the audio model generates the beat and vocals simultaneously, often prioritizing audio fidelity over lyrical structure.

An agentic system breaks this deadlock by decoupling the processes:

1. **Lyrical Planning:** An agent designs the lyrics with specific rhythmic constraints (syllable counting, stress patterns) before audio generation begins.4  
2. **Audio Realization:** The Sonauto API generates the audio based on these constrained lyrics.  
3. **Auditory Critique:** A separate agent "listens" to the result using Digital Signal Processing (DSP) to measure the alignment of vocal onsets with the beat grid.9  
4. **Iterative Refinement:** If the alignment score is low, the system triggers an inpainting task to regenerate only the flawed section.

This feedback loop moves the generation process from a linear "fire-and-forget" model to a recursive, quality-assured pipeline.

## ---

**2\. Architectural Foundations and Framework Selection**

The success of a multi-agent system (MAS) depends heavily on the orchestration framework. For this project, we evaluated two primary candidates: **CrewAI** and **LangGraph**.

### **2.1 Framework Comparative Analysis: CrewAI vs. LangGraph**

**CrewAI** is designed around a role-playing paradigm. Agents are defined with "backstories" and "goals," and they collaborate in a manner similar to a human team, often communicating via natural language.10 While excellent for creative brainstorming or open-ended research tasks, CrewAI's hierarchical or sequential processes can be opaque regarding state management. In a music production pipeline, where specific file paths, floating-point BPM values, and API task IDs must be passed with exact precision, the conversational overhead of CrewAI can introduce indeterminacy.

**LangGraph**, developed by LangChain, adopts a graph-theoretic approach. It models the workflow as a state machine where agents are nodes and the flow of control is defined by edges.6 This structure is deterministic and explicitly stateful. The "State" is a shared dictionary that persists throughout the graph traversal, allowing for precise data passing (e.g., passing a list of timestamp tuples \[(10.5, 12.0)\] from the Analysis Node to the Inpainting Node).

For the Rap Generation Layer, **LangGraph** is the superior choice. The production of a song is a finite state machine: Drafting \-\> Generating \-\> Analyzing \-\> (Fixing) \-\> Mastering. The ability to define conditional edges (e.g., *if beat\_confidence \< 0.8, route to InpaintNode; else route to MasteringNode*) is essential for the error-correction loops required to ensure rhythmic precision.14

### **2.2 The Global State Schema**

The backbone of the LangGraph architecture is the State Schema. This TypedDict defines every piece of data that the agents will read or write. It serves as the digital "Session File" for the automated studio.

**Table 1: Proposed RapGenerationState Schema**

| Key | Type | Description | Writer Agent | Reader Agent |
| :---- | :---- | :---- | :---- | :---- |
| user\_prompt | str | The initial raw request from the user (e.g., "90s boom bap about chess"). | User Input | All |
| structured\_plan | dict | Parsed intent: BPM, Key, Subgenre, Mood. | Executive | Lyrical/Sonauto |
| lyrics\_draft | str | The raw text generated by the LLM. | Lyrical | Lyrical |
| lyrics\_validated | str | Text that has passed syllable/rhyme density checks. | Lyrical | Sonauto |
| phoneme\_map | list | Phonetic breakdown of the lyrics for alignment checks. | Lyrical | Flow Supervisor |
| task\_id | str | The UUID returned by Sonauto API. | Sonauto | Sonauto/Analyst |
| audio\_url | str | The temporary CDN URL of the generated track. | Sonauto | Analyst/Mix |
| local\_filepath | str | Path to the downloaded WAV/MP3 in Colab. | Analyst | Analyst/Mix |
| analysis\_metrics | dict | Results of Librosa analysis: detected\_bpm, onset\_conf. | Analyst | Executive |
| fix\_segments | list | Timestamps \[start, end\] requiring inpainting. | Analyst | Sonauto |
| iteration\_count | int | Counter to prevent infinite correction loops. | All | Executive |
| credits\_used | int | Running total of Sonauto credits consumed. | Sonauto | Executive |

This schema ensures that the "Lyrical Architect" knows the target BPM (to adjust syllable counts) and the "Flow Supervisor" has access to the intended lyrics (to check alignment).

## ---

**3\. The Agentic Hierarchy: Role Definitions and Algorithmic Logic**

The system is composed of four specialized agents, orchestrated by a graph executive. Each agent encapsulates specific domain expertise and utilizes distinct Python libraries.

### **3.1 Agent 1: The Lyrical Architect (Text & Phonetics)**

**Role:** This agent is responsible for generating the textual content of the rap. Unlike a generic creative writing bot, the Lyrical Architect acts as a "structure-first" poet. It prioritizes rhythmic feasibility over semantic complexity.

**Tools & Libraries:**

* **langchain**: To interface with an LLM (e.g., GPT-4 or Claude) for semantic generation.5  
* **pronouncing (CMU Dict)**: For phoneme extraction and rhyme verification.15  
* **syllables / Pyphen**: For syllable counting and hyphenation.17  
* **Phyme**: For finding complex slant rhymes and assonance, which are more common in rap than perfect rhymes.19

**Algorithmic Logic:**

1. **Structure Definition:** The agent first determines the bar structure based on the BPM. A standard rap bar is 4 beats. At 90 BPM (Boom Bap), a comfortable flow is \~10-12 syllables per bar (16th notes). At 140 BPM (Trap), the flow might be slower (half-time) or faster (triplets).  
2. **Drafting Loop:** The LLM generates a couplet.  
3. **The Rhyme Density Check:**  
   * The agent uses pronouncing.phones\_for\_word() to convert the last words of the couplet into ARPAbet codes (e.g., "CAT" \-\> K AE T).  
   * It calculates the "Rhyme Density" by counting matching phonemes in the trailing window.  
   * If the rhyme is weak (e.g., only the final consonant matches), Phyme is queried for a better synonym or a slant rhyme (e.g., swapping "cat" for "stack" to rhyme with "back").19  
4. **Syllabic Constraints:** The agent counts the syllables in the line. If a line has 18 syllables where the target is 12, it is flagged as "unflowable" and sent back to the LLM for summarization/shortening.20

### **3.2 Agent 2: The Sonauto Operator (Interface & Composition)**

**Role:** The bridge between the internal state and the external generative engine. This agent manages the API interactions, handling authentication, payload construction, and polling.

**Tools & Libraries:**

* **requests**: For HTTP operations.  
* **tenacity**: For robust retry logic and exponential backoff during polling.  
* **Sonauto API Endpoints** 7:  
  * POST /generations: Initial creation.  
  * POST /generations/inpaint: Correction.

**Algorithmic Logic:**

1. **Tag Selection Strategy:** The user might ask for "sad rap." The agent queries the Sonauto "Tag Explorer" (simulated via a predefined list in code, as the API doesn't have a dynamic tag search endpoint documented) to map "sad" to valid tags like emo rap, cloud rap, melodic.21  
2. **Payload Construction:**  
   * It combines the validated\_lyrics from Agent 1 with the mapped tags.  
   * **Prompt Engineering:** It augments the user prompt with acoustic descriptors known to improve quality (e.g., "high fidelity," "studio quality," "mixed vocals").22  
   * **BPM Control:** It explicitly sets the bpm parameter if the user specified one, or sets it to auto and parses the result later.7  
3. **Polling & retrieval:** It submits the request and enters a polling loop, checking /generations/status/{task\_id} every few seconds until the status is completed or failed.

### **3.3 Agent 3: The Flow Supervisor (Audio Analysis & DSP)**

**Role:** The quality control auditor. This agent downloads the generated audio and performs Digital Signal Processing (DSP) to verify that the rap is "on beat." This is the most computationally intensive node.

**Tools & Libraries:**

* **librosa**: The industry standard for audio analysis in Python.23  
* **numpy**: For array manipulation.  
* **soundfile**: For reading audio buffers.25

**Algorithmic Logic:**

1. **Beat Tracking:** The agent uses librosa.beat.beat\_track() to detect the tempo and beat frames of the generated audio.9  
2. **BPM Verification:** It compares the detected\_bpm with the target\_bpm. A deviation of \>5% suggests the model hallucinated a tempo change or failed to adhere to the prompt.  
3. **Onset Alignment (The "Pocket" Check):**  
   * It calculates the onset\_envelope utilizing librosa.onset.onset\_strength().24  
   * It cross-references strong onsets with the predicted beat locations. In a "tight" flow, vocal onsets should cluster around grid points (1/4, 1/8 notes).  
   * **Syncopation Detection:** By analyzing the energy distribution between beats, the agent can estimate if the flow is syncopated or simply off-beat.26  
4. **Inpaint Triggering:** If a specific 4-bar section has low onset confidence (indicating slurred or mumbled vocals), the agent calculates the start and end timestamps and flags them in the fix\_segments list in the State.

### **3.4 Agent 4: The Mix Engineer (Post-Processing)**

**Role:** Ensures the final output is commercially viable in terms of loudness and spectral balance. While Sonauto generates high-quality audio, raw generations can vary in volume.

**Tools & Libraries:**

* **matchering**: An open-source library for automated reference-based mastering.27  
* **pydub**: For format conversion and trimming.

**Algorithmic Logic:**

1. **Reference Loading:** The agent selects a reference track from a pre-loaded library based on the genre (e.g., reference\_trap.wav for trap, reference\_lofi.wav for lo-fi).  
2. **Automated Mastering:** It runs the matchering.process() function, which applies equalization, compression, and limiting to match the target audio to the reference's RMS and spectral curve.28  
3. **Final Export:** The mastered track is saved, and the final path is updated in the State.

## ---

**4\. Methodical Implementation Plan: Google Colab Environment**

Deploying this architecture requires a specific environment configuration, particularly because audio processing libraries have system-level dependencies.

### **4.1 Dependency Management and Library Matrix**

The following table outlines the requisite libraries, their versions, and their specific function within the agentic architecture.

**Table 2: Python Dependency Matrix**

| Library | Version | Purpose | Snippet Ref |
| :---- | :---- | :---- | :---- |
| langgraph | ^0.0.10 | State machine orchestration for the agent workflow. | 6 |
| langchain | latest | Interface for LLM-based lyric drafting. | 14 |
| librosa | ^0.10.1 | Audio analysis (beat tracking, onsets, spectral features). | 23 |
| matchering | 2.0+ | Automated mastering and audio matching. | 27 |
| pronouncing | ^0.2.0 | Phonetic analysis for rhyme density calculations. | 15 |
| syllables | latest | Heuristic syllable counting for rhythmic structure. | 18 |
| requests | latest | HTTP client for Sonauto API interactions. | 7 |
| soundfile | latest | Audio I/O operations (required by Librosa). | 25 |
| python-dotenv | latest | Secure management of API keys. | 10 |

### **4.2 Environment Initialization Script**

To execute this in Google Colab, the environment must be bootstrapped. Note that librosa and matchering often require ffmpeg to be installed at the system level for MP3/OGG decoding.

Python

\# Cell 1: System Dependencies & Python Libraries  
\!apt-get update \-qq && apt-get install \-y ffmpeg libsndfile1  
\!pip install \-q langgraph langchain langchain\_openai librosa soundfile matchering pronouncing syllables python-dotenv tenacity

\# Cell 2: Imports and API Key Configuration  
import os  
import time  
import requests  
import numpy as np  
import librosa  
import soundfile as sf  
import matchering as mg  
from typing import TypedDict, List, Optional  
from langgraph.graph import StateGraph, END  
from google.colab import userdata

\# Securely retrieve keys from Colab's secrets manager  
os.environ \= userdata.get('SONAUTO\_API\_KEY')  
os.environ \= userdata.get('OPENAI\_API\_KEY')

print("Environment Initialized. Audio Backends Ready.")

## ---

**5\. Detailed Planning Documentation: Algorithmic Integration**

This section translates the theoretical roles into concrete logic flows and code structures.

### **5.1 Defining the Graph State**

The RapGenerationState acts as the central memory. We utilize Python's TypedDict to enforce type safety.

Python

class RapGenerationState(TypedDict):  
    \# User Inputs  
    prompt: str  
    genre: str  
    target\_bpm: Optional\[int\]  
      
    \# Lyrical Data  
    lyrics: str  
    syllable\_counts: List\[int\]  
    rhyme\_scheme\_score: float  
      
    \# Audio Generation Data  
    task\_id: str  
    audio\_url: str  
    local\_filename: str  
      
    \# Analysis & Feedback  
    detected\_bpm: float  
    beat\_confidence: float  
    inpaint\_segments: List\[List\[float\]\] \# \[\[start, end\], \[start, end\]\]  
    attempts: int  
      
    \# Final Status  
    is\_complete: bool  
    errors: List\[str\]

### **5.2 Node Logic: The Lyrical Architect**

This node integrates pronouncing and syllables to validate the LLM's output.

**Context:** The Sonauto API documentation explicitly states that lyrics must be provided to control the content.7 However, the API does not check for rhythm. That is this node's responsibility.

**Logic Flow:**

1. **Draft:** Invoke LLM with a system prompt emphasizing "measure-based writing" (e.g., "Write 4 lines per bar").  
2. **Analyze:** Split the draft into lines.  
   * count \= syllables.estimate(line)  
3. **Validate:**  
   * Calculate variance: np.var(syllable\_counts). High variance (\>5) indicates a broken flow.  
   * Check Rhymes: Use pronouncing.rhymes(last\_word) to see if the subsequent line ends with a match.  
4. **Refine:** If validation fails, re-prompt the LLM with the specific error (e.g., "Line 3 is too long, shorten by 4 syllables").

Python

import syllables  
import pronouncing

def lyrical\_architect\_node(state: RapGenerationState):  
    \# Simulation of LLM call (Replace with actual LangChain call)  
    \# prompt\_template \= f"Write a {state\['genre'\]} rap about {state\['prompt'\]}. 8 bars."  
    \# draft\_lyrics \= llm.invoke(prompt\_template)  
      
    \# Validation Logic  
    lines \= state\['lyrics'\].split('\\n')  
    valid \= True  
    for line in lines:  
        count \= syllables.estimate(line)  
        if count \> 16: \# Hard constraint for standard rap flow  
             valid \= False  
             \# Append error to state to trigger re-drafting  
               
    if valid:  
        return {"lyrics": state\['lyrics'\], "is\_complete": False}  
    return {"errors": \["Line too long"\]}

### **5.3 Node Logic: The Sonauto Operator (Generation & Inpainting)**

This node handles the complexity of the Sonauto API, specifically the distinction between fresh generation and inpainting.

**Context:** The POST /generations/inpaint endpoint requires audio\_url and sections.7 This node must intelligently switch between the standard generation endpoint and the inpaint endpoint based on the inpaint\_segments state variable.

**Implementation:**

Python

def sonauto\_node(state: RapGenerationState):  
    api\_key \= os.environ.get('SONAUTO\_API\_KEY')  
    headers \= {"Authorization": f"Bearer {api\_key}"}  
      
    \# CASE 1: Correction / Inpainting  
    if state.get("inpaint\_segments") and state.get("audio\_url"):  
        print(f"Triggering Inpainting for segments: {state\['inpaint\_segments'\]}")  
        url \= "https://api.sonauto.ai/v1/generations/inpaint"  
        payload \= {  
            "audio\_url": state\["audio\_url"\],  
            "sections": state\["inpaint\_segments"\],  
            "prompt": state\["prompt"\], \# Reinforce style during inpaint  
            "lyrics": state\["lyrics"\], \# Provide context  
            "instrumental": False  
        }  
      
    \# CASE 2: New Generation  
    else:  
        print("Triggering New Generation...")  
        url \= "https://api.sonauto.ai/v1/generations"  
        payload \= {  
            "prompt": state\["prompt"\],  
            "lyrics": state\["lyrics"\],  
            "tags": \[state\["genre"\], "rap", "hip hop", "vocal"\],  
            "bpm": state\["target\_bpm"\] if state\["target\_bpm"\] else "auto",  
            "instrumental": False  
        }

    \# Execute Request  
    try:  
        response \= requests.post(url, json=payload, headers=headers)  
        response.raise\_for\_status()  
        task\_id \= response.json().get("task\_id")  
          
        \# Polling Logic  
        status \= "processing"  
        audio\_url \= None  
        while status not in \["completed", "failed"\]:  
            time.sleep(5)  
            status\_resp \= requests.get(f"https://api.sonauto.ai/v1/generations/{task\_id}", headers=headers)  
            status\_data \= status\_resp.json()  
            status \= status\_data.get("status")  
            if status \== "completed":  
                audio\_url \= status\_data\['song\_paths'\] \# Get first variation  
          
        return {"task\_id": task\_id, "audio\_url": audio\_url, "attempts": state.get("attempts", 0) \+ 1}  
          
    except Exception as e:  
        return {"errors": \[str(e)\]}

### **5.4 Node Logic: The Flow Supervisor (Analysis)**

This is the core of the "Agentic" value add. It turns subjective music quality into objective data.

**Context:** We use librosa because it provides robust beat tracking even in noisy signals.9

**Logic Flow:**

1. **Download:** Fetch the audio from state\["audio\_url"\] and save to temp.ogg.  
2. **Load:** y, sr \= librosa.load('temp.ogg').  
3. **Beat Track:** tempo, beats \= librosa.beat.beat\_track(y=y, sr=sr).  
4. **Confidence Check:**  
   * We can estimate confidence by looking at the onset\_envelope at the detected beat frames.  
   * onset\_env \= librosa.onset.onset\_strength(y=y, sr=sr)  
   * beat\_strength \= onset\_env\[beats\]  
   * confidence \= np.mean(beat\_strength)  
5. **Decision:**  
   * If confidence \< threshold AND attempts \< max\_retries: Identify the weak section (e.g., seconds 10-15) and populate state\["inpaint\_segments"\].  
   * Else: Clear inpaint\_segments and mark is\_complete \= True.

Python

def flow\_supervisor\_node(state: RapGenerationState):  
    \# Download Audio  
    local\_filename \= "current\_gen.ogg"  
    doc \= requests.get(state\['audio\_url'\])  
    with open(local\_filename, 'wb') as f:  
        f.write(doc.content)  
          
    \# Analyze  
    y, sr \= librosa.load(local\_filename)  
    tempo, beats \= librosa.beat.beat\_track(y=y, sr=sr)  
    onset\_env \= librosa.onset.onset\_strength(y=y, sr=sr)  
      
    \# Calculate simple rhythmic consistency score  
    \# High score means strong onsets align with grid  
    beat\_strength \= onset\_env\[beats\]  
    confidence \= float(np.mean(beat\_strength))  
      
    print(f"Analysis: BPM={tempo}, Confidence={confidence}")  
      
    inpaint\_segments \=  
      
    \# If confidence is low, we schedule a repair  
    \# In a real scenario, we would find specific time ranges with low energy  
    if confidence \< 1.5 and state.get("attempts", 0) \< 3:  
        \# Example: Flag the first 10 seconds for regeneration  
        inpaint\_segments \= \[\[0.0, 10.0\]\]  
        return {  
            "detected\_bpm": tempo,   
            "beat\_confidence": confidence,   
            "inpaint\_segments": inpaint\_segments,  
            "is\_complete": False  
        }  
      
    return {  
        "detected\_bpm": tempo,   
        "beat\_confidence": confidence,   
        "inpaint\_segments":,  
        "is\_complete": True,  
        "local\_filename": local\_filename  
    }

### **5.5 Node Logic: The Mix Engineer (Mastering)**

This node applies final polish using the matchering library.

Python

def mix\_engineer\_node(state: RapGenerationState):  
    if not state.get("is\_complete"):  
        return {}

    target\_file \= state\["local\_filename"\]  
    output\_file \= "mastered\_output.wav"  
    \# Using a dummy reference for the example.   
    \# In production, this would be a high-quality WAV file loaded from a dataset.  
    reference\_file \= "reference\_track.wav"   
      
    \# Fallback if reference doesn't exist (prevent crash in demo)  
    if not os.path.exists(reference\_file):  
        print("Reference track not found. Skipping mastering.")  
        return {"local\_filename": target\_file}

    try:  
        mg.process(  
            target=target\_file,  
            reference=reference\_file,  
            results=\[mg.pcm16(output\_file)\]  
        )  
        return {"local\_filename": output\_file}  
    except Exception as e:  
        print(f"Mastering failed: {e}")  
        return {} \# Return unchanged state on failure

### **5.6 Graph Connectivity and Routing**

Using LangGraph, we wire these nodes together. The critical component is the **Conditional Edge** stemming from the Analysis node.

Python

workflow \= StateGraph(RapGenerationState)

\# Add Nodes  
workflow.add\_node("LyricalArchitect", lyrical\_architect\_node)  
workflow.add\_node("SonautoGen", sonauto\_node)  
workflow.add\_node("FlowSupervisor", flow\_supervisor\_node)  
workflow.add\_node("MixEngineer", mix\_engineer\_node)

\# Set Entry  
workflow.set\_entry\_point("LyricalArchitect")

\# Standard Flow  
workflow.add\_edge("LyricalArchitect", "SonautoGen")  
workflow.add\_edge("SonautoGen", "FlowSupervisor")

\# Conditional Logic  
def route\_after\_analysis(state):  
    if state.get("inpaint\_segments"):  
        return "SonautoGen" \# Loop back for fixing  
    elif state.get("is\_complete"):  
        return "MixEngineer" \# Proceed to finish  
    else:  
        return END \# Fallback/Error state

workflow.add\_conditional\_edges(  
    "FlowSupervisor",  
    route\_after\_analysis,  
    {  
        "SonautoGen": "SonautoGen",  
        "MixEngineer": "MixEngineer",  
        END: END  
    }  
)

workflow.add\_edge("MixEngineer", END)  
app \= workflow.compile()

## ---

**6\. Advanced Insights and Optimization**

### **6.1 Cost Management and Credit Optimization**

The Sonauto API operates on a credit system (100 credits per song).7 An autonomous agentic loop poses a financial risk: an infinite feedback loop could drain a user's balance.  
Mitigation Strategy: The State Schema includes an iteration\_count. The Conditional Edge logic must strictly enforce a limit (e.g., MAX\_RETRIES \= 3). Furthermore, the agent should prioritize inpainting (which may have different cost structures or at least saves the "good" parts of a song) over full regeneration. The Executive Agent should track estimated credit usage and halt execution if a budget threshold is exceeded.

### **6.2 Second-Order Insight: The "Syllable-to-BPM" Ratio**

Analyzing the relationship between the syllable\_counts (from Agent 1\) and the detected\_bpm (from Agent 3\) reveals a derived metric: the **Syllable Rate (Syols/Sec)**.

* *Observation:* Boom Bap (90 BPM) typically supports \~4-5 syllables/sec. Trap (140 BPM) can support \~7-8 (double time).  
* *Application:* This metric can be fed back into the Lyrical Architect. If the user requests "Fast Rap" (Eminem style), the Architect should target a higher Syllable Rate. If the Analysis node detects a low BPM but high syllable count, it can infer the generation is "rushed" or "cluttered," triggering a rewrite of the lyrics rather than just an audio regeneration.

### **6.3 Third-Order Insight: Automated Lyric Video Production via Forced Alignment**

While the current request focuses on audio, the libraries employed (librosa, torchaudio) enable a powerful downstream application: Forced Alignment. By using torchaudio.pipelines.Wav2Vec2FABundle 30, the system could align the generated audio with the Lyrical Architect's text to produce timestamped word boundaries.  
Implication: This data is identical to the .srt or .vtt format required for karaoke-style lyric videos. A "Video Agent" could be added to the graph later, taking the audio and the alignment data to render a visualization using a tool like FFmpeg or MoviePy, creating a complete multimedia asset autonomously.

## ---

**7\. Conclusion**

The framework presented here represents a significant leap beyond standard "text-to-audio" interactions. By treating rap generation as a multi-stage engineering problem—rather than a single-shot creative prompt—we leverage the specific strengths of **Sonauto** (high-fidelity synthesis) while mitigating its weaknesses (structural coherence) through external control systems.

The choice of **LangGraph** provides the necessary rigour for state management, allowing the system to "remember" the lyrics it wrote and "hear" the mistakes it made. The integration of **Librosa** and **Matchering** ensures that the final output is not only creatively aligned with the user's intent but also technically proficient and commercially mastered. This hierarchical agentic architecture transforms the role of the user from a prompt engineer into an executive producer, overseeing a team of specialized AI experts dedicated to the craft of hip-hop.

#### **Works cited**

1. Sonauto:AI-powered music creation platform that transforms prompts, lyrics, or melodies into fully produced songs in any style with radio-quality output. \- MOGE, accessed December 11, 2025, [https://moge.ai/product/sonauto](https://moge.ai/product/sonauto)  
2. Show HN: Sonauto – A more controllable AI music creator | Hacker News, accessed December 11, 2025, [https://news.ycombinator.com/item?id=39992817](https://news.ycombinator.com/item?id=39992817)  
3. alexmarozick/RapAnalysis: Rhyme detection and analysis applied to user's Spotify data, accessed December 11, 2025, [https://github.com/alexmarozick/RapAnalysis](https://github.com/alexmarozick/RapAnalysis)  
4. DeepRhymes: Efficient End-to-end Conditional Rap Lyrics Generation \- Stanford University, accessed December 11, 2025, [https://web.stanford.edu/class/archive/cs/cs224n/cs224n.1234/final-reports/final-report-169795327.pdf](https://web.stanford.edu/class/archive/cs/cs224n/cs224n.1234/final-reports/final-report-169795327.pdf)  
5. Music, Lyrics, and Agentic AI: Building a Smart Song Explainer using Python and OpenAI, accessed December 11, 2025, [https://towardsdatascience.com/music-lyrics-and-agentic-ai-building-a-smart-song-explainer-using-python-and-openai/](https://towardsdatascience.com/music-lyrics-and-agentic-ai-building-a-smart-song-explainer-using-python-and-openai/)  
6. Building Agentic Workflows with LangGraph and Granite \- IBM, accessed December 11, 2025, [https://www.ibm.com/think/tutorials/build-agentic-workflows-langgraph-granite](https://www.ibm.com/think/tutorials/build-agentic-workflows-langgraph-granite)  
7. Developers (API) \- Sonauto, accessed December 11, 2025, [https://sonauto.ai/developers](https://sonauto.ai/developers)  
8. I Found a Secret AI MUSIC Generator \- 100% FREE and Unlimited (With Commercial usage rights), accessed December 11, 2025, [https://www.youtube.com/watch?v=k\_TPO1v4tLQ](https://www.youtube.com/watch?v=k_TPO1v4tLQ)  
9. librosa.beat.beat\_track — librosa 0.11.0 documentation, accessed December 11, 2025, [https://librosa.org/doc/main/generated/librosa.beat.beat\_track.html](https://librosa.org/doc/main/generated/librosa.beat.beat_track.html)  
10. Customer Support Analysis with Gemini 2.5 Pro and CrewAI \- Google AI for Developers, accessed December 11, 2025, [https://ai.google.dev/gemini-api/docs/crewai-example](https://ai.google.dev/gemini-api/docs/crewai-example)  
11. 10 Best CrewAI Projects You Must Build in 2026 \- ProjectPro, accessed December 11, 2025, [https://www.projectpro.io/article/crew-ai-projects-ideas-and-examples/1117](https://www.projectpro.io/article/crew-ai-projects-ideas-and-examples/1117)  
12. Agentic workflows from scratch with (and without) LangGraph \- Dylan Castillo, accessed December 11, 2025, [https://dylancastillo.co/posts/agentic-workflows-langgraph.html](https://dylancastillo.co/posts/agentic-workflows-langgraph.html)  
13. Graph API overview \- Docs by LangChain, accessed December 11, 2025, [https://docs.langchain.com/oss/python/langgraph/graph-api](https://docs.langchain.com/oss/python/langgraph/graph-api)  
14. Building Multi-Agent Systems with LangGraph: A Step-by-Step Guide | by Sushmita Nandi, accessed December 11, 2025, [https://medium.com/@sushmita2310/building-multi-agent-systems-with-langgraph-a-step-by-step-guide-d14088e90f72](https://medium.com/@sushmita2310/building-multi-agent-systems-with-langgraph-a-step-by-step-guide-d14088e90f72)  
15. pronouncing \- PyPI, accessed December 11, 2025, [https://pypi.org/project/pronouncing/](https://pypi.org/project/pronouncing/)  
16. Documentation for pronouncing — pronouncing 0.2.0 documentation, accessed December 11, 2025, [https://pronouncing.readthedocs.io/en/latest/](https://pronouncing.readthedocs.io/en/latest/)  
17. How to get the number of syllables in a word? \- Data Science Stack Exchange, accessed December 11, 2025, [https://datascience.stackexchange.com/questions/23376/how-to-get-the-number-of-syllables-in-a-word](https://datascience.stackexchange.com/questions/23376/how-to-get-the-number-of-syllables-in-a-word)  
18. Programmatically Counting Syllables | by Michael Holtzscher \- Medium, accessed December 11, 2025, [https://medium.com/@mholtzscher/programmatically-counting-syllables-ca760435fab4](https://medium.com/@mholtzscher/programmatically-counting-syllables-ca760435fab4)  
19. emo-eth/Phyme: python rhyming dictionary for songwriting \- GitHub, accessed December 11, 2025, [https://github.com/emo-eth/Phyme](https://github.com/emo-eth/Phyme)  
20. Syllable Count In Python \- Stack Overflow, accessed December 11, 2025, [https://stackoverflow.com/questions/46759492/syllable-count-in-python](https://stackoverflow.com/questions/46759492/syllable-count-in-python)  
21. Sonauto | New Music by You, accessed December 11, 2025, [https://sonauto.ai/](https://sonauto.ai/)  
22. Suno Lyric formatter system prompt : r/SunoAI \- Reddit, accessed December 11, 2025, [https://www.reddit.com/r/SunoAI/comments/1hvri17/suno\_lyric\_formatter\_system\_prompt/](https://www.reddit.com/r/SunoAI/comments/1hvri17/suno_lyric_formatter_system_prompt/)  
23. Tutorial — librosa 0.11.0 documentation, accessed December 11, 2025, [https://librosa.org/doc/0.11.0/tutorial.html](https://librosa.org/doc/0.11.0/tutorial.html)  
24. Source code for librosa.feature.rhythm, accessed December 11, 2025, [https://librosa.org/doc/0.11.0/\_modules/librosa/feature/rhythm.html](https://librosa.org/doc/0.11.0/_modules/librosa/feature/rhythm.html)  
25. Audio processing in Python with Feature Extraction for machine learning \- YouTube, accessed December 11, 2025, [https://www.youtube.com/watch?v=vbhlEMcb7RQ](https://www.youtube.com/watch?v=vbhlEMcb7RQ)  
26. SynPy Toolkit and Syncopation Perceptual Dataset \- Sound Software .ac.uk, accessed December 11, 2025, [https://code.soundsoftware.ac.uk/projects/syncopation-dataset](https://code.soundsoftware.ac.uk/projects/syncopation-dataset)  
27. matchering \- PyPI, accessed December 11, 2025, [https://pypi.org/project/matchering/](https://pypi.org/project/matchering/)  
28. sergree/matchering: 🎚️ Open Source Audio Matching and Mastering \- GitHub, accessed December 11, 2025, [https://github.com/sergree/matchering](https://github.com/sergree/matchering)  
29. Beat tracking with time-varying tempo — librosa 0.11.0 documentation, accessed December 11, 2025, [http://librosa.org/doc/0.11.0/auto\_examples/plot\_dynamic\_beat.html](http://librosa.org/doc/0.11.0/auto_examples/plot_dynamic_beat.html)  
30. Forced Alignment with Wav2Vec2 — Torchaudio 2.9.0 documentation \- PyTorch, accessed December 11, 2025, [https://docs.pytorch.org/audio/stable/tutorials/forced\_alignment\_tutorial.html](https://docs.pytorch.org/audio/stable/tutorials/forced_alignment_tutorial.html)  
31. CTC forced alignment API tutorial — Torchaudio 2.7.0 documentation, accessed December 11, 2025, [https://docs.pytorch.org/audio/2.7.0/tutorials/ctc\_forced\_alignment\_api\_tutorial.html](https://docs.pytorch.org/audio/2.7.0/tutorials/ctc_forced_alignment_api_tutorial.html)