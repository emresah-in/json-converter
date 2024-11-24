import requests
import json
import webbrowser
import time

# Your Render URL
API_URL = "https://json-converter-sem2.onrender.com"

# Test data with simplified structure
test_data = {
    "title": "Sample Document",
    "sections": {
        "Introduction": "This is an introduction to our document.",
        "Main Content": {
            "Section 1": "This is the first main section.",
            "Section 2": "This is the second main section.",
            "Subsections": {
                "Subsection 2.1": "This is a subsection.",
                "Subsection 2.2": "This is another subsection."
            }
        },
        "Conclusion": "This is the conclusion of our document."
    }
}

def test_conversion():
    print("\nTesting document conversion...")
    try:
        response = requests.post(
            f"{API_URL}/convert",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Success!")
            
            # Handle both old and new response formats
            if 'download_url' in result:
                print(f"Download URL: {result['download_url']}")
                print(f"Expires in: {result['expires_in']}")
                webbrowser.open(result['download_url'])
            else:
                print("Response:")
                print(json.dumps(result, indent=2))
        else:
            print(f"Error: {response.status_code}")
            try:
                error_data = response.json()
                print("Error response:")
                print(json.dumps(error_data, indent=2))
            except:
                print(response.text[:200])
    except Exception as e:
        print(f"Error: {str(e)}")

def test_api_health():
    print("\nTesting API health...")
    try:
        response = requests.get(f"{API_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    # First check if API is running
    test_api_health()
    
    print("\nWaiting for deployment to complete...")
    time.sleep(5)  # Wait a bit for deployment
    
    # Test conversion
    test_conversion()
