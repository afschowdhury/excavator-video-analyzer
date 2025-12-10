#!/usr/bin/env python3
"""
Quick integration test for the refactored HTML report generation system.
Tests the template-based approach with Jinja2.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """Test that all refactored modules can be imported"""
    print("Testing imports...")
    
    try:
        from agents.gemini.html_assembler_agent import HTMLAssemblerAgent
        print("  ✓ HTMLAssemblerAgent imported")
    except Exception as e:
        print(f"  ✗ HTMLAssemblerAgent import failed: {e}")
        return False
    
    try:
        from agents.gemini.joystick_analytics_agent import JoystickAnalyticsAgent
        print("  ✓ JoystickAnalyticsAgent imported")
    except Exception as e:
        print(f"  ✗ JoystickAnalyticsAgent import failed: {e}")
        return False
    
    try:
        from jinja2 import Environment, FileSystemLoader
        print("  ✓ Jinja2 imported")
    except Exception as e:
        print(f"  ✗ Jinja2 import failed: {e}")
        print("  → Install with: pip install jinja2>=3.1.0")
        return False
    
    return True


def test_template_exists():
    """Test that the Jinja2 template file exists"""
    print("\nTesting template file...")
    
    template_path = Path(__file__).parent / "templates" / "report_template.html"
    
    if template_path.exists():
        print(f"  ✓ Template found at {template_path}")
        
        # Check template size
        size_kb = template_path.stat().st_size / 1024
        print(f"  ✓ Template size: {size_kb:.1f} KB")
        
        # Check for key Jinja2 placeholders
        content = template_path.read_text()
        required_vars = [
            '{{ operator_name }}',
            '{{ cycle_metrics',
            '{{ joystick_analytics',
            '{{ performance_scores',
        ]
        
        missing = []
        for var in required_vars:
            if var not in content:
                missing.append(var)
        
        if missing:
            print(f"  ✗ Missing template variables: {missing}")
            return False
        else:
            print(f"  ✓ All required template variables present")
        
        return True
    else:
        print(f"  ✗ Template not found at {template_path}")
        return False


def test_joystick_prompt():
    """Test that the joystick analyzer prompt requests HTML output"""
    print("\nTesting joystick analyzer prompt...")
    
    prompt_path = Path(__file__).parent / "prompts" / "gemini" / "joystick_analyzer.toml"
    
    if prompt_path.exists():
        content = prompt_path.read_text()
        
        # Check for HTML-related keywords
        if 'HTML' in content or 'html' in content:
            print("  ✓ Prompt requests HTML output")
        else:
            print("  ✗ Prompt does not mention HTML")
            return False
        
        # Check that markdown is NOT the primary format
        if 'Markdown format' in content or 'generate the response using strictly this Markdown format' in content:
            print("  ✗ Prompt still requests Markdown format")
            return False
        
        print("  ✓ Prompt updated for HTML output")
        return True
    else:
        print(f"  ✗ Prompt file not found at {prompt_path}")
        return False


def test_requirements():
    """Test that jinja2 is in requirements.txt"""
    print("\nTesting requirements.txt...")
    
    req_path = Path(__file__).parent / "requirements.txt"
    
    if req_path.exists():
        content = req_path.read_text()
        
        if 'jinja2' in content.lower():
            print("  ✓ jinja2 is in requirements.txt")
            return True
        else:
            print("  ✗ jinja2 missing from requirements.txt")
            return False
    else:
        print(f"  ✗ requirements.txt not found")
        return False


def main():
    """Run all integration tests"""
    print("="*70)
    print("HTML Report Refactoring - Integration Test")
    print("="*70)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Template File", test_template_exists()))
    results.append(("Joystick Prompt", test_joystick_prompt()))
    results.append(("Requirements", test_requirements()))
    
    # Summary
    print("\n" + "="*70)
    print("Test Summary")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All integration tests passed!")
        print("\nNext steps:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Run full test: python tests/test_html_report.py --sample-only")
        print("  3. Start Flask app: python app.py")
        return 0
    else:
        print("\n✗ Some integration tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

