#!/bin/bash
# Test Events Script - Curl Version
# This script creates 5 calendar events and then deletes one

BASE_URL="http://localhost:8080/api/v1/events/"

echo "🚀 Starting Calendar Event Test Script"
echo "======================================"

echo ""
echo "📅 CREATING 5 EVENTS:"
echo "----------------------"

# Event 1
echo ""
echo "🟢 [1/5] Creating meeting with Sarah..."
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{"request": "Create a meeting with Sarah tomorrow at 2 PM about project planning"}' \
  && echo ""

sleep 1

# Event 2  
echo ""
echo "🟢 [2/5] Creating dentist appointment..."
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{"request": "Schedule dentist appointment next Friday at 10 AM"}' \
  && echo ""

sleep 1

# Event 3
echo ""
echo "🟢 [3/5] Creating team standup..."
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{"request": "Book conference room for team standup Tuesday 9 AM"}' \
  && echo ""

sleep 1

# Event 4
echo ""
echo "🟢 [4/5] Creating birthday reminder..."
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{"request": "Set reminder for John birthday party this Saturday 7 PM"}' \
  && echo ""

sleep 1

# Event 5
echo ""
echo "🟢 [5/5] Creating lunch meeting..."
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{"request": "Plan lunch with marketing team next Wednesday at 12:30 PM"}' \
  && echo ""

sleep 2

echo ""
echo "======================================"
echo "🗑️  DELETING EVENT:"
echo "--------------------"

# Delete the dentist appointment
echo ""
echo "🔴 Canceling dentist appointment..."
curl -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{"request": "Cancel my dentist appointment next Friday at 10 AM"}' \
  && echo ""

echo ""
echo "======================================"
echo "✅ Test script completed!"
echo "Check your Celery worker logs to see the processing."
echo "You can also check the database to see stored events." 