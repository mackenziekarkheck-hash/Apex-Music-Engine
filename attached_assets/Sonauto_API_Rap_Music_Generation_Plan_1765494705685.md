# **Comprehensive Technical Documentation and Implementation Strategy for Sonauto API Integration in Generative Rap Production**

## **1\. Architectural Overview and System Design**

The convergence of computational linguistics and digital signal processing has birthed a new era of generative audio, where intent-based synthesis replaces traditional sample-based composition. This report serves as the definitive technical manual for integrating the Sonauto API into a Python-based, multi-agent cognitive architecture hosted within Google Colab. The objective is to architect a system where autonomous agents—functioning as Lyricists, Composers, and Producers—collaborate to synthesize highly optimized payloads for the Sonauto inference engine, specifically targeting the nuanced acoustic and lyrical requirements of the Rap and Hip-Hop genres.

### **1.1 The Paradigm Shift: From DAW to API**

In a traditional Digital Audio Workstation (DAW) environment, music production is a linear accumulation of discrete audio events. In contrast, the Sonauto API leverages latent diffusion models to generate spectral data from semantic inputs.1 For the developer, this shifts the focus from mixing and mastering to *prompt engineering* and *parameter optimization*. The API acts as a black-box synthesizer where the quality of the output is deterministically linked to the specificity and structural integrity of the input JSON payload.

The architecture proposed herein utilizes a modular client-server pattern. The client, running in a Google Colab ephemeral runtime, orchestrates the lifecycle of a music generation task. This involves three distinct phases:

1. **Pre-processing and Synthesis:** Multi-agent collaboration to generate valid lyrics, style tags, and natural language prompts.  
2. **Transmission and Inference:** Secure serialization of these inputs into an HTTP POST request to the api.sonauto.ai/v1/generations endpoint.1  
3. **Asynchronous Retrieval:** A polling-based watcher service that monitors task status and retrieves binary audio assets upon completion.1

### **1.2 The Sonauto Interface Specification**

The Sonauto API is a RESTful service operating over HTTPS. It exposes resources for generation, status checking, and asset retrieval. The primary interface for your application will be the /generations endpoint, which accepts a JSON body containing the creative DNA of the track.

The system is designed to be stateless; every request is independent, though consistency can be enforced via seed parameters.1 This property is particularly advantageous for a multi-agent system, as it allows for parallel generation of variations (A/B testing flows or beats) without session management overhead.

### **1.3 Rap and Hip-Hop Specificity**

Generating rap music presents unique challenges for AI models compared to melodic genres like pop or country. Rap relies heavily on *cadence*, *flow*, and *lyrical density*.

* **Flow:** The rhythmic delivery of lyrics must align with the beat.  
* **Intelligibility:** The model must prioritize vocal clarity over instrumental density.  
* **Structure:** Hip-hop songs often follow rigid structures (e.g., 16-bar verses, 8-bar hooks).

To address these, our implementation will heavily leverage Sonauto's lyrics parameter with structural meta-tags (e.g., \[Verse\], \[Chorus\]) and the balance\_strength parameter to ensure vocal prominence.3 The "Composer" agent must also be adept at navigating the specific taxonomy of Sonauto’s style tags—distinguishing between "Trap," "Boom Bap," and "Drill"—to ensure the rhythmic substrate matches the lyrical intent.5

## ---

**2\. Environment Configuration and Security Protocols**

Before code execution can commence, the runtime environment must be secured and configured. Google Colab provides a robust, albeit ephemeral, Linux environment. The volatile nature of the filesystem necessitates strict protocols for API key management and persistent storage of generated assets.

### **2.1 Dependency Management**

The interaction with Sonauto is primarily HTTP-based. While official wrapper clients exist for some platforms, a direct implementation using the requests library offers the highest degree of transparency and control for a custom multi-agent system.

**Required Libraries:**

* requests: For handling HTTP methods (POST, GET).  
* json: For payload serialization and response parsing.  
* time: For implementing exponential backoff during polling.  
* os & pathlib: For filesystem manipulation.  
* google.colab.userdata: For secure secret management.

No specialized hardware acceleration (GPU) is required for the *client* side of the API call, as the inference happens on Sonauto's servers. However, if your multi-agent system uses local LLMs (like Llama 3 or Mistral) for lyric generation, the Colab instance should be GPU-provisioned.

### **2.2 Authentication Architecture**

Sonauto uses Bearer Token authentication. The API key is a static secret that grants access to the compute credits associated with your account.1

**Security Critical Warning:** Never hardcode API keys in notebook cells. This practice exposes credentials if the notebook is shared or committed to version control.

Implementation Strategy:  
Utilize the google.colab.userdata module (Secrets) introduced in recent Colab updates. This stores environment variables outside the notebook content.

Python

from google.colab import userdata  
import os

def get\_api\_credentials():  
    """  
    Securely retrieves the Sonauto API key from the environment.  
    Raises a runtime error if the key is missing to prevent authentication failures downstream.  
    """  
    try:  
        api\_key \= userdata.get('SONAUTO\_API\_KEY')  
        if not api\_key:  
            raise ValueError("API Key is empty.")  
        return api\_key  
    except Exception as e:  
        \# Fallback for local testing outside Colab  
        api\_key \= os.getenv('SONAUTO\_API\_KEY')  
        if not api\_key:  
            raise RuntimeError(  
                "CRITICAL: Sonauto API Key not found. "  
                "Set 'SONAUTO\_API\_KEY' in Colab Secrets or Environment Variables."  
            ) from e  
        return api\_key

### **2.3 Network and Rate Limiting**

API interactions are subject to network latency and rate limits. While Sonauto's specific rate limits are generally generous for paid tiers, robust code must anticipate 429 Too Many Requests errors.1

* **Concurrency:** The standard plan allows for concurrent requests, but generating too many simultaneous tracks can deplete credits rapidly (100 credits per song).1  
* **Retry Logic:** A comprehensive client wrapper must implement a retry strategy with exponential backoff for 5xx (Server Error) and 429 (Rate Limit) status codes.

## ---

**3\. The POST /generations Endpoint: Anatomy of a Request**

The nucleus of the Sonauto integration is the creation of the generation task. This is where the inputs from your multi-agent system are synthesized into a coherent directive for the AI.

Endpoint URL: https://api.sonauto.ai/v1/generations 1  
Method: POST  
Content-Type: application/json  
The following subsections dissect each parameter of the request body, analyzing its impact on rap music generation.

### **3.1 The prompt Parameter: The Narrative Engine**

The prompt field is a natural language string that describes the song. For rap, this is the place to define the "texture" and "attitude" of the track.

Agent Responsibility: The "Prompt Engineer" Agent.  
Optimization Strategy:  
Unlike image generation where abstract concepts work well, audio diffusion models thrive on specific musical terminology.

* **Instrumentation:** Mention specific elements common in rap production (e.g., "heavy 808 bass," "rolling hi-hats," "sampled jazz piano," "cinematic strings," "vinyl crackle").7  
* **Vocal Delivery:** Describe the flow. Terms like "aggressive flow," "mumble rap," "fast-paced delivery," or "melodic hook" help guide the vocal synthesis.  
* **Atmosphere:** Adjectives like "dark," "triumphant," "melancholic," or "hype" set the emotional baseline.

*Example High-Fidelity Prompt:*

"A high-energy drill track with sliding 808 bass, rapid-fire hi-hat triplets, and a menacing synth melody. The vocal delivery is aggressive and staccato, typical of UK Drill."

### **3.2 The tags Parameter: Genre Taxonomy**

The tags field is a list of strings that maps the request to specific clusters in the model's latent space. This is the primary lever for genre control.

Agent Responsibility: The "Composer" Agent.  
Constraint: The model works best with tags from its known vocabulary. Providing arbitrary tags may result in them being ignored or hallucinated.  
The Rap Tag Taxonomy 5:  
To ensure the output is authentically "Rap," your Composer Agent should select 3-5 tags from the following curated categories.

| Category | Recommended Tags | Acoustic Implication |
| :---- | :---- | :---- |
| **Core Genre** | rap, hip hop | Fundamental rhythmic structure. |
| **Sub-Genre** | trap, drill, boom bap, pop rap, cloud rap | Defines the drum pattern (e.g., Trap \= fast hi-hats; Boom Bap \= swing drums). |
| **Era** | 90s, 2000s, old school, modern | Affects mixing style (lo-fi vs. polished). |
| **Mood** | aggressive, chill, dark, energetic, emotional | Guides the harmonic progression. |
| **Instrumentation** | piano, guitar, synth, 808, sample | Specific timbral choices. |

**Technical Insight:** If tags are omitted, the API attempts to infer them from the prompt. However, for a programmatic system, explicit tagging provides deterministic control. Always provide tags.1

### **3.3 The lyrics Parameter: Structural Directives**

This is the most critical parameter for your application. The lyrics field accepts a string containing the text to be vocalized.

Agent Responsibility: The "Lyricist" Agent.  
Structural Syntax:  
Sonauto's model parses specific metatags enclosed in square brackets \`\` to determine song structure. These are not vocalized but act as state-switching triggers for the generator.3  
**Supported Structural Tags for Rap:**

* \[Intro\]: Usually instrumental or spoken word ad-libs ("Yeah," "Check it").  
* \[Verse\]: The main body. The model expects a consistent rhyme scheme here.  
* \[Chorus\]: The hook. The model tends to increase melodic complexity or layering here.  
* \`\`: A change in flow or beat intensity.  
* \[Outro\]: Fading out or final ad-libs.  
* \`\`: Useful for Trap/EDM crossovers to signal high energy.

**Formatting Rules for the Lyricist Agent:**

1. **Sectioning:** Every block of text must be preceded by a structural tag.  
2. **Length:** A standard generation is approx. 90-95 seconds. The lyrics provided must fit this window. A typical 16-bar verse and 8-bar chorus fits well.  
   * *Warning:* Providing 5 minutes of lyrics for a 90-second generation window will result in the model rushing the flow (unnatural speed) or truncating the text.  
3. **Ad-libs:** Parenthetical text (yeah\!) (let's go\!) is often interpreted as background vocals or ad-libs.10

Example Lyric Payload:  
\[Intro\]  
(Yeah)  
Mic check one two  
We live from the cloud  
\[Verse 1\]  
Digital signals moving through the wire  
My logic gates open spitting pure fire  
...  
\[Chorus\]  
This is the future sound  
Automated underground  
...

### **3.4 Control Parameters: prompt\_strength and balance\_strength**

These floating-point values allow the "Producer" Agent to fine-tune the mix and adherence constraints.

**balance\_strength (Audio Mixing):**

* **Range:** 0.0 to 1.0 (Default \~0.7).  
* **Function:** Controls the ratio of vocal presence to instrumental volume.  
* **Recommendation for Rap:** Rap requires high vocal intelligibility. If the beat is too loud, the lyrics become muddy.  
  * *Set to 0.7 \- 0.8:* Ideally balances a punchy beat with clear vocals.1  
  * *Set to \< 0.5:* Creates "mumble rap" or background music where vocals are buried.

**prompt\_strength (Adherence):**

* **Function:** Determines how strictly the model follows the text prompt vs. its own creative improvisation.  
* **Recommendation:** Keep near default. Setting this too high can force the model into "overfitting" the prompt, leading to audio artifacts or unnatural transitions.1

### **3.5 Operational Parameters: seed and instrumental**

* **instrumental:** Boolean. If true, lyrics are ignored. Useful if your agents want to generate "Type Beats" first and add vocals later (though Sonauto generates vocals and music simultaneously by default). For your use case, set to false.1  
* **seed:** Integer. Critical for reproducibility. If a specific generation is successful, reusing the seed with slight prompt tweaks allows for controlled iteration. Your system should log the seed of every generated track.1

## ---

**4\. Multi-Agent Data Contracts and JSON Schemas**

To facilitate the pre-processing step, we must define the interface between your agents and the API client. This ensures that the inputs generated by the agents are always valid for the API call.

### **4.1 The Agent Output Schema**

Your agents (running as Python functions or LLM chains) should aggregate their work into a single SongConcept dictionary.

Python

\# Conceptual Schema for Agent Output  
song\_concept\_schema \= {  
    "title": "string",          \# Internal reference title  
    "lyrics\_payload": "string", \# Formatted text with \[Verse\], \[Chorus\] tags  
    "style\_profile": {  
        "tags": \["list", "of", "strings"\],  
        "prompt\_narrative": "string",  
        "bpm\_hint": "string"    \# Optional: incorporated into prompt  
    },  
    "production\_settings": {  
        "balance": 0.7,  
        "instrumental": False,  
        "model\_version": "v1"  
    }  
}

### **4.2 Agent 1: The Lyricist (Text Generator)**

Task: Generate rhyme schemes based on a theme.  
Constraint: Must adhere to the \`\` format.  
Pre-processing Logic:

1. Receive theme (e.g., "Cyberpunk Heist").  
2. Generate 16 bars of Verse, 8 bars of Chorus.  
3. *Sanitization:* Remove conversational filler from the LLM output (e.g., "Here are the lyrics you asked for:"). The output must be *only* the lyrics and tags.

### **4.3 Agent 2: The Composer (Style Architect)**

Task: Define the sonic palette.  
Constraint: Must output valid tags from the Sonauto allowed list.  
Pre-processing Logic:

1. Receive mood (e.g., "Tense").  
2. Map "Tense" to Sonauto tags: \["dark", "cinematic", "drill", "minor key"\].  
3. Construct the prompt: "A cinematic drill beat with orchestral strings and heavy bass."

### **4.4 Agent 3: The Engineer (API Client Wrapper)**

Task: Validation and Transmission.  
Logic:

1. Validate that lyrics length is \< 3000 characters (API limit safety).  
2. Ensure tags is a list of strings, not a single string.  
3. Inject the API Key.  
4. Execute the HTTP request.

## ---

**5\. Technical Implementation: The Request Lifecycle**

This section provides the definitive Python code for the SonautoClient class. This class encapsulates authentication, payload construction, and request dispatching.

### **5.1 The SonautoClient Class Structure**

Python

import requests  
import time  
import json  
from typing import List, Optional, Dict, Union

class SonautoClient:  
    """  
    A robust client for interacting with the Sonauto V1 API.  
    Handles authentication, payload construction, and error management.  
    """  
      
    BASE\_URL \= "https://api.sonauto.ai/v1"  
      
    def \_\_init\_\_(self, api\_key: str):  
        """  
        Initialize the client with the API key.  
          
        Args:  
            api\_key (str): The Bearer token for authentication.  
        """  
        self.api\_key \= api\_key  
        self.headers \= {  
            "Authorization": f"Bearer {self.api\_key}",  
            "Content-Type": "application/json"  
        }

    def generate\_song(  
        self,   
        prompt: str,   
        lyrics: str,   
        tags: List\[str\],   
        instrumental: bool \= False,  
        balance\_strength: float \= 0.7  
    ) \-\> Dict:  
        """  
        Dispatches a generation request to the Sonauto API.  
          
        Args:  
            prompt (str): Description of the song style.  
            lyrics (str): The lyrics with structural tags \[Verse\], \[Chorus\].  
            tags (List\[str\]): List of style tags (e.g., \["rap", "trap"\]).  
            instrumental (bool): If True, ignores lyrics.  
            balance\_strength (float): Vocal/Instrumental balance (0.0 \- 1.0).  
              
        Returns:  
            Dict: The response object containing the 'task\_id'.  
              
        Raises:  
            requests.exceptions.HTTPError: If the API returns a 4xx/5xx error.  
        """  
        endpoint \= f"{self.BASE\_URL}/generations"  
          
        \# Payload Construction  
        \# Note: We ensure 'tags' is a list and 'lyrics' is a string.  
        payload \= {  
            "prompt": prompt,  
            "tags": tags,  
            "lyrics": lyrics,  
            "instrumental": instrumental,  
            "balance\_strength": balance\_strength,  
            \# 'num\_songs' defaults to 2 in many internal implementations to give variety  
            "num\_songs": 2   
        }  
          
        print(f"Sending Request to {endpoint}...")  
        try:  
            response \= requests.post(  
                endpoint,   
                headers=self.headers,   
                json=payload,  
                timeout=30  \# Network timeout  
            )  
            response.raise\_for\_status() \# Raise error for bad status codes  
            return response.json()  
              
        except requests.exceptions.HTTPError as e:  
            \# Enhanced Error Logging  
            print(f"HTTP Error: {e}")  
            if response.content:  
                print(f"Server Response: {response.text}")  
            raise

### **5.2 Handling the Response: Task IDs**

The API response to a POST request is *synchronous acknowledgment of an asynchronous task*. You will not receive the audio file immediately. Instead, you receive a **Task Object**.

**Sample Success Response (Status 200):**

JSON

{  
    "id": "task\_12345abcdef",  
    "status": "PENDING",  
    "created\_at": "2025-10-27T10:00:00Z",  
    "prompt": "A dark trap beat...",  
   ...  
}

The critical piece of information here is the id (often referred to as task\_id). Your system must store this ID to track the generation progress.1

## ---

**6\. Asynchronous Polling and State Management**

Music generation is computationally expensive, taking anywhere from 60 to 120 seconds. To retrieve the result, your Colab notebook must implement a **Polling Mechanism**. This involves periodically checking the status of the task until it reaches a terminal state (COMPLETED or FAILED).

### **6.1 The Status Endpoint**

URL: GET https://api.sonauto.ai/v1/generations/{task\_id} 1  
Method: GET  
Sending a GET request to this endpoint returns the updated Task Object. The status field will evolve from QUEUED \-\> PROCESSING \-\> COMPLETED (or FAILED).

### **6.2 Polling Strategy: Exponential Backoff**

Naive polling (checking every 1 second) is inefficient and may trigger rate limiters. Exponential backoff increases the wait time between checks, reducing load while ensuring timely retrieval.

**Recommended Backoff Schedule:**

1. Check 1: Wait 5 seconds.  
2. Check 2: Wait 10 seconds.  
3. Check 3+: Wait 15 seconds.

### **6.3 Implementation of the Watcher Service**

Python

    def poll\_for\_completion(self, task\_id: str, timeout: int \= 300) \-\> Dict:  
        """  
        Polls the status endpoint until the generation is complete or times out.  
          
        Args:  
            task\_id (str): The ID received from the generate\_song call.  
            timeout (int): Maximum seconds to wait before giving up.  
              
        Returns:  
            Dict: The final task object containing audio URLs.  
        """  
        url \= f"{self.BASE\_URL}/generations/{task\_id}"  
        start\_time \= time.time()  
        wait\_time \= 5  
          
        print(f"Polling task {task\_id} for completion...")  
          
        while (time.time() \- start\_time) \< timeout:  
            try:  
                response \= requests.get(url, headers=self.headers)  
                response.raise\_for\_status()  
                data \= response.json()  
                status \= data.get("status")  
                  
                if status \== "COMPLETED" or status \== "SUCCESS":  
                    print("\\nGeneration Completed\!")  
                    return data  
                      
                elif status \== "FAILED" or status \== "FAILURE":  
                    error\_msg \= data.get("error\_message", "Unknown Error")  
                    raise RuntimeError(f"Generation Failed: {error\_msg}")  
                      
                else:  
                    \# Still processing  
                    print(f"\\rStatus: {status}... Waiting {wait\_time}s", end="")  
                    time.sleep(wait\_time)  
                    \# Cap wait time at 15 seconds  
                    wait\_time \= min(wait\_time \+ 2, 15)  
                      
            except requests.exceptions.RequestException as e:  
                print(f"Network error during polling: {e}. Retrying...")  
                time.sleep(5)  
                  
        raise TimeoutError(f"Generation timed out after {timeout} seconds.")

## ---

**7\. Asset Retrieval and Persistence**

Once the task status is COMPLETED, the JSON response will contain links to the generated assets.

### **7.1 Response Schema Analysis**

The completed task object contains the song\_paths field.

| Field | Type | Description |
| :---- | :---- | :---- |
| id | String | The task identifier. |
| status | String | "COMPLETED" |
| song\_paths | Array | A list of URLs pointing to the generated OGG or WAV files. Usually contains 2 URLs if num\_songs=2. |
| lyrics | String | The final lyrics used (may differ slightly if the model hallucinated ad-libs). |
| duration | Float | Duration in seconds. |

**Important Note:** The URLs in song\_paths are typically signed URLs from a CDN (Content Delivery Network). They may have an expiration time. Your system should download these files immediately rather than storing the links.1

### **7.2 File I/O in Google Colab**

Colab uses an ephemeral filesystem. If the runtime disconnects, files are lost.  
Best Practice:

1. Download the audio files to /content/.  
2. (Optional) Mount Google Drive and copy the files there for permanent storage.

Python

    def download\_assets(self, task\_data: Dict, output\_dir: str \= "./generated\_tracks") \-\> List\[str\]:  
        """  
        Downloads the audio files from the URLs in the task object.  
        """  
        import os  
        if not os.path.exists(output\_dir):  
            os.makedirs(output\_dir)  
              
        downloaded\_paths \=  
        urls \= task\_data.get("song\_paths",)  
          
        for i, url in enumerate(urls):  
            try:  
                print(f"Downloading track {i+1}...")  
                r \= requests.get(url, stream=True)  
                r.raise\_for\_status()  
                  
                \# Construct filename: taskID\_index.ogg  
                filename \= f"{task\_data\['id'\]}\_{i}.ogg"  
                filepath \= os.path.join(output\_dir, filename)  
                  
                with open(filepath, 'wb') as f:  
                    for chunk in r.iter\_content(chunk\_size=8192):  
                        f.write(chunk)  
                          
                downloaded\_paths.append(filepath)  
                print(f"Saved to {filepath}")  
                  
            except Exception as e:  
                print(f"Failed to download asset {url}: {e}")  
                  
        return downloaded\_paths

## ---

**8\. Advanced Workflows: Extension and Inpainting**

A truly "highly optimized" implementation does not stop at initial generation. The Producer Agent may critique the output and decide to extend the track or fix a specific section. Sonauto provides endpoints for this iterative refinement.

### **8.1 The /generations/extend Endpoint**

This allows you to append audio to the beginning or end of an existing generation.  
Use Case: The 90-second generation cut off the final verse. The Producer Agent requests an extension.  
**Payload Parameters:**

* audio\_url: The URL of the *source* track (from the previous song\_paths).  
* side: "right" (append to end) or "left" (prepend to start).  
* extend\_duration: Seconds to add (e.g., 45.0).  
* prompt / tags: Usually kept identical to the original to maintain consistency.  
* lyrics: The *new* lyrics for the extension.1

### **8.2 The /generations/inpaint Endpoint**

This allows for regenerating a specific slice of the audio.  
Use Case: The rapper's flow stumbled at 0:45, or the lyrics were garbled.  
**Payload Parameters:**

* audio\_url: The source track.  
* sections: A list of lists defining start/end times \[\[45.0, 50.0\]\].  
* lyrics: The text that *should* occur in that window.  
* prompt: Contextual prompt.

**Optimization Note:** Inpainting is computationally intensive. Ensure your "Producer" Agent identifies the timestamps accurately.

## ---

**9\. Comprehensive Troubleshooting and Error Handling**

In a production environment, knowing how to handle failures is as important as handling success.

### **9.1 HTTP Status Codes**

| Code | Meaning | Cause | Action |
| :---- | :---- | :---- | :---- |
| **200** | OK | Request successful. | Parse JSON. |
| **400** | Bad Request | Invalid JSON or missing parameters. | Check payload schema. Ensure lyrics \+ tags/prompt rules are met. |
| **401** | Unauthorized | Invalid/Missing API Key. | Check google.colab.userdata. Regenerate key. |
| **402** | Payment Required | Out of credits. | Purchase more credits or wait for refresh. |
| **415** | Unsupported Media | Missing Content-Type: application/json header. | Verify headers. |
| **429** | Too Many Requests | Rate limit exceeded. | Implement exponential backoff. |
| **500** | Internal Error | Server-side failure. | Retry after a delay. |

### **9.2 Content Failures**

Sometimes the API returns 200, but the generation is "bad" (hallucinations, silence).

* **Detection:** While hard to detect programmatically without audio analysis, the "Producer" Agent could use an external Audio-to-Text model (like Whisper) to verify that the generated lyrics match the input lyrics. If the Word Error Rate (WER) is high, trigger a regeneration with a different seed.

## ---

**10\. Conclusion and Strategic Recommendations**

This report has documented the complete technical stack required to integrate Sonauto into a Colab-based multi-agent system. By strictly adhering to the JSON schemas for the /generations endpoint, leveraging structural lyric tags, and implementing robust asynchronous polling, your system is positioned to generate high-fidelity rap music autonomously.

**Key Takeaways for Optimization:**

1. **Tag Precision:** Use the specific Rap Taxonomy provided in Section 3.2.  
2. **Structural Integrity:** Enforce \[Verse\]/\[Chorus\] formatting in the Lyricist Agent.  
3. **Security:** Use colab.userdata for API keys.  
4. **Resilience:** Implement the retry and polling logic defined in Sections 5 and 6\.

**Next Steps:**

1. Initialize a Colab notebook.  
2. Input the SonautoClient class code.  
3. Store your API key in Colab Secrets.  
4. Run a test generation with the prompt: *"A heavy 808 trap beat with fast hi-hats"* and tags \["trap", "rap"\].

This infrastructure provides the "hands" for your AI agents, allowing them to translate creative cognition into audible reality.

#### **Works cited**

1. Developers (API) \- Sonauto, accessed December 11, 2025, [https://sonauto.ai/developers](https://sonauto.ai/developers)  
2. Show HN: Sonauto API – Generative music for developers \- Hacker News, accessed December 11, 2025, [https://news.ycombinator.com/item?id=43244166](https://news.ycombinator.com/item?id=43244166)  
3. Sonauto Now Available on fal, accessed December 11, 2025, [https://blog.fal.ai/sonauto-now-available-on-fal/](https://blog.fal.ai/sonauto-now-available-on-fal/)  
4. Song Structure Tags Make AI Music Sound Pro \- YouTube, accessed December 11, 2025, [https://www.youtube.com/watch?v=bxShdhQodU8](https://www.youtube.com/watch?v=bxShdhQodU8)  
5. Tag Explorer \- Sonauto, accessed December 11, 2025, [https://sonauto.ai/tag-explorer](https://sonauto.ai/tag-explorer)  
6. Sonauto V2 | Text to Audio \- Fal.ai, accessed December 11, 2025, [https://fal.ai/models/sonauto/v2/text-to-music/api](https://fal.ai/models/sonauto/v2/text-to-music/api)  
7. What prompt to use to achieve a Song that is Full Rap? : r/SunoAI \- Reddit, accessed December 11, 2025, [https://www.reddit.com/r/SunoAI/comments/1h4v02f/what\_prompt\_to\_use\_to\_achieve\_a\_song\_that\_is\_full/](https://www.reddit.com/r/SunoAI/comments/1h4v02f/what_prompt_to_use_to_achieve_a_song_that_is_full/)  
8. Suno Style Prompt Guide 2.0 : r/SunoAI \- Reddit, accessed December 11, 2025, [https://www.reddit.com/r/SunoAI/comments/1n8lq6u/suno\_style\_prompt\_guide\_20/](https://www.reddit.com/r/SunoAI/comments/1n8lq6u/suno_style_prompt_guide_20/)  
9. AI Rap and hip hop songs on Sonauto, accessed December 11, 2025, [https://sonauto.ai/tag/rap%20and%20hip%20hop](https://sonauto.ai/tag/rap%20and%20hip%20hop)  
10. Suno AI Advanced Generative AI Music Prompting Tips \- YouTube, accessed December 11, 2025, [https://www.youtube.com/watch?v=XINZ-PkLXzw](https://www.youtube.com/watch?v=XINZ-PkLXzw)  
11. Sonauto AI Review: Features, Pricing and Tutorial 2025 \- HitPaw Edimakor, accessed December 11, 2025, [https://edimakor.hitpaw.com/ai-video-tools/sonauto-ai-review.html](https://edimakor.hitpaw.com/ai-video-tools/sonauto-ai-review.html)  
12. Sonauto V2 | Audio to Audio \- Fal.ai, accessed December 11, 2025, [https://fal.ai/models/sonauto/v2/extend/api](https://fal.ai/models/sonauto/v2/extend/api)