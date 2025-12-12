"""
Voice Demo Script for Hackathon Judges

Captures voice input, transcribes it, and stores transactions on blockchain.
Works without React Native app - uses Python microphone input.

Requirements:
  pip install speechrecognition pyaudio

Usage:
  python voice_demo.py
"""

import sys
import json
import requests
from pathlib import Path
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    print("⚠️  speech_recognition not installed. Install with: pip install speechrecognition pyaudio")

# API Configuration
API_URL = "http://localhost:5001/test/transactions"
API_STATUS_URL = "http://localhost:5001/test/blockchain/status"


def check_api_connection():
    """Check if test API is running"""
    try:
        response = requests.get("http://localhost:5001/test/health", timeout=2)
        if response.status_code == 200:
            return True
    except:
        pass
    return False


def get_voice_input():
    """Capture voice input from microphone"""
    if not SPEECH_RECOGNITION_AVAILABLE:
        print("\n❌ Speech recognition not available.")
        print("   Install: pip install speechrecognition pyaudio")
        return None
    
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    print("\n" + "=" * 70)
    print("🎤 VOICE INPUT MODE")
    print("=" * 70)
    print("\n📢 Speak your transaction:")
    print("   Examples:")
    print("   - 'राहुल को 500 रुपये का उधार दे दो' (Hindi credit)")
    print("   - 'Give 500 rupees credit to Rahul' (English credit)")
    print("   - '2 किलो चावल 120 रुपये' (Hindi sale)")
    print("   - '2 kg rice 120 rupees' (English sale)")
    print("\n⏸️  Listening... (speak now, or press Ctrl+C to cancel)")
    
    try:
        with microphone as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
        
        print("🔄 Processing audio...")
        
        # Try Hindi first, then English
        transcript = None
        language = None
        
        try:
            # Try Hindi (India)
            transcript = recognizer.recognize_google(audio, language='hi-IN')
            language = 'hi-IN'
            print(f"✅ Detected: Hindi")
        except sr.UnknownValueError:
            try:
                # Try English (India)
                transcript = recognizer.recognize_google(audio, language='en-IN')
                language = 'en-IN'
                print(f"✅ Detected: English")
            except sr.UnknownValueError:
                print("❌ Could not understand audio. Please try again.")
                return None
        except sr.RequestError as e:
            print(f"❌ Speech recognition service error: {e}")
            print("   Note: Requires internet connection for Google Speech API")
            return None
        
        print(f"\n📝 Transcript: {transcript}")
        return {'transcript': transcript, 'language': language}
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        return None
    except sr.WaitTimeoutError:
        print("\n⏱️  Timeout - no speech detected")
        return None
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None


def parse_transaction(transcript, language):
    """
    Parse transcript to extract transaction details.
    This is a simple parser - for demo purposes.
    """
    transcript_lower = transcript.lower()
    
    # Detect transaction type
    tx_type = 'credit'
    if any(word in transcript_lower for word in ['sale', 'buy', 'purchase', 'खरीद', 'बिक्री']):
        tx_type = 'sale'
    elif any(word in transcript_lower for word in ['repay', 'paid', 'चुकाया', 'भुगतान']):
        tx_type = 'repay'
    
    # Extract amount (simple regex-like parsing)
    import re
    amounts = re.findall(r'\d+', transcript)
    amount = 50000  # Default ₹500
    
    if amounts:
        # Take the largest number as amount
        amount_value = int(max(amounts, key=lambda x: int(x)))
        # Convert to paise (assume rupees if < 1000, else already in smaller units)
        if amount_value < 1000:
            amount = amount_value * 100  # Convert rupees to paise
        else:
            amount = amount_value
    
    # Extract customer name (simplified)
    customer_id = 'cust_demo'
    if 'rahul' in transcript_lower or 'राहुल' in transcript:
        customer_id = 'cust_001'
    elif 'priya' in transcript_lower or 'प्रिया' in transcript:
        customer_id = 'cust_002'
    elif 'amit' in transcript_lower or 'अमित' in transcript:
        customer_id = 'cust_003'
    
    return {
        'type': tx_type,
        'amount': amount,
        'customer_id': customer_id,
        'customer_confirmed': True  # Auto-confirm for demo
    }


def send_to_backend(transcript_data, parsed_data):
    """Send transaction to backend API"""
    print("\n" + "=" * 70)
    print("📡 SENDING TO BACKEND")
    print("=" * 70)
    
    # Prepare transaction data
    transaction_data = {
        'transcript': transcript_data['transcript'],
        'type': parsed_data['type'],
        'amount': parsed_data['amount'],
        'customer_id': parsed_data['customer_id'],
        'shopkeeper_id': 'shop_demo',
        'customer_confirmed': parsed_data['customer_confirmed'],
        'language': transcript_data['language']
    }
    
    # Add sale-specific fields if needed
    if parsed_data['type'] == 'sale':
        transaction_data['product'] = 'Demo Product'
        transaction_data['price'] = parsed_data['amount']
        transaction_data['quantity'] = 1
    
    print(f"\n📤 Sending transaction:")
    print(f"   Type: {transaction_data['type']}")
    print(f"   Amount: ₹{transaction_data['amount']/100:.2f}")
    print(f"   Customer: {transaction_data['customer_id']}")
    print(f"   Language: {transaction_data['language']}")
    
    try:
        response = requests.post(API_URL, json=transaction_data, timeout=10)
        
        if response.status_code == 201:
            result = response.json()
            
            print("\n✅ TRANSACTION VERIFIED!")
            print(f"   Status: {result['verification']['status']}")
            print(f"   Storage: {result['verification']['storage_location']}")
            print(f"   Transcript Hash: {result['verification']['transcript_hash'][:16]}...")
            
            if result['verification']['should_write_to_blockchain']:
                if result.get('blockchain'):
                    print(f"\n⛓️  BLOCKCHAIN WRITE SUCCESS!")
                    print(f"   TX Hash: {result['blockchain']['tx_hash']}")
                    print(f"   Block: {result['blockchain']['block_number']}")
                    print(f"   Gas Used: {result['blockchain']['gas_used']}")
                else:
                    print("\n⚠️  Blockchain write attempted but no result")
            else:
                print(f"\n💾 Stored in database: {result['verification']['status']}")
            
            # Show fraud check results
            if result.get('fraud_check'):
                fraud = result['fraud_check']
                if fraud['is_flagged']:
                    print(f"\n⚠️  FRAUD CHECK:")
                    print(f"   Risk Level: {fraud['risk_level']}")
                    print(f"   Score: {fraud['score']:.2f}")
                    if fraud['reasons']:
                        print(f"   Reasons:")
                        for reason in fraud['reasons']:
                            print(f"     - {reason}")
            
            return True
        else:
            print(f"\n❌ API Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to API. Is test_api.py running?")
        print("   Start it with: python test_api.py")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def manual_input_mode():
    """Fallback: Manual text input if microphone not available"""
    print("\n" + "=" * 70)
    print("⌨️  MANUAL INPUT MODE")
    print("=" * 70)
    print("\nEnter transaction transcript:")
    print("   Examples:")
    print("   - राहुल को 500 रुपये का उधार दे दो")
    print("   - Give 500 rupees credit to Rahul")
    print("   - 2 किलो चावल 120 रुपये")
    print()
    
    transcript = input("📝 Transcript: ").strip()
    
    if not transcript:
        print("❌ Empty transcript")
        return None
    
    # Detect language
    language = 'hi-IN'
    if all(ord(c) < 128 for c in transcript):  # ASCII only = English
        language = 'en-IN'
    
    return {'transcript': transcript, 'language': language}


def show_blockchain_status():
    """Show current blockchain status"""
    try:
        response = requests.get(API_STATUS_URL, timeout=2)
        if response.status_code == 200:
            status = response.json()
            print("\n" + "=" * 70)
            print("⛓️  BLOCKCHAIN STATUS")
            print("=" * 70)
            print(f"   Connected: {status.get('connected', False)}")
            if status.get('connected'):
                print(f"   Address: {status.get('address', 'N/A')}")
                print(f"   Contract: {status.get('contract_address', 'N/A')[:20]}...")
                print(f"   Balance: {status.get('balance_eth', 0):.4f} ETH")
                print(f"   Next TX ID: {status.get('next_transaction_id', 0)}")
            return True
    except:
        pass
    return False


def main():
    """Main demo loop"""
    print("\n" + "=" * 70)
    print("🎤 KIRANA VOICE TRANSACTION DEMO")
    print("=" * 70)
    print("\nThis demo captures voice input and stores transactions on blockchain.")
    print("Perfect for hackathon judges to test!")
    
    # Check API connection
    print("\n🔍 Checking API connection...")
    if not check_api_connection():
        print("\n❌ Test API is not running!")
        print("\n📋 To start the API:")
        print("   1. Open a new terminal")
        print("   2. cd whackiest\\backend\\blockchain")
        print("   3. python test_api.py")
        print("\n   Then run this script again.")
        return
    
    print("✅ API is running!")
    
    # Show blockchain status
    show_blockchain_status()
    
    # Main loop
    while True:
        print("\n" + "=" * 70)
        print("🎯 READY FOR VOICE INPUT")
        print("=" * 70)
        print("\nOptions:")
        print("  1. Voice input (microphone)")
        print("  2. Manual text input")
        print("  3. Show blockchain status")
        print("  4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            if not SPEECH_RECOGNITION_AVAILABLE:
                print("\n⚠️  Voice input not available. Use option 2 for manual input.")
                continue
            
            # Get voice input
            transcript_data = get_voice_input()
            if not transcript_data:
                continue
            
            # Parse transaction
            print("\n🔍 Parsing transaction...")
            parsed_data = parse_transaction(
                transcript_data['transcript'],
                transcript_data['language']
            )
            
            # Confirm details
            print(f"\n📋 Transaction Details:")
            print(f"   Type: {parsed_data['type']}")
            print(f"   Amount: ₹{parsed_data['amount']/100:.2f}")
            print(f"   Customer: {parsed_data['customer_id']}")
            
            confirm = input("\n✅ Confirm? (y/n): ").strip().lower()
            if confirm != 'y':
                print("❌ Cancelled")
                continue
            
            # Send to backend
            send_to_backend(transcript_data, parsed_data)
            
        elif choice == '2':
            # Manual input
            transcript_data = manual_input_mode()
            if not transcript_data:
                continue
            
            # Parse transaction
            print("\n🔍 Parsing transaction...")
            parsed_data = parse_transaction(
                transcript_data['transcript'],
                transcript_data['language']
            )
            
            # Confirm details
            print(f"\n📋 Transaction Details:")
            print(f"   Type: {parsed_data['type']}")
            print(f"   Amount: ₹{parsed_data['amount']/100:.2f}")
            print(f"   Customer: {parsed_data['customer_id']}")
            
            confirm = input("\n✅ Confirm? (y/n): ").strip().lower()
            if confirm != 'y':
                print("❌ Cancelled")
                continue
            
            # Send to backend
            send_to_backend(transcript_data, parsed_data)
            
        elif choice == '3':
            show_blockchain_status()
            
        elif choice == '4':
            print("\n👋 Exiting demo. Thank you!")
            break
        
        else:
            print("\n❌ Invalid option")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

