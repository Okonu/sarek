#!/bin/bash

echo "🖖 Installing Sarek dependencies using system packages..."

echo "📦 Updating package list..."
sudo apt update

echo "🔧 Installing core dependencies..."
sudo apt install -y \
    python3-requests \
    python3-rich \
    python3-git \
    python3-psutil \
    python3-full

echo "🎤 Installing voice dependencies (optional)..."
sudo apt install -y \
    python3-speechrecognition \
    python3-pyttsx3 \
    portaudio19-dev \
    python3-pyaudio \
    espeak \
    espeak-data

chmod +x run_sarek.py

echo "✅ Installation complete!"
echo ""
echo "🚀 You can now run Sarek with:"
echo "   ./run_sarek.py"
echo "   or"
echo "   python3 run_sarek.py"
echo ""
echo "🖖 Live long and prosper!"