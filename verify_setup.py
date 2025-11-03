"""
SkillLens MVP - Quick Verification Script
Checks installation and environment setup
"""
import sys
import os

def check_python_version():
    """Verify Python version is 3.8+"""
    version = sys.version_info
    print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("  ⚠️  Warning: Python 3.8+ recommended")
        return False
    return True

def check_dependencies():
    """Verify all required packages are installed"""
    required = [
        'streamlit',
        'pdfplumber',
        'regex',
        'dotenv',
        'plotly',
        'unidecode'
    ]
    
    missing = []
    for package in required:
        try:
            if package == 'dotenv':
                __import__('dotenv')
            else:
                __import__(package)
            print(f"✓ {package:15} installed")
        except ImportError:
            print(f"✗ {package:15} NOT FOUND")
            missing.append(package)
    
    return len(missing) == 0, missing

def check_files():
    """Verify all required files exist"""
    files = [
        'app_streamlit.py',
        'requirements.txt',
        '.env',
        'backend/security.py',
        'backend/parser.py',
        'backend/skills.py',
        'backend/viz.py',
        'backend/utils.py',
        'data/roles.json',
        'data/skill_bank.json',
        'data/stopwords.txt',
        'tests/run_smoke.py'
    ]
    
    missing = []
    for file in files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file} NOT FOUND")
            missing.append(file)
    
    return len(missing) == 0, missing

def main():
    print("=" * 60)
    print("SkillLens MVP - Environment Verification")
    print("=" * 60)
    
    print("\n1️⃣  Checking Python version...")
    python_ok = check_python_version()
    
    print("\n2️⃣  Checking dependencies...")
    deps_ok, missing_deps = check_dependencies()
    
    print("\n3️⃣  Checking project files...")
    files_ok, missing_files = check_files()
    
    print("\n" + "=" * 60)
    if python_ok and deps_ok and files_ok:
        print("✅ ALL CHECKS PASSED!")
        print("=" * 60)
        print("\nYou're ready to run SkillLens!")
        print("\nQuick Start:")
        print("  1. streamlit run app_streamlit.py")
        print("  2. Upload a PDF resume")
        print("  3. Analyze and download results")
        print("\nFor smoke tests:")
        print("  python -m tests.run_smoke")
        print("=" * 60)
        return 0
    else:
        print("❌ SOME CHECKS FAILED")
        print("=" * 60)
        
        if not python_ok:
            print("\n⚠️  Python version issue detected")
            print("   → Install Python 3.8 or higher")
        
        if not deps_ok:
            print("\n⚠️  Missing dependencies:")
            for dep in missing_deps:
                print(f"   → {dep}")
            print("\n   Fix: pip install -r requirements.txt")
        
        if not files_ok:
            print("\n⚠️  Missing files:")
            for file in missing_files:
                print(f"   → {file}")
            print("\n   Fix: Ensure you're in the project root directory")
        
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
