#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Creating and activating virtual environment..."

source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running Database Migrations..."
alembic upgrade head
