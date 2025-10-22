#!/usr/bin/env python3
"""Test search API with metadata filters for Level 5 Evocation spells."""

import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 70)
print("TEST 1: Search with metadata filters (level=5, school=Evocation)")
print("=" * 70)

response = requests.get(
    f"{BASE_URL}/api/references/search",
    params={
        "q": "wizard evocation damage spell",
        "ref_type": "spells_md",
        "level": 5,
        "school": "Evocation",
        "k": 10
    }
)

print(f"Status: {response.status_code}")
data = response.json()
results = data.get("results", [])
print(f"Results found: {len(results)}\n")

if results:
    print("Spells returned:")
    for i, spell in enumerate(results, 1):
        score = spell.get("score", 0)
        title = spell.get("title", "Unknown")
        level = spell.get("level", "?")
        school = spell.get("school", "?")
        print(f"  {i}. {title} (Level {level}, {school}) - Score: {score:.4f}")
else:
    print("  No results found!")

print("\n" + "=" * 70)
print("TEST 2: Search without filters (baseline)")
print("=" * 70)

response2 = requests.get(
    f"{BASE_URL}/api/references/search",
    params={
        "q": "level 5 evocation wizard spell",
        "ref_type": "spells_md",
        "k": 10
    }
)

print(f"Status: {response2.status_code}")
data2 = response2.json()
results2 = data2.get("results", [])
print(f"Results found: {len(results2)}\n")

if results2:
    print("Top 10 spells (no filters):")
    for i, spell in enumerate(results2, 1):
        score = spell.get("score", 0)
        title = spell.get("title", "Unknown")
        level = spell.get("level", "?")
        school = spell.get("school", "?")
        print(f"  {i}. {title} (Level {level}, {school}) - Score: {score:.4f}")
        
print("\n" + "=" * 70)
print("TEST 3: Filter-only query (no semantic search)")
print("=" * 70)

response3 = requests.get(
    f"{BASE_URL}/api/references/search",
    params={
        "ref_type": "spells_md",
        "level": 5,
        "school": "Evocation",
        "k": 10
    }
)

print(f"Status: {response3.status_code}")
data3 = response3.json()
results3 = data3.get("results", [])
print(f"Results found: {len(results3)}\n")

if results3:
    print("Spells returned (filter only, no search query):")
    for i, spell in enumerate(results3, 1):
        title = spell.get("title", "Unknown")
        level = spell.get("level", "?")
        school = spell.get("school", "?")
        print(f"  {i}. {title} (Level {level}, {school})")
else:
    print("  No results found!")

print("\n" + "=" * 70)
print("TEST 4: Chunk-based search with filters")
print("=" * 70)

response4 = requests.get(
    f"{BASE_URL}/api/references/search",
    params={
        "q": "powerful evocation spell damage",
        "ref_type": "spells_md",
        "level": 5,
        "school": "Evocation",
        "use_chunks": True,
        "k": 10
    }
)

print(f"Status: {response4.status_code}")
data4 = response4.json()
results4 = data4.get("results", [])
print(f"Results found: {len(results4)}\n")

if results4:
    print("Spells returned (chunk search with filters):")
    for i, spell in enumerate(results4, 1):
        score = spell.get("score", 0)
        title = spell.get("title", "Unknown")
        level = spell.get("level", "?")
        school = spell.get("school", "?")
        chunks = spell.get("chunks", [])
        print(f"  {i}. {title} (Level {level}, {school}) - Score: {score:.4f}")
        if chunks:
            print(f"      Chunks: {len(chunks)}")
            for chunk in chunks[:2]:  # Show first 2 chunks
                heading = chunk.get("heading", "No heading")
                chunk_score = chunk.get("chunk_score", 0)
                print(f"        - {heading} (score: {chunk_score:.4f})")
