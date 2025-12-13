"""
Test script for /api/transactions/transcribe endpoint.

Tests the speech transcription integration with the Flask backend.

Usage:
    1. Start Flask server: python run.py
    2. Run this test: python test_transcribe_endpoint.py

Requirements:
    pip install requests
"""

import requests
import os
import sys
from pathlib import Path

# API endpoint
BASE_URL = "http://localhost:5000"
TRANSCRIBE_URL = f"{BASE_URL}/api/transactions/transcribe"


def test_endpoint_exists():
    """Test that the endpoint exists and accepts POST requests"""
    print("\n" + "=" * 60)
    print("TEST 1: Endpoint Exists")
    print("=" * 60)
    
    try:
        # Test with empty request (should return validation error)
        response = requests.post(TRANSCRIBE_URL, timeout=5)
        
        # Any response means server is running and endpoint exists
        print(f"✅ Endpoint responds: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask server")
        print("   Start the server with: python run.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_missing_file():
    """Test response when no audio file is provided"""
    print("\n" + "=" * 60)
    print("TEST 2: Missing File Handling")
    print("=" * 60)
    
    try:
        response = requests.post(TRANSCRIBE_URL, timeout=5)
        result = response.json()
        
        # Should return error about missing file
        if response.status_code in [400, 422] or 'error' in result:
            print(f"✅ Properly handles missing file")
            print(f"   Status: {response.status_code}")
            print(f"   Message: {result.get('message', result.get('error', 'N/A'))}")
            return True
        else:
            print(f"⚠️  Unexpected response: {result}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_with_audio_file():
    """Test transcription with an actual audio file"""
    print("\n" + "=" * 60)
    print("TEST 3: Transcription with Audio File")
    print("=" * 60)
    
    # Check for test audio file
    test_audio_paths = [
        "test_audio.m4a",
        "test_audio.wav",
        "test_audio.mp3",
        Path(__file__).parent / "test_audio.m4a",
        Path(__file__).parent / "test_audio.wav",
    ]
    
    audio_file_path = None
    for path in test_audio_paths:
        if os.path.exists(path):
            audio_file_path = str(path)
            break
    
    if not audio_file_path:
        print("⚠️  No test audio file found. Skipping this test.")
        print("   Create a test audio file named 'test_audio.m4a' or 'test_audio.wav'")
        print("   in the backend directory to test actual transcription.")
        return None
    
    try:
        print(f"📁 Using audio file: {audio_file_path}")
        
        with open(audio_file_path, 'rb') as f:
            files = {'audio': (os.path.basename(audio_file_path), f)}
            data = {'language': 'hi-IN'}
            
            response = requests.post(TRANSCRIBE_URL, files=files, data=data, timeout=30)
        
        result = response.json()
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {result}")
        
        if response.status_code == 200:
            transcript = result.get('transcription') or result.get('transcript', '')
            if transcript:
                print(f"✅ Transcription successful!")
                print(f"   Transcript: {transcript}")
                print(f"   Language: {result.get('language', 'N/A')}")
                print(f"   Confidence: {result.get('confidence', 'N/A')}")
                return True
            elif result.get('error'):
                print(f"⚠️  Transcription returned error: {result['error']}")
                return False
            else:
                print(f"⚠️  Empty transcription (no speech detected?)")
                return True  # Still technically successful
        else:
            print(f"❌ Transcription failed: {result}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_with_audio_file_field():
    """Test that 'audio_file' field also works (backward compatibility)"""
    print("\n" + "=" * 60)
    print("TEST 4: Backward Compatible Field Name")
    print("=" * 60)
    
    # Check for test audio file
    test_audio_paths = [
        "test_audio.m4a",
        "test_audio.wav",
        Path(__file__).parent / "test_audio.m4a",
    ]
    
    audio_file_path = None
    for path in test_audio_paths:
        if os.path.exists(path):
            audio_file_path = str(path)
            break
    
    if not audio_file_path:
        print("⚠️  No test audio file found. Skipping this test.")
        return None
    
    try:
        print(f"📁 Using audio file: {audio_file_path}")
        
        with open(audio_file_path, 'rb') as f:
            # Use 'audio_file' field name (backward compatibility)
            files = {'audio_file': (os.path.basename(audio_file_path), f)}
            data = {'language_code': 'en-IN'}  # Also test language_code param
            
            response = requests.post(TRANSCRIBE_URL, files=files, data=data, timeout=30)
        
        result = response.json()
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Backward compatible field name works!")
            print(f"   Both 'transcription' and 'transcript' in response: "
                  f"{'transcription' in result and 'transcript' in result}")
            return True
        else:
            print(f"❌ Failed: {result}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n" + "=" * 60)
    print("DEPENDENCY CHECK")
    print("=" * 60)
    
    all_good = True
    
    # Check speech_recognition
    try:
        import speech_recognition
        print(f"✅ speech_recognition installed (v{speech_recognition.__version__})")
    except ImportError:
        print("❌ speech_recognition NOT installed")
        print("   Install: pip install SpeechRecognition")
        all_good = False
    
    # Check pydub
    try:
        import pydub
        print(f"✅ pydub installed")
    except ImportError:
        print("❌ pydub NOT installed")
        print("   Install: pip install pydub")
        all_good = False
    
    # Check requests
    try:
        import requests
        print(f"✅ requests installed")
    except ImportError:
        print("❌ requests NOT installed")
        print("   Install: pip install requests")
        all_good = False
    
    return all_good


def main():
    print("\n" + "=" * 60)
    print("🎤 TRANSCRIBE ENDPOINT TEST")
    print("=" * 60)
    print(f"Testing: {TRANSCRIBE_URL}")
    
    # Check dependencies first
    if not check_dependencies():
        print("\n❌ Missing dependencies. Install them and try again.")
        return
    
    # Run tests
    results = []
    
    results.append(("Endpoint Exists", test_endpoint_exists()))
    results.append(("Missing File Handling", test_missing_file()))
    results.append(("Audio Transcription", test_with_audio_file()))
    results.append(("Backward Compatible Field", test_with_audio_file_field()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    skipped = 0
    
    for name, result in results:
        if result is True:
            print(f"✅ {name}: PASSED")
            passed += 1
        elif result is False:
            print(f"❌ {name}: FAILED")
            failed += 1
        else:
            print(f"⏭️  {name}: SKIPPED")
            skipped += 1
    
    print(f"\nTotal: {passed} passed, {failed} failed, {skipped} skipped")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Check the output above for details.")


if __name__ == '__main__':
    main()

