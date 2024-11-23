import requests
import json
import os
from time import sleep

# Replace this with your Render URL once deployed
API_URL = "https://your-app-name.onrender.com"

def test_api_health():
    """Test if the API is running"""
    try:
        response = requests.get(f"{API_URL}/")
        print("\n1. API Health Check:")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_convert_to_word():
    """Test Word document conversion"""
    print("\n2. Testing Word Conversion:")
    data = {
        "title": "Test Document",
        "sections": {
            "Introduction": "This is a test document.",
            "Chapter 1": {
                "Section 1.1": "This is section 1.1",
                "Section 1.2": "This is section 1.2"
            },
            "Conclusion": "This is the conclusion."
        }
    }
    
    try:
        response = requests.post(
            f"{API_URL}/convert?format=word",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            with open("test_output.docx", "wb") as f:
                f.write(response.content)
            print("✓ Word document created successfully")
            return True
        else:
            print(f"Error: {response.json().get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_convert_to_pdf():
    """Test PDF conversion"""
    print("\n3. Testing PDF Conversion:")
    data = {
        "title": "Test Document",
        "sections": {
            "Introduction": "This is a test document.",
            "Chapter 1": {
                "Section 1.1": "This is section 1.1",
                "Section 1.2": "This is section 1.2"
            },
            "Conclusion": "This is the conclusion."
        }
    }
    
    try:
        response = requests.post(
            f"{API_URL}/convert?format=pdf",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            with open("test_output.pdf", "wb") as f:
                f.write(response.content)
            print("✓ PDF document created successfully")
            return True
        else:
            print(f"Error: {response.json().get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_error_handling():
    """Test error handling"""
    print("\n4. Testing Error Handling:")
    
    # Test with invalid JSON
    print("\na) Testing with invalid JSON:")
    try:
        response = requests.post(
            f"{API_URL}/convert?format=word",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Test with invalid format
    print("\nb) Testing with invalid format:")
    try:
        response = requests.post(
            f"{API_URL}/convert?format=invalid",
            json={"test": "data"},
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {str(e)}")

def run_all_tests():
    """Run all tests"""
    print("Starting API Tests...")
    
    # Test 1: Health Check
    if not test_api_health():
        print("❌ Health check failed. Waiting 30 seconds for cold start...")
        sleep(30)
        if not test_api_health():
            print("❌ Health check failed again. Exiting tests.")
            return
    
    # Test 2: Word Conversion
    test_convert_to_word()
    
    # Test 3: PDF Conversion
    test_convert_to_pdf()
    
    # Test 4: Error Handling
    test_error_handling()
    
    print("\nTest Results:")
    if os.path.exists("test_output.docx"):
        print("✓ Word document test passed")
    if os.path.exists("test_output.pdf"):
        print("✓ PDF document test passed")

if __name__ == "__main__":
    run_all_tests()
