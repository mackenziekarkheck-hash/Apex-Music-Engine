"""
Synthetic Audio Test Harness

Generates synthetic audio files for testing audio agents without
requiring real audio generation. Creates test fixtures with:
- Sine waves at specific BPMs
- Periodic impulses for beat detection testing
- Controlled syncopation patterns
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import numpy as np
    import soundfile as sf
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False


TEST_FIXTURES_DIR = os.path.join(
    os.path.dirname(__file__), 
    'fixtures', 
    'audio'
)


def generate_click_track(bpm: int, duration_sec: float = 10.0, sr: int = 22050) -> 'np.ndarray':
    """
    Generate a click track at the specified BPM.
    
    Creates a simple sine wave impulse at each beat position,
    useful for testing beat detection algorithms.
    """
    if not AUDIO_AVAILABLE:
        return None
    
    samples = int(duration_sec * sr)
    audio = np.zeros(samples)
    
    samples_per_beat = int((60.0 / bpm) * sr)
    
    click_duration = int(0.01 * sr)
    t = np.linspace(0, 0.01, click_duration)
    click = np.sin(2 * np.pi * 1000 * t) * np.exp(-50 * t)
    
    beat = 0
    while beat * samples_per_beat + click_duration < samples:
        start = beat * samples_per_beat
        audio[start:start + click_duration] += click
        beat += 1
    
    audio = audio / np.max(np.abs(audio))
    
    return audio


def generate_syncopated_track(bpm: int, syncopation_level: float = 0.3, 
                              duration_sec: float = 10.0, sr: int = 22050) -> 'np.ndarray':
    """
    Generate a track with controlled syncopation.
    
    Args:
        bpm: Tempo in beats per minute
        syncopation_level: 0.0 = on-beat, 1.0 = maximum syncopation
        duration_sec: Duration in seconds
        sr: Sample rate
        
    Returns:
        Audio array with syncopated rhythm
    """
    if not AUDIO_AVAILABLE:
        return None
    
    samples = int(duration_sec * sr)
    audio = np.zeros(samples)
    
    samples_per_beat = int((60.0 / bpm) * sr)
    samples_per_16th = samples_per_beat // 4
    
    click_duration = int(0.015 * sr)
    t = np.linspace(0, 0.015, click_duration)
    click = np.sin(2 * np.pi * 800 * t) * np.exp(-40 * t)
    off_click = np.sin(2 * np.pi * 1200 * t) * np.exp(-40 * t)
    
    beat = 0
    position = 0
    while position + click_duration < samples:
        is_downbeat = (beat % 4) == 0
        
        if np.random.random() < syncopation_level and not is_downbeat:
            offset = samples_per_16th * np.random.choice([1, 2, 3])
            pos = position + offset
            if pos + click_duration < samples:
                audio[pos:pos + click_duration] += off_click * 0.8
        else:
            audio[position:position + click_duration] += click
        
        position += samples_per_beat
        beat += 1
    
    audio = audio / np.max(np.abs(audio)) if np.max(np.abs(audio)) > 0 else audio
    
    return audio


def generate_test_fixtures():
    """Generate all test fixture audio files."""
    if not AUDIO_AVAILABLE:
        print("Audio libraries not available. Skipping fixture generation.")
        return
    
    os.makedirs(TEST_FIXTURES_DIR, exist_ok=True)
    
    bpm_targets = [90, 100, 140]
    for bpm in bpm_targets:
        audio = generate_click_track(bpm, duration_sec=10.0)
        filepath = os.path.join(TEST_FIXTURES_DIR, f'click_track_{bpm}bpm.wav')
        sf.write(filepath, audio, 22050)
        print(f"Generated: {filepath}")
    
    syncopation_levels = [(0.0, 'straight'), (0.3, 'moderate'), (0.6, 'heavy')]
    for level, name in syncopation_levels:
        audio = generate_syncopated_track(140, syncopation_level=level)
        filepath = os.path.join(TEST_FIXTURES_DIR, f'syncopated_{name}_140bpm.wav')
        sf.write(filepath, audio, 22050)
        print(f"Generated: {filepath}")
    
    print(f"\nTest fixtures generated in: {TEST_FIXTURES_DIR}")


def get_test_audio_path(fixture_name: str) -> str:
    """Get the path to a test audio fixture."""
    return os.path.join(TEST_FIXTURES_DIR, fixture_name)


class SyntheticAudioGenerator:
    """Helper class for generating test audio on-the-fly."""
    
    def __init__(self, sr: int = 22050):
        self.sr = sr
    
    def generate_tone(self, freq: float, duration: float) -> 'np.ndarray':
        """Generate a simple sine tone."""
        if not AUDIO_AVAILABLE:
            return None
        t = np.linspace(0, duration, int(duration * self.sr))
        return np.sin(2 * np.pi * freq * t)
    
    def generate_beat_pattern(self, bpm: int, pattern: list, duration: float) -> 'np.ndarray':
        """
        Generate audio with a specific beat pattern.
        
        Args:
            bpm: Tempo
            pattern: List of 0s and 1s for 16th notes (e.g., [1,0,0,0,1,0,1,0])
            duration: Total duration in seconds
        """
        if not AUDIO_AVAILABLE:
            return None
        
        samples = int(duration * self.sr)
        audio = np.zeros(samples)
        
        samples_per_16th = int((60.0 / bpm / 4) * self.sr)
        
        click_len = int(0.01 * self.sr)
        t = np.linspace(0, 0.01, click_len)
        click = np.sin(2 * np.pi * 1000 * t) * np.exp(-60 * t)
        
        pos = 0
        pattern_idx = 0
        while pos + click_len < samples:
            if pattern[pattern_idx % len(pattern)] == 1:
                audio[pos:pos + click_len] += click
            pos += samples_per_16th
            pattern_idx += 1
        
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio))
        
        return audio


if __name__ == '__main__':
    generate_test_fixtures()
