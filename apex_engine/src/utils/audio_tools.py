"""
APEX Engine Audio Tools - Audio Processing Utilities.

Provides wrappers for audio processing libraries:
- Librosa integration for DSP
- Loudness normalization (pyloudnorm)
- Format conversion
- Basic audio manipulation
"""

from typing import Optional, Tuple, List, Dict, Any
import os


class AudioProcessor:
    """
    Audio processing utility class.
    
    Wraps common audio operations with graceful degradation
    when audio libraries are not available.
    """
    
    def __init__(self):
        """Initialize the audio processor."""
        self.librosa_available = self._check_librosa()
        self.soundfile_available = self._check_soundfile()
    
    def _check_librosa(self) -> bool:
        """Check if librosa is available."""
        try:
            import librosa
            return True
        except ImportError:
            return False
    
    def _check_soundfile(self) -> bool:
        """Check if soundfile is available."""
        try:
            import soundfile
            return True
        except ImportError:
            return False
    
    def load_audio(
        self, 
        filepath: str, 
        sr: Optional[int] = None
    ) -> Tuple[Optional['np.ndarray'], int]:
        """
        Load audio file.
        
        Args:
            filepath: Path to audio file
            sr: Target sample rate (None for native)
            
        Returns:
            Tuple of (audio_array, sample_rate)
        """
        if not os.path.exists(filepath):
            return None, 0
            
        if self.librosa_available:
            import librosa
            y, sample_rate = librosa.load(filepath, sr=sr)
            return y, sample_rate
        else:
            return None, 0
    
    def save_audio(
        self, 
        audio: 'np.ndarray', 
        filepath: str, 
        sr: int
    ) -> bool:
        """
        Save audio to file.
        
        Args:
            audio: Audio array
            filepath: Output path
            sr: Sample rate
            
        Returns:
            True if successful
        """
        if self.soundfile_available:
            import soundfile as sf
            sf.write(filepath, audio, sr)
            return True
        return False
    
    def get_duration(self, filepath: str) -> float:
        """
        Get audio duration in seconds.
        
        Args:
            filepath: Path to audio file
            
        Returns:
            Duration in seconds
        """
        if self.librosa_available:
            import librosa
            return float(librosa.get_duration(path=filepath))
        return 0.0
    
    def get_tempo(self, filepath: str) -> Tuple[float, float]:
        """
        Detect tempo from audio file.
        
        Args:
            filepath: Path to audio file
            
        Returns:
            Tuple of (tempo, confidence)
        """
        if self.librosa_available:
            import librosa
            import numpy as np
            
            y, sr = librosa.load(filepath)
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            
            confidence = 0.8
            return float(tempo), confidence
        return 0.0, 0.0
    
    def extract_features(self, filepath: str) -> Dict[str, Any]:
        """
        Extract common audio features.
        
        Args:
            filepath: Path to audio file
            
        Returns:
            Dictionary of audio features
        """
        features = {
            'duration': 0.0,
            'tempo': 0.0,
            'rms_mean': 0.0,
            'spectral_centroid_mean': 0.0,
            'available': False
        }
        
        if not self.librosa_available:
            return features
            
        try:
            import librosa
            import numpy as np
            
            y, sr = librosa.load(filepath)
            
            features['duration'] = float(len(y) / sr)
            
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            features['tempo'] = float(tempo)
            
            rms = librosa.feature.rms(y=y)[0]
            features['rms_mean'] = float(np.mean(rms))
            
            centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            features['spectral_centroid_mean'] = float(np.mean(centroid))
            
            features['available'] = True
            
        except Exception as e:
            features['error'] = str(e)
        
        return features
    
    def normalize_loudness(
        self, 
        audio: 'np.ndarray', 
        sr: int, 
        target_lufs: float = -14.0
    ) -> 'np.ndarray':
        """
        Normalize audio to target loudness (LUFS).
        
        Args:
            audio: Input audio array
            sr: Sample rate
            target_lufs: Target loudness in LUFS
            
        Returns:
            Normalized audio array
        """
        try:
            import pyloudnorm as pyln
            import numpy as np
            
            meter = pyln.Meter(sr)
            loudness = meter.integrated_loudness(audio)
            
            normalized = pyln.normalize.loudness(audio, loudness, target_lufs)
            return normalized
            
        except ImportError:
            import numpy as np
            current_rms = np.sqrt(np.mean(audio**2))
            target_rms = 0.1
            
            if current_rms > 0:
                audio = audio * (target_rms / current_rms)
            
            return np.clip(audio, -1.0, 1.0)
    
    def convert_format(
        self, 
        input_path: str, 
        output_path: str,
        format: str = 'wav'
    ) -> bool:
        """
        Convert audio to a different format.
        
        Args:
            input_path: Input file path
            output_path: Output file path
            format: Target format
            
        Returns:
            True if successful
        """
        if not self.librosa_available or not self.soundfile_available:
            return False
            
        try:
            import librosa
            import soundfile as sf
            
            y, sr = librosa.load(input_path)
            sf.write(output_path, y, sr)
            return True
            
        except Exception:
            return False
