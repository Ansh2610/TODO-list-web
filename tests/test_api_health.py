"""
Basic API Health Check
Run this to verify API is running correctly
"""
import httpx
import sys


def test_api_health():
    """Test API health endpoint"""
    try:
        response = httpx.get("http://127.0.0.1:8000/health", timeout=5.0)
        response.raise_for_status()
        data = response.json()
        
        print("✅ API Health Check PASSED")
        print(f"   Status: {data['status']}")
        print(f"   Version: {data['version']}")
        print(f"   LLM Providers: {', '.join(data['llm_providers_configured'])}")
        return True
        
    except httpx.ConnectError:
        print("❌ Cannot connect to API")
        print("   Make sure FastAPI is running:")
        print("   uvicorn api.main:app --reload")
        return False
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_roles_endpoint():
    """Test roles listing endpoint"""
    try:
        response = httpx.get("http://127.0.0.1:8000/api/roles", timeout=5.0)
        response.raise_for_status()
        data = response.json()
        
        print(f"\n✅ Roles Endpoint PASSED")
        print(f"   Found {len(data['roles'])} job roles")
        print(f"   Examples: {', '.join(data['roles'][:3])}")
        return True
        
    except Exception as e:
        print(f"\n❌ Roles endpoint failed: {e}")
        return False


def main():
    """Run all API tests"""
    print("🧪 Testing FastAPI Backend...\n")
    
    results = []
    results.append(test_api_health())
    results.append(test_roles_endpoint())
    
    print("\n" + "="*50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All tests passed ({passed}/{total})")
        print("\nAPI is ready! Start Streamlit with:")
        print("  streamlit run app_streamlit_api.py")
        sys.exit(0)
    else:
        print(f"❌ Some tests failed ({passed}/{total})")
        print("\nMake sure to start the API first:")
        print("  uvicorn api.main:app --reload")
        sys.exit(1)


if __name__ == "__main__":
    main()
