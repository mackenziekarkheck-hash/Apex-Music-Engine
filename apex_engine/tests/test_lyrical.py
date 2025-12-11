"""
Unit tests for lyrical analysis agents.

Tests:
- Raplyzer rhyme density calculation
- Syllable counting accuracy
- Flow consistency analysis
- PDI calculation
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.lyrical.agent_bars import BarsAnalyzer
from src.agents.lyrical.agent_flow import FlowAnalyzer


class TestRaplyzerRhymeDensity(unittest.TestCase):
    """Tests for the Raplyzer rhyme density algorithm."""
    
    def setUp(self):
        self.analyzer = BarsAnalyzer()
    
    def test_perfect_rhymes_detection(self):
        """Test detection of perfect end rhymes."""
        lyrics = """I'm making cash, stacking bread
Living fast till I'm dead
Counting money in my head
Every word that I said"""
        
        state = {'lyrics_draft': lyrics, 'structured_plan': {'bpm': 100}}
        result = self.analyzer.execute(state)
        
        self.assertTrue(result.success)
        metrics = result.state_updates.get('lyrical_metrics', {})
        
        self.assertIn('rhyme_factor', metrics)
        self.assertGreater(metrics['rhyme_factor'], 0.3)
    
    def test_internal_rhymes_detection(self):
        """Test detection of internal rhymes within lines."""
        lyrics = """I'm racing, pacing, never wasting time
Chasing, placing bets upon the grind"""
        
        state = {'lyrics_draft': lyrics, 'structured_plan': {'bpm': 100}}
        result = self.analyzer.execute(state)
        
        self.assertTrue(result.success)
    
    def test_multisyllabic_rhymes(self):
        """Test detection of multi-syllabic rhyme chains."""
        lyrics = """Astronomical, phenomenal, I'm unstoppable
Economical with syllables, clinical, biblical"""
        
        state = {'lyrics_draft': lyrics, 'structured_plan': {'bpm': 100}}
        result = self.analyzer.execute(state)
        
        self.assertTrue(result.success)
        metrics = result.state_updates.get('lyrical_metrics', {})
        
        self.assertIn('multisyllabic_rhymes', metrics)
    
    def test_low_rhymes(self):
        """Test handling of lyrics with minimal obvious rhymes."""
        lyrics = """Walking through the market square
Looking at the products there
Nothing special to be found
Just some items all around"""
        
        state = {'lyrics_draft': lyrics, 'structured_plan': {'bpm': 100}}
        result = self.analyzer.execute(state)
        
        self.assertTrue(result.success)
        metrics = result.state_updates.get('lyrical_metrics', {})
        
        self.assertIn('rhyme_factor', metrics)
    
    def test_slant_rhymes(self):
        """Test detection of slant/near rhymes."""
        lyrics = """I'm on the grind, pushing through the night
Every single time, fighting for my right"""
        
        state = {'lyrics_draft': lyrics, 'structured_plan': {'bpm': 100}}
        result = self.analyzer.execute(state)
        
        self.assertTrue(result.success)


class TestFlowAnalyzer(unittest.TestCase):
    """Tests for flow analysis including syllable velocity and PDI."""
    
    def setUp(self):
        self.analyzer = FlowAnalyzer()
    
    def test_syllable_counting(self):
        """Test accurate syllable counting."""
        test_word = "unstoppable"
        count = self.analyzer._count_syllables_accurate(test_word)
        
        self.assertEqual(count, 4)
    
    def test_syllable_line_counting(self):
        """Test syllable counting for full lines."""
        line = "I am counting syllables accurately"
        count = self.analyzer._count_syllables_accurate(line)
        
        self.assertGreater(count, 8)
        self.assertLess(count, 15)
    
    def test_pdi_calculation(self):
        """Test Plosive Density Index calculation."""
        high_pdi_lines = ["Big dogs bark back", "Kick that beat down"]
        low_pdi_lines = ["Smooth sailing all the way", "Flow like water now"]
        
        high_pdi = self.analyzer._calculate_plosive_density_index(high_pdi_lines)
        low_pdi = self.analyzer._calculate_plosive_density_index(low_pdi_lines)
        
        self.assertGreater(high_pdi['pdi'], low_pdi['pdi'])
    
    def test_flow_consistency(self):
        """Test flow consistency calculation."""
        consistent = [10, 10, 11, 10, 10]
        inconsistent = [5, 15, 3, 20, 8]
        
        high_consistency = self.analyzer._calculate_consistency(consistent)
        low_consistency = self.analyzer._calculate_consistency(inconsistent)
        
        self.assertGreater(high_consistency, low_consistency)
    
    def test_breath_injection_detection(self):
        """Test breath injection point detection."""
        long_lines = [
            "This is a very long line that keeps going and going without any punctuation whatsoever",
            "Short line, with breaks"
        ]
        
        breath_analysis = self.analyzer._analyze_breath_points(long_lines)
        
        self.assertGreater(breath_analysis['injections_needed'], 0)
    
    def test_syllable_variance_classification(self):
        """Test flow classification based on syllable variance."""
        syncopated = [10, 12, 11, 13, 10]
        rigid = [10, 10, 10, 10, 10]
        broken = [5, 18, 7, 20, 6]
        
        syncopated_result = self.analyzer._analyze_syllable_variance(syncopated)
        rigid_result = self.analyzer._analyze_syllable_variance(rigid)
        broken_result = self.analyzer._analyze_syllable_variance(broken)
        
        self.assertEqual(rigid_result['classification'], 'rigid_flow')
        self.assertEqual(broken_result['classification'], 'broken_flow')


class TestSyllableCounterAccuracy(unittest.TestCase):
    """Specific tests for syllable counting accuracy."""
    
    def setUp(self):
        self.analyzer = FlowAnalyzer()
    
    def test_common_words(self):
        """Test syllable counts for common words."""
        word_tests = {
            'money': 2,
            'beautiful': 3,
            'extraordinary': 5,
            'a': 1,
            'the': 1,
        }
        
        for word, expected in word_tests.items():
            count = self.analyzer._count_syllables_accurate(word)
            self.assertGreater(count, 0, f"Should have at least 1 syllable for '{word}'")
    
    def test_slang_words(self):
        """Test syllable counts for slang/rap vocabulary."""
        count = self.analyzer._count_syllables_accurate("gonna")
        self.assertEqual(count, 2)
        
        count = self.analyzer._count_syllables_accurate("yeah")
        self.assertEqual(count, 1)


if __name__ == '__main__':
    unittest.main()
