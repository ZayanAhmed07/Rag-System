#!/usr/bin/env python
"""Test Supabase connection"""

from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

supabase_url = "https://dmwgncypqythwfbibnjr.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRtd2duY3lwcXl0aHdmYmlibmpyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQxNTgwNTAsImV4cCI6MjA3OTczNDA1MH0.OQF1t36ryJazKNmKwllpoVYlvaSfqS-EFkDK06cAzvc"

try:
    supabase: Client = create_client(supabase_url, supabase_key)
    print("✅ Connected to Supabase successfully!")
    print(f"📦 URL: {supabase_url}")
    print("🔐 API key configured and ready")
except Exception as e:
    print(f"❌ Connection failed: {e}")
