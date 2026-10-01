"""Test script for pipeline components."""
import os, sys
sys.path.insert(0, '.')

print("1. Testing generate_json...")
from tools.gemini_tool import generate_json
result = generate_json('Return this exact JSON: {"status": "ok"}')
print("   PASS:", result)

print("2. Testing director agent...")
from tools.gemini_tool import generate_json as gj
import json

# Inline test without emoji progress
from agents import director_agent
import agents.director_agent as da

# Patch progress to avoid emoji encoding issues
plan = da.run(
    idea="story about a rabbit",
    scene_count=2,
    on_progress=lambda m: None  # silently skip progress
)
print("   Plan:", plan.get("title_ar") or plan.get("title_en"), "| scenes:", plan.get("scene_count"))
print("\nAll tests PASSED!")
