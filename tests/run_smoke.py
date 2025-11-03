"""
Smoke test for SkillLens MVP
Tests PDF parsing, skill extraction, and coverage calculation
"""
import os
import sys
from backend.parser import extract_text_from_pdf
from backend.utils import load_json
from backend.skills import extract_skills, flatten_categories, coverage_against_role


def main():
    print("=" * 60)
    print("SkillLens MVP - Smoke Test")
    print("=" * 60)
    
    # Check if sample PDF exists
    sample_pdf_path = "tests/sample_resume.pdf"
    if not os.path.exists(sample_pdf_path):
        print(f"\n⚠️  Sample PDF not found at: {sample_pdf_path}")
        print("Please add a sample resume PDF to tests/sample_resume.pdf")
        print("You can use any text-based PDF resume for testing.")
        print("\nSkipping PDF parsing test...")
        text = "Python Java JavaScript React Node.js Flask SQL Docker Git APIs REST OOP Pandas NumPy Leadership"
        print(f"\n✅ Using mock text for remaining tests: {len(text)} chars")
    else:
        # 1) Load sample PDF
        print(f"\n1️⃣  Testing PDF parsing...")
        with open(sample_pdf_path, "rb") as f:
            pdf_bytes = f.read()
        
        text = extract_text_from_pdf(pdf_bytes)
        assert isinstance(text, str) and len(text) > 0, "PDF parsing failed"
        print(f"   ✅ PDF parsed successfully: {len(text)} chars")

    # 2) Extract skills
    print(f"\n2️⃣  Testing skill extraction...")
    skill_bank = load_json("data/skill_bank.json")
    extracted = extract_skills(text, skill_bank)
    flat = flatten_categories(extracted)
    
    print(f"   ✅ Skills extracted by category:")
    for cat, skills in extracted.items():
        print(f"      - {cat}: {len(skills)} skills")
    print(f"   ✅ Total unique skills: {len(flat)}")

    # 3) Coverage vs role
    print(f"\n3️⃣  Testing role coverage calculation...")
    roles = load_json("data/roles.json")
    
    for role in ["Software Engineer", "Data Analyst"]:
        coverage, missing = coverage_against_role(flat, roles[role])
        
        # Assertions for validation
        assert isinstance(coverage, int), f"Coverage should be int, got {type(coverage)}"
        assert 0 <= coverage <= 100, f"Coverage should be 0-100, got {coverage}"
        assert isinstance(missing, list), f"Missing should be list, got {type(missing)}"
        
        print(f"   ✅ Coverage vs {role}: {coverage}%")
        if missing:
            print(f"      Missing: {', '.join(missing[:5])}{'...' if len(missing) > 5 else ''}")
    
    # 4) Validate result structure (as would be downloaded)
    print(f"\n4️⃣  Testing result JSON structure...")
    result_dict = {
        "target_role": "Software Engineer",
        "coverage": coverage,
        "missing_skills": missing,
        "extracted_by_category": extracted,
        "extracted_flat_unique": flat
    }
    
    assert "coverage" in result_dict and isinstance(result_dict["coverage"], int), "Result must contain 'coverage' as int"
    assert "missing_skills" in result_dict and isinstance(result_dict["missing_skills"], list), "Result must contain 'missing_skills' as list"
    assert "extracted_by_category" in result_dict and isinstance(result_dict["extracted_by_category"], dict), "Result must contain 'extracted_by_category' as dict"
    print(f"   ✅ Result JSON structure valid")

    print("\n" + "=" * 60)
    print("✅ All smoke tests passed!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run the Streamlit app: streamlit run app_streamlit.py")
    print("2. Upload a PDF resume and test the full workflow")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
