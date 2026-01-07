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

### Adding New Tokens

1. Update `tokens.json` with new token key/value pairs
2. Run `build.sh patch` for token additions
3. Rebuild color icons if adding new color tokens

### Modifying Search Logic

The fuzzy matching in `search_tokens.py` uses:
- Exact substring matching (highest priority)
- Character sequence matching (flexible)
- Similarity ratio matching (threshold: 0.2)

Results are limited to top 20 matches, sorted by relevance.

## Files Overview

```
.
├── search_tokens.py       # Main Python search script
├── tokens.json            # Tapestry design token data
├── info.plist            # Alfred workflow configuration
├── build.sh              # Build and versioning script
├── icon.png              # Workflow icon
├── images/               # Generated token icons
│   ├── tapestry-icon-*.png
│   └── --t-*.png        # Individual color token icons
├── README.md             # User documentation
└── CLAUDE.md             # This file
```

## Performance Characteristics

- **Load time**: <100ms for ~400 tokens
- **Search time**: <50ms for typical queries
- **Memory**: Minimal (no caching)
- **Disk I/O**: ~1 file read per search

## Future Considerations

If the workflow needs to be extended:
- Consider adding caching back if token count grows significantly (>1000)
- Could implement update checking if auto-updates become valuable
- Potential for filtering by token type (colors, spacing, etc.)
