"""
Setup script to check environment and create mock results if needed
"""
import os
import sys

def check_api_keys():
    """Check if API keys are available"""
    openai_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    if openai_key:
        print("✓ OpenAI API key found")
        return "openai"
    elif anthropic_key:
        print("✓ Anthropic API key found")
        return "anthropic"
    else:
        print("✗ No API keys found")
        print("  Will run with simulated results for demonstration")
        return None

if __name__ == "__main__":
    api_available = check_api_keys()
    sys.exit(0 if api_available else 1)
