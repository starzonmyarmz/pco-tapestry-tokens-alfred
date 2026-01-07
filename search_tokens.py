#!/usr/bin/env python3

import sys
import json
import os
import re
from difflib import SequenceMatcher

_script_dir = os.path.dirname(os.path.abspath(__file__))

def fuzzy_match(query, text, threshold=0.2):
    """Relaxed fuzzy matching using sequence matcher"""
    if not query:
        return True
    
    query = query.lower()
    text = text.lower()
    
    # Exact substring match gets highest priority
    if query in text:
        return True
    
    # Check if all characters in query appear in order in text (more flexible)
    query_idx = 0
    for char in text:
        if query_idx < len(query) and char == query[query_idx]:
            query_idx += 1
    
    if query_idx == len(query):
        return True
    
    # More lenient similarity matching
    similarity = SequenceMatcher(None, query, text).ratio()
    return similarity >= threshold


def fetch_tokens():
    """Load tokens from local JSON file"""
    try:
        tokens_file = os.path.join(_script_dir, 'tokens.json')
        with open(tokens_file, 'r') as f:
            tokens = json.load(f)

        return [
            {
                'name': name,
                'value': value,
                'description': value,
                'is_color': value.startswith(('hsl(', 'hsla('))
            }
            for name, value in tokens.items()
        ]

    except Exception:
        return []

def search_tokens(query):
    """Search tokens with fuzzy matching"""
    tokens = fetch_tokens()
    
    if not query.strip():
        return tokens[:20]
    
    query_lower = query.lower()
    filtered_tokens = []
    
    # Filter and score tokens in one pass
    for token in tokens:
        name_lower = token['name'].lower()
        
        # Quick exact match check first
        if query_lower in name_lower:
            score = (0, name_lower.index(query_lower))
            filtered_tokens.append((token, score))
        elif fuzzy_match(query, token['name']):
            similarity = SequenceMatcher(None, query_lower, name_lower).ratio()
            score = (1, -similarity)
            filtered_tokens.append((token, score))
    
    # Sort by score and return tokens
    filtered_tokens.sort(key=lambda x: x[1])
    return [token for token, _ in filtered_tokens[:20]]


def get_icon_config(token):
    """Get icon configuration for a token"""
    if token['is_color']:
        safe_name = re.sub(r'[^a-zA-Z0-9-]', '_', token['name'])
        icon_path = os.path.join(_script_dir, 'images', f"{safe_name}.png")
        return {"path": icon_path} if os.path.exists(icon_path) else {"type": "default"}
    else:
        mono_path = os.path.join(_script_dir, 'images', 'tapestry-icon-mono.png')
        return {"path": mono_path} if os.path.exists(mono_path) else {"type": "default"}

def main():
    query = sys.argv[1] if len(sys.argv) > 1 else ""

    tokens = search_tokens(query)
    
    # Format results for Alfred
    items = [
        {
            "uid": token['name'],
            "title": token['name'],
            "subtitle": token['description'],
            "arg": token['name'],
            "autocomplete": token['name'],
            "icon": get_icon_config(token)
        }
        for token in tokens
    ]
    
    print(json.dumps({"items": items}, separators=(',', ':')))

if __name__ == "__main__":
    main()