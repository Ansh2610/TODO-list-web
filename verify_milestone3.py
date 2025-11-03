"""
Quick verification script for Milestone 3 AI features
Tests that all modules import correctly and basic functionality works
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all new modules can be imported"""
    print("Testing imports...")
    
    try:
        from backend.redact import redact_text
        print("✅ backend.redact imported")
    except Exception as e:
        print(f"❌ backend.redact failed: {e}")
        return False
    
    try:
        from backend.schemas import validate_ai_payload, AIRecommendations
        print("✅ backend.schemas imported")
    except Exception as e:
        print(f"❌ backend.schemas failed: {e}")
        return False
    
    try:
        from backend.llm_router import LLMRouter
        print("✅ backend.llm_router imported")
    except Exception as e:
        print(f"❌ backend.llm_router failed: {e}")
        return False
    
    try:
        from backend.benchmark import get_ai_recommendations, build_prompt
        print("✅ backend.benchmark imported")
    except Exception as e:
        print(f"❌ backend.benchmark failed: {e}")
        return False
    
    return True


def test_redaction():
    """Test PII redaction"""
    print("\nTesting PII redaction...")
    from backend.redact import redact_text
    
    text = "Contact me at john.doe@email.com or call 555-123-4567"
    redacted = redact_text(text)
    
    assert "john.doe@email.com" not in redacted
    assert "555-123-4567" not in redacted
    assert "[EMAIL]" in redacted or "[PHONE]" in redacted
    print(f"✅ PII redaction works: {redacted}")
    return True


def test_schema_validation():
    """Test Pydantic schema validation"""
    print("\nTesting schema validation...")
    from backend.schemas import validate_ai_payload
    
    # Valid payload
    valid = {
        "coverage_explanation": "You have a strong foundation in Python and data analysis.",
        "top_missing_skills": "Focus on learning Docker and Kubernetes for DevOps skills.",
        "learning_path": "Start with Docker basics, then move to K8s. Use free online courses.",
        "project_ideas": "Build a containerized web app. Deploy it using Kubernetes.",
        "resume_tweaks": "Highlight your Python projects more prominently in the experience section."
    }
    
    result = validate_ai_payload(valid)
    assert result is not None
    print("✅ Valid payload passed validation")
    
    # Invalid payload (missing field)
    invalid = {
        "coverage_explanation": "Test",
        "top_missing_skills": "Test"
        # Missing other required fields
    }
    
    try:
        validate_ai_payload(invalid)
        print("❌ Invalid payload should have failed")
        return False
    except ValueError:
        print("✅ Invalid payload correctly rejected")
    
    return True


def test_prompt_builder():
    """Test prompt construction"""
    print("\nTesting prompt builder...")
    from backend.benchmark import build_prompt
    
    prompt = build_prompt(
        extracted_skills=["Python", "SQL", "Git"],
        missing_skills=["Docker", "Kubernetes"],
        role_name="Data Engineer",
        coverage_pct=60
    )
    
    assert "Python" in prompt
    assert "Docker" in prompt
    assert "Data Engineer" in prompt
    assert "60%" in prompt
    print(f"✅ Prompt built successfully ({len(prompt)} chars)")
    return True


def test_llm_router_init():
    """Test LLM router initialization"""
    print("\nTesting LLM router initialization...")
    from backend.llm_router import LLMRouter
    
    router = LLMRouter()
    assert router.timeout == 20
    assert router.max_tokens == 800
    print(f"✅ LLM router initialized (providers: {router.providers})")
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("Milestone 3 AI Features - Verification Script")
    print("=" * 60)
    
    all_passed = True
    
    tests = [
        ("Imports", test_imports),
        ("PII Redaction", test_redaction),
        ("Schema Validation", test_schema_validation),
        ("Prompt Builder", test_prompt_builder),
        ("LLM Router Init", test_llm_router_init),
    ]
    
    for name, test_func in tests:
        try:
            if not test_func():
                all_passed = False
        except Exception as e:
            print(f"❌ {name} failed with exception: {e}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All tests passed! Milestone 3 is ready.")
    else:
        print("❌ Some tests failed. Check the output above.")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
