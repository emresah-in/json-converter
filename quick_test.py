import requests
import json
import webbrowser

# Your Render URL
API_URL = "https://json-converter-sem2.onrender.com"

# Test data
test_data = {
    "title": "Quick Test Document",
    "sections": {
        "Introduction": "This is a test of the JSON converter API.",
        "Chapter 1": {
            "Section 1.1": "This is the first section.",
            "Section 1.2": "This is the second section."
        },
        "Conclusion": "This is the end of our test document."
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
            print(f"Download URL: {result['download_url']}")
            print(f"Expires in: {result['expires_in']}")
            
            # Automatically open the download URL in browser
            webbrowser.open(result['download_url'])
        else:
            print(f"Error: {response.status_code}")
            try:
                print(response.json())
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
    
    # Test conversion
    test_conversion()
