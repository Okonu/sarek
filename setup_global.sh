#!/bin/bash

echo "🖖 Setting up Sarek globally..."

INSTALL_DIR="/opt/sarek"
BIN_DIR="/usr/local/bin"
CURRENT_DIR=$(pwd)

if [[ $EUID -eq 0 ]]; then
    echo "✅ Running with admin privileges"
else
    echo "❌ This script needs sudo privileges to install globally"
    echo "Run: sudo ./setup_global.sh"
    exit 1
fi

echo "📁 Creating installation directory..."
mkdir -p "$INSTALL_DIR"

echo "📋 Copying Sarek files..."
cp -r "$CURRENT_DIR/sarek" "$INSTALL_DIR/"
cp "$CURRENT_DIR/run_sarek.py" "$INSTALL_DIR/"

echo "🔗 Creating global sarek command..."
cat > "$BIN_DIR/sarek" << 'EOF'
#!/bin/bash
# Global Sarek launcher
cd /opt/sarek
python3 run_sarek.py "$@"
EOF

chmod +x "$BIN_DIR/sarek"
chmod +x "$INSTALL_DIR/run_sarek.py"

chown -R root:root "$INSTALL_DIR"

echo "✅ Global installation complete!"
echo ""
echo "🚀 You can now run Sarek from anywhere with:"
echo "   sarek"
echo "   sarek help"
echo "   sarek 'your query here'"
echo ""
echo "📁 Installation location: $INSTALL_DIR"
echo "🔗 Command location: $BIN_DIR/sarek"
echo ""
echo "🖖 Live long and prosper!"