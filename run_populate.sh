#!/bin/bash

echo "🚀 Starting database population..."
echo "=================================================="

# Try the Django management command first
echo "Attempting to use Django management command..."
if python manage.py populate_db --clear; then
    echo
    echo "✅ Database populated successfully using Django management command!"
    exit 0
fi

echo
echo "Django management command failed, trying standalone script..."
echo

# Try the standalone script
if python populate_database.py --clear; then
    echo
    echo "✅ Database populated successfully using standalone script!"
else
    echo
    echo "❌ Both methods failed. Please check the error messages above."
    echo
    echo "Make sure you:"
    echo "1. Are in the project root directory"
    echo "2. Have activated your virtual environment"
    echo "3. Have installed all required dependencies"
    echo "4. Have run database migrations"
    exit 1
fi