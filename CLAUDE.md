# Claude Code Development Notes

This Alfred workflow was developed using [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview).

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
- Total: 464 tokens (352 colors, 112 non-colors)

## Architecture

### Core Components

**search_tokens.py**
- Main search logic using fuzzy matching with `difflib.SequenceMatcher`
- Token loading from local `tokens.json` file
- Alfred JSON output formatting
- Icon configuration for color tokens

**tokens.json**
- Flat JSON structure containing Tapestry design tokens
- Keys: CSS custom property names (e.g., `--t-border-radius-sm`)
- Values: CSS values (e.g., `"2px"`, `"hsl(0, 0%, 24%)"`)
- Source: Parsed from Tapestry's `tokens-alias.css` file

**generate_icon_script.py**
- Python script using Pillow (PIL) to generate color token icons
- Parses HSL/HSLA color values and creates 64x64 PNG images
- Handles both solid colors and linear gradients
- Generates 352 icons for all color tokens

**build.sh**
- Automated versioning (major/minor/patch)
- Creates `.alfredworkflow` package
- Excludes development files via `.gitignore` patterns

### Design Decisions

1. **No Caching**: Simplified loading by reading tokens fresh from disk each time
   - Trade-off: Slightly slower performance for maintainability
   - File I/O is fast enough for ~400 tokens

2. **No Auto-Updates**: Removed GitHub API integration
   - Users manually update by downloading new releases
   - Eliminates network dependencies and potential failures

3. **Local-Only**: All functionality works offline
   - No external API calls during normal operation

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

The fuzzy matching in `search_tokens.py` uses:
- Exact substring matching (highest priority)
- Character sequence matching (flexible)
- Similarity ratio matching (threshold: 0.2)

Results are limited to top 20 matches, sorted by relevance.

## Files Overview

```
.
├── search_tokens.py          # Main Python search script
├── tokens.json               # Tapestry design token data (464 tokens)
├── generate_icon_script.py  # Icon generation script (Pillow/PIL)
├── info.plist                # Alfred workflow configuration
├── build.sh                  # Build and versioning script
├── icon.png                  # Workflow icon
├── images/                   # Generated token icons (352 PNGs)
│   ├── tapestry-icon-*.png   # Mono/color Tapestry logos
│   └── --t-*.png             # Individual color token icons (64x64)
├── README.md                 # User documentation
└── CLAUDE.md                 # This file
```

## Performance Characteristics

- **Token count**: 464 total (352 colors, 112 non-colors)
- **Load time**: <100ms for 464 tokens
- **Search time**: <50ms for typical queries
- **Memory**: Minimal (no caching)
- **Disk I/O**: ~1 file read per search
- **Icon generation**: ~5-10 seconds for all 352 color icons

## Future Considerations

If the workflow needs to be extended:
- Consider adding caching back if token count grows significantly (>1000)
- Could implement update checking if auto-updates become valuable
- Potential for filtering by token type (colors, spacing, etc.)
