"""
Master test runner and integration tests for APEX Engine.

Tests:
- Full workflow execution
- Agent coordination
- State management
- Iteration limits
- PVS calculation
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestWorkflowIntegration(unittest.TestCase):
    """Integration tests for the full APEX workflow."""
    
    def test_workflow_creation(self):
        """Test that the workflow can be created."""
        from src.core.orchestrator import create_workflow
        
        orchestrator = create_workflow()
        self.assertIsNotNone(orchestrator)
        self.assertGreater(len(orchestrator.agents), 0)
    
    def test_workflow_run_simulation(self):
        """Test running workflow in simulation mode."""
        from src.core.orchestrator import create_workflow
        
        orchestrator = create_workflow()
        state = orchestrator.run(
            "Create aggressive trap at 140 BPM",
            max_iterations=1
        )
        
        self.assertIn('status', state)
        self.assertIn('structured_plan', state)
    
    def test_planning_phase(self):
        """Test the planning phase extracts correct parameters."""
        from src.core.orchestrator import APEXOrchestrator
        
        orchestrator = APEXOrchestrator()
        
        bpm = orchestrator._extract_bpm("make a 150 bpm track")
        self.assertEqual(bpm, 150)
        
        bpm = orchestrator._extract_bpm("trap style beat")
        self.assertEqual(bpm, 140)
        
        bpm = orchestrator._extract_bpm("old school boom bap")
        self.assertEqual(bpm, 90)
    
    def test_iteration_limit_enforcement(self):
        """Test that iteration limits are respected."""
        from src.core.orchestrator import create_workflow
        
        orchestrator = create_workflow()
        state = orchestrator.run(
            "Test prompt",
            max_iterations=1
        )
        
        self.assertLessEqual(state.get('iteration_count', 0), 1)


class TestPVSCalculation(unittest.TestCase):
    """Tests for the Predicted Virality Score calculation."""
    
    def test_pvs_formula(self):
        """Test that PVS formula calculates correctly."""
        from src.core.predictor import ViralityPredictor
        
        predictor = ViralityPredictor()
        
        state = {
            'lyrical_metrics': {
                'rhyme_factor': 0.8,
                'flow_consistency': 0.7,
                'plosive_density_index': 0.15
            },
            'analysis_metrics': {
                'syncopation_index': 22,
                'onset_confidence': 0.8,
                'pocket_alignment': 0.9
            }
        }
        
        prediction = predictor.predict(state)
        
        self.assertGreater(prediction.pvs_score, 0)
        self.assertLessEqual(prediction.pvs_score, 1.0)
        self.assertIn(prediction.tier, ['VIRAL_POTENTIAL', 'HIGH', 'MODERATE', 'LOW', 'VERY_LOW'])
    
    def test_pvs_tiers(self):
        """Test that PVS correctly assigns tiers."""
        from src.core.predictor import ViralityPredictor
        
        predictor = ViralityPredictor()
        
        self.assertEqual(predictor._determine_tier(0.9), 'VIRAL_POTENTIAL')
        self.assertEqual(predictor._determine_tier(0.75), 'HIGH')
        self.assertEqual(predictor._determine_tier(0.55), 'MODERATE')
        self.assertEqual(predictor._determine_tier(0.35), 'LOW')
        self.assertEqual(predictor._determine_tier(0.1), 'VERY_LOW')
    
    def test_recommendations_generated(self):
        """Test that recommendations are generated."""
        from src.core.predictor import ViralityPredictor
        
        predictor = ViralityPredictor()
        
        state = {
            'lyrical_metrics': {'rhyme_factor': 0.3},
            'analysis_metrics': {'syncopation_index': 5}
        }
        
        prediction = predictor.predict(state)
        
        self.assertIsInstance(prediction.recommendations, list)


class TestStateSchema(unittest.TestCase):
    """Tests for state management."""
    
    def test_initial_state_creation(self):
        """Test creating initial state."""
        from src.core.state_schema import create_initial_state
        
        state = create_initial_state("Test prompt")
        
        self.assertEqual(state['user_prompt'], "Test prompt")
        self.assertIn(state['status'], ['initialized', 'pending'])
        self.assertEqual(state['iteration_count'], 0)
    
    def test_state_validation(self):
        """Test state validation."""
        from src.core.state_schema import validate_state
        
        valid_state = {
            'user_prompt': 'test',
            'status': 'pending',
            'iteration_count': 0
        }
        
        result = validate_state(valid_state)
        self.assertIsNotNone(result)


class TestAgentBase(unittest.TestCase):
    """Tests for agent base classes."""
    
    def test_agent_result_success(self):
        """Test creating success result."""
        from src.agents.agent_base import AgentResult
        
        result = AgentResult.success_result(
            state_updates={'key': 'value'},
            metadata={'meta': 'data'}
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.state_updates['key'], 'value')
    
    def test_agent_result_failure(self):
        """Test creating failure result."""
        from src.agents.agent_base import AgentResult
        
        result = AgentResult.failure_result(
            errors=['Error message']
        )
        
        self.assertFalse(result.success)
        self.assertIn('Error message', result.errors)


class TestReportGenerator(unittest.TestCase):
    """Tests for report generation."""
    
    def test_full_report_generation(self):
        """Test generating a full report."""
        from src.utils.report_generator import ReportGenerator
        
        generator = ReportGenerator()
        
        state = {
            'lyrical_metrics': {'rhyme_factor': 0.5, 'flow_consistency': 0.6},
            'analysis_metrics': {'syncopation_index': 20, 'onset_confidence': 0.7}
        }
        
        report = generator.generate_full_report(state)
        
        self.assertIn('overall_grade', report)
        self.assertIn('sections', report)


def run_all_tests():
    """Run all tests and print summary."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflowIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestPVSCalculation))
    suite.addTests(loader.loadTestsFromTestCase(TestStateSchema))
    suite.addTests(loader.loadTestsFromTestCase(TestAgentBase))
    suite.addTests(loader.loadTestsFromTestCase(TestReportGenerator))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
