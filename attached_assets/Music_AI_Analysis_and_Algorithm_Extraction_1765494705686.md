# **Technical Architecture for Neuro-Acoustic Optimization: A Comprehensive Analysis of Algorithmic Music Generation and Evaluation**

## **1\. Introduction: The Paradigm Shift to Engineered Psychoacoustics**

The intersection of generative artificial intelligence and computational psychoacoustics marks a fundamental transition in music production. Historically, music creation has been an intuitive, artistic process, often resistant to quantification. However, the emergence of controllable diffusion models, such as those provided by the Sonauto API, allows for a new methodology: **Neuro-Acoustic Optimization**. This approach treats music generation not as a stochastic creative act, but as a solvable engineering problem where the objective function is the maximization of specific physiological and psychological responses in the listener.

This report details the technical architecture for a multi-agent Python system designed to orchestrate this optimization. By wrapping the generative core in layers of rigorous algorithmic analysis, we can iteratively refine audio and lyrical content to target metrics such as **Frisson** (aesthetic chills), **Dopaminergic Reward** (mediated by rhythmic prediction error), and **Lyrical Flow Complexity**. The system moves beyond the "black box" nature of standard AI generation, employing a "generate-analyze-optimize" feedback loop managed by stateful agents.

The analysis draws upon a wide array of technical documentation and academic research, extracting specific algorithms for phonetic analysis (the "Raplyzer" protocol), rhythmic syncopation (Longuet-Higgins models), and spectral feature extraction (Librosa-based frisson detection). It integrates these into a cohesive framework utilizing **LangGraph** for agent orchestration, ensuring a robust, human-in-the-loop workflow suitable for professional production environments.

## ---

**2\. The Generative Core: Deep Technical Analysis of the Sonauto API**

The foundation of the proposed architecture is the Sonauto API. Unlike consumer-facing interfaces which obfuscate the underlying mechanics, the API exposes critical parameters that allow for granular control over the latent diffusion process. A deep understanding of these endpoints is required to implement the "Director" agent effectively.

### **2.1 Latent Diffusion and Generation Mechanics**

The core generation mechanism operates via a diffusion transformer model. The process begins with a noise vector in a high-dimensional latent space, which is iteratively denoised conditioned on text prompts and lyrical inputs. The POST /generations endpoint is the primary interface for this process.

#### **2.1.1 Parameter Space and Optimization Vectors**

To engineer specific outcomes, the "Director" agent must manipulate the following parameters extracted from the documentation :

* **Prompt Strength (prompt\_strength):** This scalar value (range typically implied 0.0 to 1.0 or higher) governs the guidance scale of the diffusion model. It dictates how strictly the model adheres to the stylistic tags versus the inherent probability distribution of the training data.  
  * *Strategic Application:* High values enforce strict genre adherence (e.g., "Industrial Techno") but may introduce artifacts or reduce acoustic naturalness ("baking" the sound). Low values increase "creativity" and naturalness but risk genre drift. The agent must dynamically adjust this based on a "Novelty Score." If previous iterations are too generic, prompt\_strength is lowered to traverse new regions of the latent space.  
* **Balance Strength (balance\_strength):** This parameter controls the mixing equilibrium between the vocal track and the instrumental backing. The documentation suggests a default of 0.7.  
  * *Strategic Application:* This is a critical variable for **Lyrical Intelligibility**. In genres with high "Rhyme Density" (see Section 3), such as technical rap, the vocal articulation must be pristine. The "Mixing Agent" increases this value (e.g., to 0.75-0.80) when the "Lyric Analyst" detects a high syllable-per-second count, ensuring the intricate flow is not buried in the mix. Conversely, for atmospheric genres where vocals are textural, this value is lowered.  
* **Seed Control (seed):** The API allows for deterministic generation by fixing the random seed.  
  * *Strategic Application:* This is essential for controlled ablation studies. The system can lock the seed and varying *only* the lyrics or *only* the prompt\_strength, allowing the agents to isolate the causal impact of specific variables on the output metrics.

### **2.2 The Inpainting Protocol: Surgical Latent Editing**

Perhaps the most powerful feature for an optimization workflow is **Inpainting**. This allows the system to regenerate specific temporal regions of a track while preserving the surrounding context.

* **The Mechanism:** The agent defines a mask (start time, end time) and a new prompt/lyric set. The model retains the latent representation of the unmasked areas and re-diffuses the masked section.  
* **Critical Implementation Detail:** To prevent generation loss (digital degradation), the documentation specifies that the audio\_url passed to the inpainting endpoint must be the **internal CDN path** provided by Sonauto, not a re-uploaded binary file. This ensures the model references the original latent tensors rather than re-encoding a lossy audio file.  
* **Use Case:** If the "Frisson Detector" (Section 4\) identifies a "drop" at 1:15 that lacks dynamic impact, the agent does not discard the song. It schedules an inpainting task for mask\_start=75 (seconds), mask\_end=90, with an intensified prompt (e.g., "add sub-bass, explosive drums"), effectively "patching" the emotional hole in the composition.

### **2.3 Transition Algorithms and Song Extension**

The API supports generating transitions between existing tracks, facilitating the creation of continuous mixes or extended compositions.

* **Trimming Logic:** The endpoint accepts trim\_from\_end (Song A) and trim\_to\_start (Song B).  
  * *Algorithmic Alignment:* The "DJ Agent" utilizes librosa.beat.beat\_track to identify the beat grid of both source files. It calculates the trim values such that the transition point aligns with a downbeat (the first beat of a bar). This prevents "rhythmic trainwrecks" where the phase of the two tracks is misaligned.  
* **Silence Injection:** The silence parameter inserts a gap, which the model attempts to bridge.  
  * *Strategic Application:* For "Frisson" induction, a brief silence before a transition can act as a tension-builder (the "pre-drop gap"). The agent optimizes this duration based on the BPM (e.g., exactly 1 bar of silence) to maximize the impact of the incoming track.

## ---

**3\. Computational Linguistics: Algorithms for Lyrical Engineering**

In the domain of hip-hop and lyrical music, the "quality" of the text is not subjective; it is measurable through phonetics. The system employs a suite of algorithms extracted from the "Raplyzer" methodology and "DopeLearning" research to quantify and optimize the flow.

### **3.1 The Raplyzer Protocol: Phonetic Rhyme Density Analysis**

The standard metric for lyrical technicality is **Rhyme Density** (or Rhyme Factor). This moves beyond simple end-rhymes (AABB) to detect complex **Assonance Chains** and **Multisyllabic Rhymes** (Multis).

#### **3.1.1 The Phonetic Transduction Algorithm**

English orthography obscures phonetic reality (e.g., "rough" vs. "though"). The first step is **Grapheme-to-Phoneme (G2P)** conversion.

* **Library:** The system utilizes the pronouncing library (based on the CMU Pronouncing Dictionary) and g2p\_en (a neural G2P model) for out-of-vocabulary slang terms common in rap.  
* **Process:**  
  1. **Normalization:** The text is scrubbed of punctuation and lowercased.  
  2. **Deduplication:** Repeated lines (e.g., choruses) are removed or flagged. As noted in , analyzing repeated choruses artificially inflates the rhyme density score without reflecting actual lyrical skill.  
  3. **Vowel Isolation:** The "Raplyzer" algorithm posits that rap flow is primarily driven by vowels. Consonants are stripped from the phonetic string.  
     * *Input:* "My vision is clear"  
     * *Phonemes:* M AY1 V IH1 ZH AH0 N IH1 Z K L IH1 R  
     * *Vowel Stream:* AY IH AH IH IH

#### **3.1.2 Longest Common Subsequence (LCS) Matching**

The core scoring algorithm iterates through the vowel stream to find matching patterns.

* **The Lookback Window:** For each word $w\_i$, the algorithm scans the preceding $k$ words (typically $k=15$ to $20$ ) to find the best rhyme match.  
* **Matching Criteria:**  
  * The algorithm identifies the **Longest Common Suffix** of vowels between the current word and any word in the window.  
  * *Constraint:* A valid rhyme must consist of at least **two** vowels (a "Multi"). Single vowel matches are often discarded as trivial or noise.  
  * *Slat Rhymes:* Advanced implementation allows for "imperfect" matches (e.g., identifying AA and AH as similar). This requires a phonetic similarity matrix.  
* Scoring (Rhyme Factor):

  $$RF \= \\frac{\\sum\_{i=1}^{N} \\text{Length}(LCS\_i)}{N}$$

  Where $N$ is the total word count. An $RF \> 1.0$ indicates that, on average, every word is part of a multisyllabic rhyme chain, a hallmark of elite lyricism (e.g., MF DOOM, Eminem).

### **3.2 Flow Dynamics: Syllabic Stress and Meter**

"Flow" is the interaction of lyrics with time. The system extracts algorithms to measure rhythmic consistency.

#### **3.2.1 Syllable Counting and Stress Detection**

* **Tools:** syllables library for counting, pronouncing for stress patterns (0=unstressed, 1=primary, 2=secondary).  
* **Algorithm:**  
  * The "Flow Agent" constructs a **Stress Map** for each line: 0-1-0-1-0-1.  
  * **Meter Identification:** It compares this map against standard metrical feet (Iambic, Trochaic, Dactylic).  
  * **Variance Analysis:** It calculates the standard deviation of syllable counts across a verse.  
    * *Low Variance:* "Choppy," consistent flow (e.g., Dr. Seuss style).  
    * *Controlled Variance:* Complex, syncopated flow.  
    * *High Variance:* Free verse or poor writing.  
* **Optimization Loop:** If the variance is erratic without a pattern, the agent rewrites the line using an LLM (GPT-4o) to match the syllable count of the preceding line, smoothing the flow.

### **3.3 Semantic Coherence and "DopeLearning"**

Extracted from the "DopeLearning" research , the system implements a **Next-Line Prediction** model to ensure lyrical creativity does not descend into nonsense.

* **Technique:** **RankSVM**. The agent ranks candidate lines (generated by the LLM) based on a feature vector:  
  1. **Rhyme Density Score** (calculated above).  
  2. **Structural Similarity:** Line length match.  
  3. **Semantic Similarity:** Calculated using Latent Semantic Analysis (LSA) or Bag-of-Words (BoW) overlap with the previous $k=5$ lines.  
* **Goal:** To maximize the *combined* score of Rhyme and Meaning, ensuring the lyrics are "dope" (technically complex) but also coherent.

## ---

**4\. Psychoacoustics and Physiological Scoring: The "Evaluator" Agents**

The ultimate goal is **Neuro-Acoustic Optimization**—engineering sound to trigger specific biological pathways. We focus on two primary phenomena: **Frisson** (the "chills" response) and **Dopaminergic Engagement** (driven by rhythm).

### **4.1 The Frisson Index: Engineering Aesthetic Chills**

Frisson is a psychophysiological response characterized by shivers, piloerection (goosebumps), and pupil dilation. Research indicates it is triggered by specific acoustic features: sudden loudness changes, spectral expansion, and the violation of musical expectation.

#### **4.1.1 Audio Feature Extraction (Librosa Implementation)**

To quantify the "Frisson Potential" of a generated track, the system extracts the following features using the librosa Python library:

1. **Dynamic Surge ($\\Delta$RMS):**  
   * *Theory:* Sudden increases in loudness (e.g., the entry of the full band) trigger a brainstem reflex that contributes to frisson.  
   * *Algorithm:*  
     * Calculate RMS Energy: y\_rms \= librosa.feature.rms(y=y).  
     * Calculate the first derivative (Delta): delta\_rms \= numpy.diff(y\_rms).  
     * *Metric:* The maximum value of delta\_rms represents the "hardest hit" in the track.  
2. **Spectral Brightness (Centroid Expansion):**  
   * *Theory:* A rapid increase in high-frequency content (timbral brightness) is associated with high emotional arousal.  
   * *Algorithm:*  
     * Calculate Spectral Centroid: cent \= librosa.feature.spectral\_centroid(y=y, sr=sr).  
     * *Metric:* Detect slopes where the centroid rises significantly over a short window (e.g., a "riser" sound effect).  
3. **Spectral Contrast:**  
   * *Theory:* Measures the energy difference between peaks and valleys in the spectrum. High contrast correlates with "clear" and "powerful" sounds, distinct from muddy noise.

#### **4.1.2 The "Surprise" Model (Expectation Violation)**

Based on the IDyOM (Information Dynamics of Music) framework , frisson is strongly linked to **Prediction Error**.

* **Proxy Algorithm:**  
  * **Beat Expectation:** Use librosa.onset.onset\_strength to build an onset envelope.  
  * **Autocorrelation:** Perform autocorrelation on the envelope to determine the "strength" of the pulse (how predictable the rhythm is).  
  * **Violation Detection:** Identify moments where a high-magnitude onset occurs *off* the predicted grid (syncopation) or where a strong beat is *omitted* (syncopation by subtraction).  
  * *The "Drop" Mechanic:* A period of low rhythmic stability (buildup) followed by a moment of hyper-stability (the drop) maximizes the reward prediction error.

### **4.2 The Syncopation Index: Optimizing for Dopamine**

Music groove is fundamentally about the balance between predictability and complexity. The **Syncopation Index**, derived from the Longuet-Higgins and Lee models, quantifies this.

#### **4.2.1 The Weighting Algorithm**

1. **Quantization:** The audio beat is subdivided into a 16th-note grid.  
2. **Metric Weight Assignment:** Each position in the bar is assigned a weight ($W$) representing its structural importance:  
   * **Downbeat (Beat 1):** $W=0$ (Maximum expectation).  
   * **Quarter Notes:** $W=-1$.  
   * **Eighth Notes:** $W=-2$.  
   * **Sixteenth Notes:** $W=-3$ (Weakest expectation).  
3. **Syncopation Detection:**  
   * A syncopation event occurs when a note onset exists at a "weak" position (e.g., $W=-2$) and the *subsequent* "stronger" position (e.g., $W=-1$) is **silent**.  
   * The brain "hallucinates" the missing strong beat, creating cognitive tension.  
4. **Scoring:**  
   * $S\_{index} \= \\sum (W\_{strong} \- W\_{weak})$ for all syncopated pairs.  
   * **Optimization Target:** The "Rhythm Agent" aims for a "Goldilocks Zone" (e.g., Index 15-30).  
     * *Index \< 5:* Monotonous (No dopamine).  
     * *Index \> 50:* Chaotic/Math Rock (Too much cognitive load).

## ---

**5\. Agentic Architecture: The Multi-Agent Orchestration**

To implement these algorithms programmatically, we require a stateful, graph-based architecture. **LangGraph** is the optimal framework, as it supports cyclic workflows and human-in-the-loop intervention.

### **5.1 System Persona and Roles**

The system is composed of specialized agents, each interacting with the shared state.

* **The Lyricist (Creator):** Uses LLMs (OpenAI) to generate text. It receives feedback from the Analyst (e.g., "Rhyme density is 0.4; increase multis on vowel 'AY'").  
* **The Analyst (Quality Control):** Runs the **Raplyzer** and **Flow** algorithms. It acts as a gatekeeper for the text before it reaches the audio engine.  
* **The Producer (Renderer):** Interfaces with the **Sonauto API**. It manages credit usage, retries, and inpainting requests.  
* **The Critic (Psychoacoustic Evaluator):** Downloads the generated audio and runs the **Librosa** feature extraction (Frisson/Syncopation). It decides whether to "Approve" the track or send it back for "Inpainting" or "Remixing."

### **5.2 The LangGraph Workflow (State Diagram)**

The workflow is defined as a directed cyclic graph.

1. **Node 1: Draft Lyrics:** Initial prompt generation.  
2. **Node 2: Analyze Text:** Raplyzer check.  
   * *Conditional Edge:* If score \< threshold $\\rightarrow$ Loop back to Node 1 (Rewrite).  
   * *Else* $\\rightarrow$ Proceed to Node 3\.  
3. **Node 3: Generate Audio:** Sonauto API call.  
4. **Node 4: Analyze Audio:** Frisson and Syncopation check.  
   * *Conditional Edge:* If FrissonScore \< threshold $\\rightarrow$ Proceed to Node 5 (Inpaint).  
   * *Else* $\\rightarrow$ Proceed to Node 6 (Finalize).  
5. **Node 5: Inpaint Strategy:** Identify weak sections (low dynamic range), create mask, call API. $\\rightarrow$ Loop back to Node 4\.  
6. **Node 6: Human Review (Interrupt):** Pause execution. Present metrics to human.  
   * *Input:* Approve/Reject.

### **5.3 Human-in-the-Loop Integration**

As detailed in , LangGraph's interrupt mechanism is vital. While the agents can optimize metrics, "artistic soul" is currently unquantifiable. The system pauses before the final file export, displaying a dashboard of the metrics (Rhyme Factor: 1.2, Frisson Index: High). The human user acts as the final executive producer, preventing the "Paperclip Maximizer" problem where the AI creates something mathematically perfect but sonically unpleasing.

## ---

**6\. Python Implementation Guide and Library Stack**

This section provides the implementation details for the conceptual framework.

### **6.1 Dependency Stack**

The following libraries are essential for the "Analyzer" nodes:

* **librosa:** The industry standard for audio signal processing (Spectral Centroid, RMS, Beat Tracking).  
* **numpy / scipy:** For numerical operations and signal filtering.  
* **pydub:** For simple file manipulation (slicing, format conversion) pre-upload.  
* **pronouncing:** CMU Dictionary interface for rhyme analysis.  
* **syllables:** For flow metering.  
* **langgraph / langchain:** For the agent runtime environment.  
* **requests:** For API I/O.  
* **rubberband:** (Optional) For high-quality time-stretching if manual alignment is needed.

### **6.2 Code Implementation: The "Raplyzer" Node**

### **6.3 Code Implementation: The Frisson Detector**

## ---

**7\. Conclusion**

This report defines a comprehensive, technically exhaustive architecture for the next generation of AI music systems. By shifting the focus from simple generation to **Neuro-Acoustic Optimization**, we unlock the ability to engineer music that is not only structurally sound but physiologically impactful. The extraction of specific algorithms—from the phonetic density calculations of the **Raplyzer** to the spectral arousal detection of the **Frisson Index**—provides the necessary toolkit for this transformation.

The implementation of this system via **LangGraph** ensures that the optimization process is robust, stateful, and controllable. It represents a move away from "black box" creativity toward a future where AI acts as a precision instrument for emotional engineering, capable of iteratively refining a composition until it hits the exact dopaminergic and aesthetic targets defined by the human operator.

### **Table 1: Summary of Extracted Algorithms and Agents**

#### **Works cited**

1. Developers (API) \- Sonauto, accessed December 11, 2025, [https://sonauto.ai/developers](https://sonauto.ai/developers)  
2. Sonauto AI Review (2025): Free AI Music Generation, Stems, and Inpainting Tested, accessed December 11, 2025, [https://skywork.ai/blog/sonauto-ai-review-2025/](https://skywork.ai/blog/sonauto-ai-review-2025/)  
3. Examples using Sonauto's generative music API \- GitHub, accessed December 11, 2025, [https://github.com/Sonauto/sonauto-api-examples](https://github.com/Sonauto/sonauto-api-examples)  
4. Algorithm That Counts Rap Rhymes and Scouts Mad Lines | Mining ..., accessed December 11, 2025, [https://mining4meaning.com/2015/02/13/raplyzer/](https://mining4meaning.com/2015/02/13/raplyzer/)  
5. Poetry & Data II: Identifying meter in poetry using Python \- Florian Maas, accessed December 11, 2025, [https://www.fpgmaas.com/blog/poetry-and-data-2-addendum](https://www.fpgmaas.com/blog/poetry-and-data-2-addendum)  
6. DopeLearning: A Computational Approach to Rap Lyrics Generation \- Arya McCarthy, accessed December 11, 2025, [https://aryamccarthy.github.io/malmi2016dopelearning/](https://aryamccarthy.github.io/malmi2016dopelearning/)  
7. DopeLearning: A Computational Approach to Rap Lyrics Generation∗ \- SIGKDD, accessed December 11, 2025, [https://www.kdd.org/kdd2016/papers/files/adf0399-malmiA.pdf](https://www.kdd.org/kdd2016/papers/files/adf0399-malmiA.pdf)  
8. DopeLearning: A Computational Approach to Rap Lyrics Generation \- ResearchGate, accessed December 11, 2025, [https://www.researchgate.net/publication/305997530\_DopeLearning\_A\_Computational\_Approach\_to\_Rap\_Lyrics\_Generation](https://www.researchgate.net/publication/305997530_DopeLearning_A_Computational_Approach_to_Rap_Lyrics_Generation)  
9. Frisson \- Wikipedia, accessed December 11, 2025, [https://en.wikipedia.org/wiki/Frisson](https://en.wikipedia.org/wiki/Frisson)  
10. Thrills, chills, frissons, and skin orgasms: toward an integrative model of transcendent psychophysiological experiences in music \- Frontiers, accessed December 11, 2025, [https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2014.00790/full](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2014.00790/full)  
11. Melodic expectation as an elicitor of music-evoked chills \- bioRxiv, accessed December 11, 2025, [https://www.biorxiv.org/content/10.1101/2024.10.02.616280v2.full.pdf](https://www.biorxiv.org/content/10.1101/2024.10.02.616280v2.full.pdf)  
12. A multi-sensory code for emotional arousal \- PMC \- PubMed Central \- NIH, accessed December 11, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC6650719/](https://pmc.ncbi.nlm.nih.gov/articles/PMC6650719/)  
13. SoundSignature: What Type of Music Do You Like? \- arXiv, accessed December 11, 2025, [https://arxiv.org/pdf/2410.03375?](https://arxiv.org/pdf/2410.03375)  
14. The Construction and Evaluation of Statistical Models of Melodic Structure in Music Perception and Composition | Request PDF \- ResearchGate, accessed December 11, 2025, [https://www.researchgate.net/publication/266316834\_The\_Construction\_and\_Evaluation\_of\_Statistical\_Models\_of\_Melodic\_Structure\_in\_Music\_Perception\_and\_Composition](https://www.researchgate.net/publication/266316834_The_Construction_and_Evaluation_of_Statistical_Models_of_Melodic_Structure_in_Music_Perception_and_Composition)  
15. Hesitation, Anticipation and Syncopation. | Download Scientific Diagram \- ResearchGate, accessed December 11, 2025, [https://www.researchgate.net/figure/Hesitation-Anticipation-and-Syncopation\_fig2\_228850033](https://www.researchgate.net/figure/Hesitation-Anticipation-and-Syncopation_fig2_228850033)  
16. Master's Thesis \- Utrecht University Student Theses Repository Home, accessed December 11, 2025, [https://studenttheses.uu.nl/bitstream/handle/20.500.12932/43448/MasterThesis\_5970709\_LuukSchlette.pdf?sequence=1\&isAllowed=y](https://studenttheses.uu.nl/bitstream/handle/20.500.12932/43448/MasterThesis_5970709_LuukSchlette.pdf?sequence=1&isAllowed=y)  
17. LangGraph \- LangChain, accessed December 11, 2025, [https://www.langchain.com/langgraph](https://www.langchain.com/langgraph)  
18. Interrupts and Commands in LangGraph: Building Human-in-the-Loop Workflows, accessed December 11, 2025, [https://dev.to/jamesbmour/interrupts-and-commands-in-langgraph-building-human-in-the-loop-workflows-4ngl](https://dev.to/jamesbmour/interrupts-and-commands-in-langgraph-building-human-in-the-loop-workflows-4ngl)  
19. bmcfee/pyrubberband: python wrapper for rubberband \- GitHub, accessed December 11, 2025, [https://github.com/bmcfee/pyrubberband](https://github.com/bmcfee/pyrubberband)