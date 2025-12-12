# Voice Input Setup Guide

Yes, you can test with voice! Here's how to set it up.

## Step 1: Install Voice Recognition Packages

### Option A: Standard Installation (Try this first)

```powershell
# Activate your virtual environment first (if using one)
cd helloKittyFanclub\backend
.\venv\Scripts\Activate.ps1

# Install packages
pip install speechrecognition pyaudio
```

### Option B: Windows - If pyaudio fails (Common on Windows)

If `pyaudio` installation fails, use `pipwin`:

```powershell
# Install pipwin first
pip install pipwin

# Then install pyaudio via pipwin
pipwin install pyaudio

# Install speechrecognition normally
pip install speechrecognition
```

### Option C: Alternative - Use conda (if you have Anaconda)

```powershell
conda install pyaudio
pip install speechrecognition
```

---

## Step 2: Verify Installation

Test if packages are installed:

```powershell
python -c "import speech_recognition; print('✅ speech_recognition installed')"
python -c "import pyaudio; print('✅ pyaudio installed')"
```

---

## Step 3: Test Voice Input

### Start Test API (Terminal 1)

```powershell
cd helloKittyFanclub\backend\blockchain
python test_api.py
```

**Keep this running!**

### Run Voice Demo (Terminal 2)

```powershell
cd helloKittyFanclub\backend\blockchain
python voice_demo.py
```

### Select Option 1: Voice Input

1. When prompted, select **option 1** (Voice input)
2. Wait for "⏸️ Listening..." message
3. **Speak clearly** into your microphone:
   - Hindi: `राहुल को 500 रुपये का उधार दे दो`
   - English: `Give 500 rupees credit to Rahul`
4. The script will automatically stop after 10 seconds or when you stop speaking
5. You'll see the transcript
6. Confirm the transaction (type `y`)
7. Watch for blockchain write confirmation!

---

## What You'll See

```
🎤 VOICE INPUT MODE
======================================================================

📢 Speak your transaction:
   Examples:
   - 'राहुल को 500 रुपये का उधार दे दो' (Hindi credit)
   - 'Give 500 rupees credit to Rahul' (English credit)

⏸️  Listening... (speak now, or press Ctrl+C to cancel)

🔄 Processing audio...
✅ Detected: Hindi

📝 Transcript: राहुल को 500 रुपये का उधार दे दो

🔍 Parsing transaction...

📋 Transaction Details:
   Type: credit
   Amount: ₹500.00
   Customer: cust_001

✅ Confirm? (y/n): y

📡 SENDING TO BACKEND
======================================================================

✅ TRANSACTION VERIFIED!
   Status: verified
   Storage: blockchain
   Transcript Hash: a1b2c3d4...

⛓️  BLOCKCHAIN WRITE SUCCESS!
   TX Hash: 0xabc123...
   Block: 12345
   Gas Used: 145830
```

---

## Troubleshooting Voice Input

### Issue: "Speech recognition not available"

**Solution:**
- Make sure you installed both packages: `pip install speechrecognition pyaudio`
- If pyaudio failed, use `pipwin install pyaudio`

### Issue: "No speech detected" or "Could not understand audio"

**Solutions:**
1. **Check microphone permissions:**
   - Windows: Settings → Privacy → Microphone → Allow apps to access microphone
   - Make sure Python/terminal has microphone access

2. **Speak clearly and wait:**
   - Wait for "Listening..." message before speaking
   - Speak clearly and at normal pace
   - Make sure microphone is working (test in other apps)

3. **Check microphone:**
   - Test microphone in Windows Sound Settings
   - Make sure it's the default input device

4. **Try manual input first:**
   - Use option 2 to verify the rest of the flow works
   - Then troubleshoot voice separately

### Issue: "Speech recognition service error"

**Solution:**
- Voice recognition uses Google Speech API (requires internet)
- Make sure you have internet connection
- Check firewall isn't blocking Python

### Issue: "pyaudio installation fails"

**Windows Solution:**
```powershell
pip install pipwin
pipwin install pyaudio
```

**Alternative - Download wheel file:**
1. Go to: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
2. Download the `.whl` file matching your Python version
3. Install: `pip install PyAudio-0.2.11-cp39-cp39-win_amd64.whl` (adjust version)

---

## Quick Test Commands

```powershell
# 1. Install (if not done)
pip install speechrecognition pyaudio

# 2. Test installation
python -c "import speech_recognition, pyaudio; print('✅ Ready for voice!')"

# 3. Start API
cd helloKittyFanclub\backend\blockchain
python test_api.py

# 4. In another terminal, run voice demo
cd helloKittyFanclub\backend\blockchain
python voice_demo.py
# Select option 1, then speak!
```

---

## Tips for Best Results

1. **Speak clearly** - Enunciate each word
2. **Wait for prompt** - Don't speak until you see "Listening..."
3. **Quiet environment** - Reduce background noise
4. **Close to microphone** - Speak 6-12 inches from mic
5. **Test phrases:**
   - Hindi: `राहुल को 500 रुपये का उधार दे दो`
   - English: `Give 500 rupees credit to Rahul`
   - Sale: `2 किलो चावल 120 रुपये`

---

## Fallback: Manual Input

If voice doesn't work, you can always use **option 2** (Manual input) to test the transaction flow and blockchain write. The voice is just for convenience - the core functionality works the same!

---

## Success Checklist

- [ ] `speechrecognition` installed
- [ ] `pyaudio` installed
- [ ] Microphone permissions granted
- [ ] Test API running (`test_api.py`)
- [ ] Voice demo script running (`voice_demo.py`)
- [ ] Can see "Listening..." message
- [ ] Transcript appears after speaking
- [ ] Transaction created successfully
- [ ] Blockchain write confirmed

Good luck with voice testing! 🎤

