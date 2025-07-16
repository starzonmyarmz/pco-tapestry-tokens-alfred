#!/usr/bin/env python3

import sys
import json
import os
import re
import time
import urllib.request
import urllib.error
from difflib import SequenceMatcher

# Global cache for better performance
_cached_tokens = None
_tapestry_mono_icon = None
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


def check_for_updates(force_update=False):
    """Check for token updates using GitHub commit hash"""
    try:
        tokens_file = os.path.join(_script_dir, 'tokens.json')
        update_check_file = os.path.join(_script_dir, '.last_update_check')
        commit_hash_file = os.path.join(_script_dir, '.commit_hash')
        
        # Check if we need to update (1 hour expiry) unless forced
        current_time = time.time()
        if not force_update and os.path.exists(update_check_file):
            with open(update_check_file, 'r') as f:
                last_check = float(f.read().strip())
            if current_time - last_check < 3600:  # 1 hour
                return False
        
        # Get latest commit hash from GitHub API
        api_url = "https://api.github.com/repos/starzonmyarmz/tapestry-tokens-alfred-extension/commits/main"
        with urllib.request.urlopen(api_url, timeout=5) as response:
            commit_data = json.loads(response.read().decode())
            remote_hash = commit_data['sha'][:7]  # Short hash
        
        # Check local commit hash
        local_hash = ""
        if os.path.exists(commit_hash_file):
            with open(commit_hash_file, 'r') as f:
                local_hash = f.read().strip()
        
        # Update last check time
        with open(update_check_file, 'w') as f:
            f.write(str(current_time))
        
        # Download new tokens if hash is different or forced
        if force_update or remote_hash != local_hash:
            tokens_url = "https://raw.githubusercontent.com/starzonmyarmz/tapestry-tokens-alfred-extension/main/tokens.json"
            with urllib.request.urlopen(tokens_url, timeout=10) as response:
                new_tokens = response.read().decode()
            
            # Backup old tokens
            if os.path.exists(tokens_file):
                backup_file = tokens_file + '.bak'
                os.rename(tokens_file, backup_file)
            
            # Save new tokens
            with open(tokens_file, 'w') as f:
                f.write(new_tokens)
            
            # Save new commit hash
            with open(commit_hash_file, 'w') as f:
                f.write(remote_hash)
            
            # Clear cache to force reload
            global _cached_tokens
            _cached_tokens = None
            
            return True
            
    except Exception:
        # Silently fail - don't break the workflow
        pass
    
    return False


def force_update_tokens():
    """Force update tokens by bypassing commit hash check"""
    return check_for_updates(force_update=True)


def fetch_tokens():
    """Load tokens from local JSON file with caching"""
    global _cached_tokens
    if _cached_tokens is not None:
        return _cached_tokens
    
    # Check for updates first
    check_for_updates()
    
    try:
        tokens_file = os.path.join(_script_dir, 'tokens.json')
        with open(tokens_file, 'r') as f:
            token_data = json.load(f)
        
        # Handle both old and new format
        tokens = token_data.get('tokens', token_data)
        if '_meta' in tokens:
            tokens = {k: v for k, v in tokens.items() if k != '_meta'}
        
        _cached_tokens = [
            {
                'name': name,
                'value': value,
                'description': value,
                'is_color': value.startswith(('hsl(', 'hsla('))
            }
            for name, value in tokens.items()
        ]
        return _cached_tokens
        
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
    global _tapestry_mono_icon
    
    if token['is_color']:
        safe_name = re.sub(r'[^a-zA-Z0-9-]', '_', token['name'])
        icon_path = os.path.join(_script_dir, 'images', f"{safe_name}.png")
        return {"path": icon_path} if os.path.exists(icon_path) else {"type": "default"}
    else:
        if _tapestry_mono_icon is None:
            mono_path = os.path.join(_script_dir, 'images', 'tapestry-icon-mono.png')
            _tapestry_mono_icon = {"path": mono_path} if os.path.exists(mono_path) else {"type": "default"}
        return _tapestry_mono_icon

def main():
    query = sys.argv[1] if len(sys.argv) > 1 else ""
    
    # Handle manual update command
    if query.strip().lower() == "update":
        updated = force_update_tokens()
        if updated:
            items = [{
                "uid": "update_success",
                "title": "✅ Tokens updated successfully",
                "subtitle": "Downloaded latest tokens from GitHub",
                "icon": {"path": os.path.join(_script_dir, 'images', 'tapestry-icon-color.png')}
            }]
        else:
            items = [{
                "uid": "update_no_change",
                "title": "ℹ️ No updates available",
                "subtitle": "Tokens are already up to date",
                "icon": {"path": os.path.join(_script_dir, 'images', 'tapestry-icon-mono.png')}
            }]
        
        print(json.dumps({"items": items}, separators=(',', ':')))
        return
    
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