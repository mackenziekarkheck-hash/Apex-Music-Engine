"""
APEX Engine - Autonomous Aural Architectures for Algorithmic Rap Composition.

CLI Entry Point for the hierarchical agentic framework.
Provides interactive prompt-based rap generation and analysis.
"""

import sys
import os
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def print_banner():
    """Print the APEX Engine banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║     █████╗ ██████╗ ███████╗██╗  ██╗    ███████╗███╗   ██╗   ║
    ║    ██╔══██╗██╔══██╗██╔════╝╚██╗██╔╝    ██╔════╝████╗  ██║   ║
    ║    ███████║██████╔╝█████╗   ╚███╔╝     █████╗  ██╔██╗ ██║   ║
    ║    ██╔══██║██╔═══╝ ██╔══╝   ██╔██╗     ██╔══╝  ██║╚██╗██║   ║
    ║    ██║  ██║██║     ███████╗██╔╝ ██╗    ███████╗██║ ╚████║   ║
    ║    ╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝    ╚══════╝╚═╝  ╚═══╝   ║
    ║                                                              ║
    ║    Autonomous Aural Architectures for Algorithmic Rap        ║
    ║                      v0.1.0                                  ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_environment():
    """Check and report on the environment."""
    print("\n[Environment Check]")
    print("-" * 40)
    print(f"Python Version: {sys.version.split()[0]}")
    print(f"Working Directory: {os.getcwd()}")
    
    optional_libs = {
        'librosa': 'Audio DSP analysis',
        'numpy': 'Numerical operations',
        'requests': 'API communication'
    }
    
    print("\nOptional Dependencies:")
    for lib, purpose in optional_libs.items():
        try:
            __import__(lib)
            status = "✓ Available"
        except ImportError:
            status = "✗ Not installed"
        print(f"  {lib}: {status} ({purpose})")
    
    api_keys = {
        'SONAUTO_API_KEY': 'Sonauto API',
        'OPENAI_API_KEY': 'OpenAI LLM'
    }
    
    print("\nAPI Keys:")
    for key, service in api_keys.items():
        status = "✓ Set" if os.environ.get(key) else "✗ Not set (simulation mode)"
        print(f"  {service}: {status}")
    
    print("-" * 40)


def run_demo():
    """Run a demonstration of the APEX Engine."""
    print("\n[Demo Mode]")
    print("-" * 40)
    
    try:
        from apex_engine.src.core import create_workflow, create_initial_state
        from apex_engine.src.core.predictor import ViralityPredictor
        from apex_engine.src.utils.report_generator import ReportGenerator
        
        orchestrator = create_workflow()
        print("✓ Orchestrator initialized")
        print(f"  Available agents: {len(orchestrator.agents)}")
        
        demo_prompt = "Create an aggressive trap banger at 140 BPM with hard-hitting 808s"
        print(f"\nDemo Prompt: \"{demo_prompt}\"")
        
        print("\nRunning workflow (simulation mode)...")
        state = orchestrator.run(demo_prompt, max_iterations=2)
        
        print(f"\n[Workflow Complete]")
        print(f"  Status: {state.get('status')}")
        print(f"  Iterations: {state.get('iteration_count', 0)}")
        print(f"  Credits Used: {state.get('credits_used', 0)}")
        
        if state.get('lyrical_metrics'):
            lm = state['lyrical_metrics']
            print(f"\n[Lyrical Analysis]")
            print(f"  Rhyme Factor: {lm.get('rhyme_factor', 0):.2f}")
            print(f"  Flow Consistency: {lm.get('flow_consistency', 0):.2f}")
        
        if state.get('analysis_metrics'):
            am = state['analysis_metrics']
            print(f"\n[Audio Analysis]")
            print(f"  Detected BPM: {am.get('detected_bpm', 'N/A')}")
            print(f"  Onset Confidence: {am.get('onset_confidence', 0):.2f}")
            print(f"  Syncopation Index: {am.get('syncopation_index', 0):.1f}")
        
        predictor = ViralityPredictor()
        prediction = predictor.predict(state)
        print(f"\n[Virality Prediction]")
        print(f"  PVS Score: {prediction.pvs_score:.2f}")
        print(f"  Tier: {prediction.tier}")
        print(f"  Confidence: {prediction.confidence:.2f}")
        
        report_gen = ReportGenerator()
        report = report_gen.generate_full_report(state)
        print(f"\n[Report Generated]")
        print(f"  Overall Grade: {report['overall_grade']}")
        if report.get('recommendations'):
            print(f"  Top Recommendation: {report['recommendations'][0]}")
        
        print("\n" + "=" * 50)
        print("Demo completed successfully!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ Error during demo: {e}")
        import traceback
        traceback.print_exc()


def run_interactive():
    """Run interactive prompt mode."""
    print("\n[Interactive Mode]")
    print("-" * 40)
    print("Enter your rap generation prompts below.")
    print("Type 'quit' or 'exit' to stop.")
    print("-" * 40)
    
    try:
        from apex_engine.src.core import create_workflow
        from apex_engine.src.utils.report_generator import ReportGenerator
        
        orchestrator = create_workflow()
        report_gen = ReportGenerator()
        
        while True:
            print()
            prompt = input("APEX> ").strip()
            
            if not prompt:
                continue
            
            if prompt.lower() in ('quit', 'exit', 'q'):
                print("Goodbye!")
                break
            
            if prompt.lower() == 'help':
                print("\nCommands:")
                print("  <prompt>  - Generate rap from prompt")
                print("  help      - Show this help")
                print("  quit      - Exit interactive mode")
                continue
            
            print(f"\nProcessing: \"{prompt}\"")
            print("Please wait...")
            
            try:
                state = orchestrator.run(prompt)
                
                print(f"\n[Result]")
                print(f"  Status: {state.get('status')}")
                print(f"  Grade: ", end="")
                
                report = report_gen.generate_full_report(state)
                print(report['overall_grade'])
                
                if state.get('lyrics_validated'):
                    print(f"\n[Generated Lyrics Preview]")
                    lyrics = state['lyrics_validated']
                    lines = lyrics.split('\n')[:8]
                    for line in lines:
                        print(f"  {line}")
                    if len(lyrics.split('\n')) > 8:
                        print("  ...")
                
                orchestrator.reset()
                
            except Exception as e:
                print(f"Error: {e}")
    
    except ImportError as e:
        print(f"Could not start interactive mode: {e}")


def analyze_lyrics(lyrics_file: str):
    """Analyze lyrics from a file."""
    print(f"\n[Analyzing: {lyrics_file}]")
    print("-" * 40)
    
    if not os.path.exists(lyrics_file):
        print(f"Error: File not found: {lyrics_file}")
        return
    
    try:
        with open(lyrics_file, 'r') as f:
            lyrics = f.read()
        
        from apex_engine.src.agents.lyrical import (
            LyricalArchitectAgent,
            BarsAnalyzer,
            FlowAnalyzer,
            VowelAnalyzer
        )
        
        state = {
            'lyrics_draft': lyrics,
            'structured_plan': {'bpm': 100}
        }
        
        architect = LyricalArchitectAgent()
        result = architect.execute(state)
        
        if result.success:
            state.update(result.state_updates)
            
            metrics = state.get('lyrical_metrics', {})
            print(f"\n[Analysis Results]")
            print(f"  Rhyme Factor: {metrics.get('rhyme_factor', 0):.2f}")
            print(f"  Flow Consistency: {metrics.get('flow_consistency', 0):.2f}")
            print(f"  Syllable Variance: {metrics.get('syllable_variance', 0):.2f}")
            
            if result.warnings:
                print(f"\n[Warnings]")
                for w in result.warnings:
                    print(f"  - {w}")
        else:
            print(f"Analysis failed: {result.errors}")
    
    except Exception as e:
        print(f"Error during analysis: {e}")


def main():
    """Main entry point for the APEX Engine."""
    parser = argparse.ArgumentParser(
        description="APEX Engine - Algorithmic Rap Composition Framework"
    )
    parser.add_argument(
        '--demo', 
        action='store_true',
        help='Run a demonstration of the engine'
    )
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Run in interactive prompt mode'
    )
    parser.add_argument(
        '--analyze',
        type=str,
        metavar='FILE',
        help='Analyze lyrics from a file'
    )
    parser.add_argument(
        '--prompt', '-p',
        type=str,
        help='Run a single generation with the given prompt'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress banner output'
    )
    
    args = parser.parse_args()
    
    if not args.quiet:
        print_banner()
    
    check_environment()
    
    if args.demo:
        run_demo()
    elif args.interactive:
        run_interactive()
    elif args.analyze:
        analyze_lyrics(args.analyze)
    elif args.prompt:
        print(f"\n[Single Generation]")
        try:
            from apex_engine.src.core import create_workflow
            orchestrator = create_workflow()
            state = orchestrator.run(args.prompt)
            print(f"Status: {state.get('status')}")
            print(f"Iterations: {state.get('iteration_count', 0)}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("\nUsage Examples:")
        print("  python apex_engine/main.py --demo          # Run demonstration")
        print("  python apex_engine/main.py --interactive   # Interactive mode")
        print("  python apex_engine/main.py --prompt 'trap 140bpm aggressive'")
        print("  python apex_engine/main.py --analyze lyrics.txt")
        print("\nFor more options, run: python apex_engine/main.py --help")


if __name__ == "__main__":
    main()
