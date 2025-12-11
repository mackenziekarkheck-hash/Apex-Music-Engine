"""
Unit tests for Pydantic models and fal_client integration.

Tests:
- SonautoGenerationRequest validation
- SonautoInpaintRequest section format
- SonautoExtendRequest parameters
- O(1) tag validation
- to_fal_payload() output format
- Cost estimation
"""

import unittest
import sys
import os
import warnings

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.fal_models import (
    SonautoGenerationRequest,
    SonautoInpaintRequest,
    SonautoExtendRequest,
    SonautoModel,
    OutputFormat,
    ExtendSide,
    GENRE_CFG_DEFAULTS,
    COST_PER_GENERATION_USD,
    validate_tags_o1,
    VALID_TAGS_SET
)


class TestTagValidation(unittest.TestCase):
    """Tests for O(1) tag validation."""
    
    def test_valid_tags_normalized(self):
        """Test that valid tags are normalized to lowercase."""
        tags = ["TRAP", "Hip Hop", "808"]
        normalized, invalid = validate_tags_o1(tags)
        
        self.assertEqual(normalized, ["trap", "hip hop", "808"])
        self.assertEqual(invalid, [])
    
    def test_invalid_tags_detected(self):
        """Test that invalid tags are flagged."""
        tags = ["trap", "invalid_tag_xyz", "808"]
        normalized, invalid = validate_tags_o1(tags)
        
        self.assertEqual(len(normalized), 3)
        self.assertIn("invalid_tag_xyz", invalid)
    
    def test_tag_set_is_frozenset(self):
        """Test that tag database is cached as frozenset for O(1) lookup."""
        self.assertIsInstance(VALID_TAGS_SET, frozenset)
    
    def test_empty_tags_handled(self):
        """Test empty tag list handling."""
        normalized, invalid = validate_tags_o1([])
        self.assertEqual(normalized, [])
        self.assertEqual(invalid, [])


class TestSonautoGenerationRequest(unittest.TestCase):
    """Tests for generation request validation."""
    
    def test_minimal_valid_request(self):
        """Test creating request with minimal required fields."""
        request = SonautoGenerationRequest(prompt="Test trap beat")
        
        self.assertEqual(request.prompt, "Test trap beat")
        self.assertEqual(request.prompt_strength, 2.0)
        self.assertEqual(request.balance_strength, 0.7)
        self.assertEqual(request.num_songs, 1)
        self.assertEqual(request.output_format, OutputFormat.WAV)
    
    def test_full_request_with_all_fields(self):
        """Test creating request with all fields populated."""
        request = SonautoGenerationRequest(
            prompt="Aggressive phonk with heavy 808s",
            tags=["phonk", "trap", "aggressive"],
            lyrics="[Verse]\nTest lyrics here",
            prompt_strength=3.0,
            balance_strength=0.6,
            bpm=140,
            seed=42,
            num_songs=2,
            instrumental=False
        )
        
        self.assertEqual(request.prompt_strength, 3.0)
        self.assertEqual(request.bpm, 140)
        self.assertEqual(request.seed, 42)
        self.assertEqual(request.num_songs, 2)
    
    def test_bpm_auto_string(self):
        """Test that 'auto' BPM is accepted."""
        request = SonautoGenerationRequest(prompt="Test", bpm="auto")
        self.assertEqual(request.bpm, "auto")
    
    def test_bpm_invalid_string_rejected(self):
        """Test that invalid BPM strings are rejected."""
        with self.assertRaises(ValueError):
            SonautoGenerationRequest(prompt="Test", bpm="fast")
    
    def test_bpm_out_of_range_rejected(self):
        """Test that BPM outside 40-240 is rejected."""
        with self.assertRaises(ValueError):
            SonautoGenerationRequest(prompt="Test", bpm=300)
        
        with self.assertRaises(ValueError):
            SonautoGenerationRequest(prompt="Test", bpm=20)
    
    def test_prompt_strength_bounds(self):
        """Test prompt_strength validation bounds."""
        with self.assertRaises(ValueError):
            SonautoGenerationRequest(prompt="Test", prompt_strength=6.0)
        
        with self.assertRaises(ValueError):
            SonautoGenerationRequest(prompt="Test", prompt_strength=-1.0)
    
    def test_num_songs_bounds(self):
        """Test num_songs validation (1 or 2 only)."""
        with self.assertRaises(ValueError):
            SonautoGenerationRequest(prompt="Test", num_songs=3)
    
    def test_to_fal_payload_format(self):
        """Test that to_fal_payload() produces correct structure."""
        request = SonautoGenerationRequest(
            prompt="Test prompt",
            tags=["trap", "808"],
            lyrics="Test lyrics",
            bpm=140,
            seed=123
        )
        
        payload = request.to_fal_payload()
        
        self.assertEqual(payload['prompt'], "Test prompt")
        self.assertEqual(payload['tags'], ["trap", "808"])
        self.assertEqual(payload['lyrics'], "Test lyrics")
        self.assertEqual(payload['bpm'], 140)
        self.assertEqual(payload['seed'], 123)
        self.assertEqual(payload['output_format'], "wav")
        self.assertIn('prompt_strength', payload)
        self.assertIn('balance_strength', payload)
    
    def test_to_fal_payload_omits_none_values(self):
        """Test that None values are not included in payload."""
        request = SonautoGenerationRequest(prompt="Test")
        payload = request.to_fal_payload()
        
        self.assertNotIn('lyrics', payload)
        self.assertNotIn('seed', payload)
        self.assertNotIn('bpm', payload)
    
    def test_cost_estimation_single_song(self):
        """Test cost estimation for single song."""
        request = SonautoGenerationRequest(prompt="Test", num_songs=1)
        self.assertEqual(request.estimate_cost(), COST_PER_GENERATION_USD)
    
    def test_cost_estimation_two_songs(self):
        """Test cost estimation for two songs (1.5x)."""
        request = SonautoGenerationRequest(prompt="Test", num_songs=2)
        self.assertEqual(request.estimate_cost(), COST_PER_GENERATION_USD * 1.5)


class TestSonautoInpaintRequest(unittest.TestCase):
    """Tests for inpainting request validation."""
    
    def test_valid_inpaint_request(self):
        """Test creating valid inpaint request."""
        request = SonautoInpaintRequest(
            audio_url="https://example.com/audio.wav",
            sections=[(10.0, 15.0)],
            lyrics="Inpainted lyrics"
        )
        
        self.assertEqual(request.audio_url, "https://example.com/audio.wav")
        self.assertEqual(len(request.sections), 1)
    
    def test_empty_sections_rejected(self):
        """Test that empty sections list is rejected."""
        with self.assertRaises(ValueError):
            SonautoInpaintRequest(
                audio_url="https://example.com/audio.wav",
                sections=[]
            )
    
    def test_negative_start_rejected(self):
        """Test that negative start time is rejected."""
        with self.assertRaises(ValueError):
            SonautoInpaintRequest(
                audio_url="https://example.com/audio.wav",
                sections=[(-1.0, 5.0)]
            )
    
    def test_end_before_start_rejected(self):
        """Test that end <= start is rejected."""
        with self.assertRaises(ValueError):
            SonautoInpaintRequest(
                audio_url="https://example.com/audio.wav",
                sections=[(10.0, 5.0)]
            )
    
    def test_to_fal_payload_section_format(self):
        """Test that sections are converted to {start, end} object format."""
        request = SonautoInpaintRequest(
            audio_url="https://example.com/audio.wav",
            sections=[(10.5, 15.0), (30.0, 35.5)],
            lyrics="Test"
        )
        
        payload = request.to_fal_payload()
        
        self.assertEqual(len(payload['sections']), 2)
        self.assertEqual(payload['sections'][0], {"start": 10.5, "end": 15.0})
        self.assertEqual(payload['sections'][1], {"start": 30.0, "end": 35.5})
    
    def test_lyrics_prompt_key(self):
        """Test that lyrics are sent as lyrics_prompt for fal_client."""
        request = SonautoInpaintRequest(
            audio_url="https://example.com/audio.wav",
            sections=[(0, 5)],
            lyrics="Test lyrics"
        )
        
        payload = request.to_fal_payload()
        self.assertEqual(payload['lyrics_prompt'], "Test lyrics")


class TestSonautoExtendRequest(unittest.TestCase):
    """Tests for extension request validation."""
    
    def test_valid_extend_request(self):
        """Test creating valid extension request."""
        request = SonautoExtendRequest(
            audio_url="https://example.com/audio.wav",
            side=ExtendSide.RIGHT
        )
        
        self.assertEqual(request.side, ExtendSide.RIGHT)
    
    def test_crop_duration_bounds(self):
        """Test crop_duration validation (0-10 seconds)."""
        with self.assertRaises(ValueError):
            SonautoExtendRequest(
                audio_url="https://example.com/audio.wav",
                crop_duration=15.0
            )
    
    def test_to_fal_payload_format(self):
        """Test extension payload format."""
        request = SonautoExtendRequest(
            audio_url="https://example.com/audio.wav",
            side=ExtendSide.LEFT,
            crop_duration=2.0,
            lyrics="Extended lyrics"
        )
        
        payload = request.to_fal_payload()
        
        self.assertEqual(payload['side'], "left")
        self.assertEqual(payload['crop_duration'], 2.0)
        self.assertEqual(payload['lyrics_prompt'], "Extended lyrics")


class TestGenreCFGDefaults(unittest.TestCase):
    """Tests for genre-based CFG scale defaults."""
    
    def test_both_key_formats_present(self):
        """Test that both 'boom_bap' and 'boom bap' keys work."""
        self.assertIn('boom_bap', GENRE_CFG_DEFAULTS)
        self.assertIn('boom bap', GENRE_CFG_DEFAULTS)
        self.assertEqual(GENRE_CFG_DEFAULTS['boom_bap'], GENRE_CFG_DEFAULTS['boom bap'])
    
    def test_phonk_high_cfg(self):
        """Test that phonk has high CFG (artifacts become aesthetic)."""
        self.assertGreaterEqual(GENRE_CFG_DEFAULTS['phonk'], 2.5)
    
    def test_melodic_low_cfg(self):
        """Test that melodic has low CFG (natural timbre)."""
        self.assertLessEqual(GENRE_CFG_DEFAULTS['melodic'], 2.0)


class TestSonautoModelEndpoints(unittest.TestCase):
    """Tests for model endpoint definitions."""
    
    def test_text_to_music_endpoint(self):
        """Test text-to-music endpoint format."""
        self.assertEqual(SonautoModel.TEXT_TO_MUSIC.value, "fal-ai/sonauto/v2/text-to-music")
    
    def test_inpaint_endpoint(self):
        """Test inpaint endpoint format."""
        self.assertEqual(SonautoModel.INPAINT.value, "fal-ai/sonauto/v2/inpaint")
    
    def test_extend_endpoint(self):
        """Test extend endpoint format."""
        self.assertEqual(SonautoModel.EXTEND.value, "fal-ai/sonauto/v2/extend")


if __name__ == '__main__':
    unittest.main()
