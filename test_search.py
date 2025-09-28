#!/usr/bin/env python3
"""
Test script to analyze Google Search API behavior with Gemini
"""

import os
from google import genai
from google.genai import types

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    api_key = os.environ["GOOGLE_API_KEY"]
    client = genai.Client(api_key=api_key)
except KeyError:
    print("Error: GOOGLE_API_KEY environment variable not set.")
    exit()

MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-2.5-pro")

def test_search_raw():
    """Test 1: Just search, no JSON formatting - see raw response"""
    print("=== TEST 1: Raw Search Response ===")

    search_tool = types.Tool(google_search=types.GoogleSearch())

    prompt = "Search for fertility journey personal experiences reddit"

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[search_tool]
            )
        )

        print("Raw response text:")
        print("-" * 50)
        print(response.text)
        print("-" * 50)

        # Try to extract URLs from raw response
        import re
        urls = re.findall(r'https?://[^\s<>"]{,256}', response.text)
        print(f"\nURLs found in raw response: {len(urls)}")
        for i, url in enumerate(urls[:10], 1):
            print(f"{i}. {url}")

    except Exception as e:
        print(f"Error: {e}")

def test_search_with_json():
    """Test 2: Search with JSON formatting request"""
    print("\n=== TEST 2: Search with JSON Formatting ===")

    search_tool = types.Tool(google_search=types.GoogleSearch())

    prompt = """
    Search for fertility journey personal experiences reddit

    Return exactly 3 results in this JSON format:
    [
      {
        "url": "exact URL from search results",
        "title": "page title"
      }
    ]
    """

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[search_tool]
            )
        )

        print("JSON formatted response:")
        print("-" * 50)
        print(response.text)
        print("-" * 50)

        # Try to parse JSON
        import json
        try:
            start = response.text.find('[')
            end = response.text.rfind(']') + 1
            if start >= 0 and end > start:
                json_str = response.text[start:end]
                results = json.loads(json_str)

                print(f"\nParsed {len(results)} results:")
                for i, result in enumerate(results, 1):
                    print(f"{i}. URL: {result.get('url')}")
                    print(f"   Title: {result.get('title')}")

                    # Test if URL works
                    url = result.get('url')
                    if url:
                        print(f"   Testing URL...")
                        try:
                            import requests
                            resp = requests.head(url, timeout=5, allow_redirects=True)
                            print(f"   Status: {resp.status_code}")
                        except Exception as e:
                            print(f"   URL Error: {str(e)[:50]}...")
                    print()

        except Exception as e:
            print(f"JSON parsing error: {e}")

    except Exception as e:
        print(f"Error: {e}")

def test_search_with_strict_instructions():
    """Test 3: Search with very strict URL copying instructions"""
    print("\n=== TEST 3: Search with Strict URL Instructions ===")

    search_tool = types.Tool(google_search=types.GoogleSearch())

    prompt = """
    Search for fertility journey personal experiences reddit

    CRITICAL INSTRUCTION: Copy URLs EXACTLY as they appear in search results. Do not modify, shorten, or reconstruct URLs.

    Return exactly 2 results in this JSON format:
    [
      {
        "url": "COPY EXACT URL FROM SEARCH - DO NOT CHANGE ANYTHING",
        "title": "page title",
        "note": "describe what you did to get this URL"
      }
    ]
    """

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[search_tool]
            )
        )

        print("Strict instructions response:")
        print("-" * 50)
        print(response.text)
        print("-" * 50)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print(f"🧪 Testing Google Search API behavior with {MODEL_NAME}")
    print("=" * 60)

    test_search_raw()
    test_search_with_json()
    test_search_with_strict_instructions()

    print("\n✅ Test complete!")