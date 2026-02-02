# Claude Code Development Notes

This Alfred workflow was developed using [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview).

**IMPORTANT**: Always check `CLAUDE.local.md` for personal/local environment settings before starting work.

## Development History

### Version 1.x (Initial Development)
- **Duration**: 2.5 hours
- **Cost**: ~$10 in API tokens
- Created initial fuzzy search functionality
- Implemented GitHub-based auto-update system
- Added in-memory caching for performance
- Integrated color token icon generation

### Version 2.0 (Major Refactor)
- **Breaking Changes**: Removed all update and caching functionality
- Simplified architecture for maintainability
- Removed dependencies on `urllib`, `time` modules
- Flattened `tokens.json` structure (removed `_meta` wrapper)
- Reduced codebase by 133 lines (-124 deletions, +9 insertions)

### Version 2.0.1 (Token Update)
- Updated all tokens to latest Tapestry 2.0 definitions
- Added 8 new musicstand product color tokens (010-080)
- Added new `--t-spacing-1-half` token (12px)
- Simplified token naming (removed redundant -default/-primary suffixes)
- Regenerated all 352 color token PNG icons with updated values
- Added `generate_icon_script.py` for reproducible icon generation

### Version 2.1.0 (Version Bump)
- Version bump from 2.0.1 to 2.1.0
- Rebuilt workflow package
- **Current token count**: 403 total (352 colors, 51 non-colors)

## Features

### Search & Copy
- **Fuzzy search**: Type partial token names (e.g., "bord dark" finds `--t-border-color-dark`)
- **Instant results**: Returns top 20 matches, sorted by relevance
- **Quick copy**: Press Enter to copy token name to clipboard
- **Visual icons**: Color tokens show actual color previews (64x64 PNG icons)

### Search Algorithm
The fuzzy matching system uses three strategies (in priority order):
1. **Exact substring matching** - Highest priority for direct matches
2. **Character sequence matching** - Finds tokens where query chars appear in order
3. **Similarity ratio** - Uses `difflib.SequenceMatcher` with 0.2 threshold for flexible matching

### Token Support
- **Color tokens**: HSL/HSLA colors with visual icon previews
- **Gradient tokens**: Linear gradients rendered as icon images
- **Non-color tokens**: Spacing, sizing, border-radius, etc. with mono Tapestry icon

## Architecture

### Core Components

**search_tokens.py** (115 lines)
- Main entry point for Alfred Script Filter
- Fuzzy search using three-tier matching strategy:
  - Exact substring matching (position-scored)
  - Character sequence matching (flexible)
  - Similarity ratio matching (`difflib.SequenceMatcher`, threshold: 0.2)
- Token loading from local `tokens.json` (no caching)
- Alfred JSON output formatting with icon configuration
- Detects color tokens by HSL/HSLA prefix
- Returns top 20 results, sorted by relevance

**tokens.json** (403 tokens, ~25KB)
- Flat JSON structure: `{"--token-name": "value"}`
- Keys: CSS custom property names (e.g., `--t-border-radius-sm`)
- Values: CSS values (e.g., `"2px"`, `"hsl(0, 0%, 24%)"`, `"linear-gradient(...)"`)
- Source: Manually parsed from Tapestry's `tokens-alias.css`
- Excludes `var()` references (only concrete values included)

**generate_icon_script.py** (120 lines)
- Standalone Python script using Pillow (PIL)
- Parses HSL/HSLA color strings to RGBA via custom HSL→RGB conversion
- Generates 64x64 PNG icons for all color tokens (352 icons)
- Supports solid colors and linear gradients
- Gradient rendering: Horizontal interpolation between color stops
- Creates `images/*.png` files with sanitized token names

**build.sh** (89 lines)
- Automated semantic versioning (major/minor/patch via CLI argument)
- Reads current version from `info.plist`, bumps, and updates
- Creates `.alfredworkflow` ZIP package
- Excludes development files: `.git`, `.claude`, `build.sh`, `*.pyc`, etc.
- Validates version bump argument before proceeding

**info.plist** (Alfred workflow configuration)
- Workflow metadata: name, bundle ID, description
- Script Filter configuration: keyword `tt`, runs `search_tokens.py`
- Output action: Copy to clipboard (no auto-paste)
- Current version: 2.1.0

### Design Decisions

1. **No Caching**: Reads `tokens.json` fresh from disk on every search
   - Trade-off: Prioritizes simplicity over performance
   - File I/O is fast enough (<100ms for 403 tokens)
   - Eliminates cache invalidation complexity

2. **No Auto-Updates**: Removed GitHub API integration (v2.0)
   - Users manually download new releases from GitHub
   - Eliminates network dependencies and potential failures
   - Reduces code complexity (removed `urllib`, `time` modules)

3. **Local-Only**: Zero network calls during normal operation
   - All data and icons bundled in workflow package
   - Works completely offline

4. **Three-Tier Fuzzy Matching**: Balances accuracy and flexibility
   - Exact matches ranked highest (by position)
   - Sequence matching catches partial/misspelled queries
   - Low similarity threshold (0.2) for very fuzzy queries

5. **Icon Generation**: Pre-generated PNGs instead of dynamic rendering
   - All 352 color icons generated once via `generate_icon_script.py`
   - Faster Alfred display (no runtime rendering)
   - Trade-off: Manual regeneration needed when tokens change

## Development Workflow

### Making Changes

1. Edit source files (`search_tokens.py`, `tokens.json`, etc.)
2. Test changes in Alfred
3. Run build script: `./build.sh [major|minor|patch]`
4. Commit with descriptive message
5. Create GitHub release with built `.alfredworkflow` file

### Updating Tokens from Tapestry Source

1. Fetch latest `tokens-alias.css` from Tapestry repository
2. Parse CSS file to extract token definitions (exclude `var()` references)
3. Update `tokens.json` with parsed values
4. Regenerate color icons: `python3 generate_icon_script.py`
5. Build new version: `./build.sh patch`
6. Commit changes with detailed description

### Adding Individual Tokens

1. Manually add token to `tokens.json`
2. For color tokens, run icon generator or create PNG manually
3. Run `build.sh patch` for token additions

### Modifying Search Logic

The fuzzy matching in [search_tokens.py](search_tokens.py) uses a three-tier approach:

1. **Exact substring matching** (lines 19-21, 72-74)
   - Highest priority: `if query_lower in name_lower`
   - Scored by position: `score = (0, name_lower.index(query_lower))`

2. **Character sequence matching** (lines 23-30)
   - Checks if all query chars appear in order in token name
   - More flexible than substring (allows gaps)

3. **Similarity ratio** (lines 33-34, 76-78)
   - Uses `difflib.SequenceMatcher` with threshold: 0.2
   - Very lenient for fuzzy/misspelled queries

Results are limited to top 20 matches, sorted by score tuple (category, detail).

## Files Overview

```
.
├── search_tokens.py          # Main Python search script (115 lines)
├── tokens.json               # Tapestry token data: 403 tokens (~25KB)
├── generate_icon_script.py  # Icon generation script (120 lines, Pillow/PIL)
├── info.plist                # Alfred workflow config (XML plist, version 2.1.0)
├── build.sh                  # Build & versioning script (89 lines)
├── icon.png                  # Workflow icon (24KB)
├── images/                   # Generated token icons (423 files total)
│   ├── tapestry-icon-*.png   # Mono/color Tapestry logos (2 files)
│   └── --t-*.png             # Color token icons (352 PNGs, 64x64 each)
├── README.md                 # User documentation
├── CLAUDE.md                 # This file (development notes)
├── CLAUDE.local.md           # Personal/local settings (gitignored)
└── .claude/                  # Claude Code settings (gitignored)
    └── settings.local.json   # Local permissions config
```

### Packaged in Workflow
The `.alfredworkflow` file excludes:
- `.git/`, `.claude/` directories
- `build.sh` build script
- `.gitignore`, `.DS_Store`
- Python cache files (`__pycache__/`, `*.pyc`)
- Previous `.alfredworkflow` files

## Performance Characteristics

- **Token count**: 403 total (352 colors, 51 non-colors)
- **Data size**: ~25KB `tokens.json` file
- **Load time**: <100ms (reads and parses JSON on every search)
- **Search time**: <50ms for typical queries (single-pass filtering + sorting)
- **Memory**: Minimal (~1-2MB, no caching between searches)
- **Disk I/O**: 1 file read per search (`tokens.json`)
- **Icon generation**: ~5-10 seconds total for all 352 color icons (one-time via script)
- **Package size**: ~460KB `.alfredworkflow` file (includes all 423 icon PNGs)

## Future Considerations

Potential enhancements if needed:
- **Caching**: Re-add in-memory cache if token count exceeds ~1000 (currently 403)
- **Type filtering**: Add modifiers to filter by token type (colors only, spacing only, etc.)
- **Auto-updates**: Restore GitHub API integration for automatic token updates
- **Token details**: Show computed values, contrast ratios, or usage examples
- **Copy variations**: Modifiers to copy value instead of name (e.g., `hsl(0, 0%, 88%)`)
- **Icon improvements**: Support RGB/hex colors, radial gradients, or larger icon sizes
