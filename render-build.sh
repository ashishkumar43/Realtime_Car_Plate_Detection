echo "Installing Tesseract OCR..."
apt-get install -y tesseract-ocr
echo "Setting environment variable for Tesseract..."
export TESSERACT_PATH="/usr/bin/tesseract"