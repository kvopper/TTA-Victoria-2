# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Victoria 2: The Third Age (TTA)** is a Lord of the Rings total conversion mod for Victoria 2. It replaces the entire Victoria 2 experience -map, countries, events, technologies, cultures, religions -with Middle Earth content set during the War of the Ring era (starting date: 2954 Third Age). The mod also improves Victoria 2's UI with quality-of-life features (static modifiers viewer, province location overlays in decisions, dynamic localization).

## Validation Scripts

Three Python scripts in [scripts/](scripts/) validate mod consistency. Run them from the repo root after making relevant changes:

```bash
python scripts/check-encoding.py        # Verify all localisation/ files are Windows-1252 encoded
python scripts/check-terrains.py        # Verify custom terrains exist across all required files
python scripts/check-ideologies.py      # Verify ideologies are registered in all required places
```

These also run automatically in CI on push/PR to `main`. Most content (events, decisions, history, etc.) is **not** covered by these scripts - changes there must be verified by running the game.

## File Encoding

**All localisation CSV files must be Windows-1252 encoded** (not UTF-8). Victoria 2 requires this. The `check-encoding.py` script enforces it. When editing localisation files, ensure your editor saves in Windows-1252 / cp1252.

## Architecture

### Victoria 2 Mod File Format

Most game data files use a custom Clausewitz-engine text format (`.txt`), not JSON/XML. The syntax is:

```
identifier = {
    key = value
    nested_block = {
        ...
    }
}
```

Comments use `#`. String values use `"quotes"` or bare words.

### Key Content Areas

| Directory | Purpose |
|-----------|---------|
| [common/](common/) | Core game definitions: countries, ideologies, governments, religions, cultures, goods, buildings, traits, CB types, defines.lua |
| [events/](events/) | Scripted events (`.txt`). Each event has an `id`, `trigger`, `mean_time_to_happen`, and `option` blocks |
| [decisions/](decisions/) | Player-selectable decisions (`.txt`). Have `potential`, `allow`, `effect` blocks |
| [history/countries/](history/countries/) | Starting conditions per country: ruling party, tech levels, reforms |
| [history/provinces/](history/provinces/) | Per-province starting state: owner, controller, pops, buildings |
| [localisation/](localisation/) | Windows-1252 CSV files mapping keys to displayed text. Format: `KEY;English text;;;;;;;;;` |
| [map/](map/) | Province definitions, terrain, adjacencies, positions |
| [technologies/](technologies/) | 7 tech tree files (army, navy, commerce, diplomacy, military_theory, knowledge, population) |
| [inventions/](inventions/) | Invention unlocks triggered by technologies |
| [poptypes/](poptypes/) | Population type definitions must reference every ideology |
| [interface/](interface/) | UI layout files (`.gui`, `.gfx`) |
| [gfx/](gfx/) | Graphics assets |

### Ideology System

When adding a new ideology, it must be registered in **all** of the following (the `check-ideologies.py` script enforces this):
1. `common/ideologies.txt` -definition
2. `common/countries/*.txt` -party entries for each country
3. `localisation/politics.csv` -display name and upper house (`_uh`) variant
4. `common/national_focus.txt` -`promote_<ideology>` and `demote_<ideology>` entries
5. `events/Election.txt` -events 14006 and 14007
6. `localisation/modifiers and flags.csv` -`ideologies_<ideology>_active` entry
7. Every `poptypes/*.txt` file (except slaves, tribals, bankers)

### Terrain System

When adding a new terrain type, it must appear in (enforced by `check-terrains.py`):
1. `localisation/terrain.csv`
2. `events/Work Place.txt` (event 12057)
3. `interface/province_interface.gfx` -`GFX_terrainimg_<terrain>` sprite entry
4. `map/terrain.txt` -categories block

### Engine Constants

[common/defines.lua](common/defines.lua) overrides Victoria 2 defaults for the fantasy setting. Notable changes:
- `GREAT_NATIONS_COUNT = 4` (vanilla: 8)
- `start_date = '2954.1.1'`, `end_date = '3100.12.31'`

### Localisation CSV Format

```
KEY;English text;French;German;Polish;Spanish;Italian;Swedish;Czech;Hungarian;Dutch;Braz_Por;Russian;Finnish;
```

Only the English column (index 1) is populated. Keys in the `### Section ###` comment headers delimit sections used by `check-ideologies.py`.

### Dynamic Localisation

TTA uses Victoria 2's dynamic localisation feature for context-aware tooltips and descriptions. Static portions are embedded in decision/event scripts; the CSV provides the text templates.

## Victoria 2 Modding Reference

**Always check the wiki before writing Clausewitz script** to avoid hallucinating invalid effects, conditions, or scopes.

### Core Scripting References
- [List of effects](https://vic2.paradoxwikis.com/List_of_effects) - used in `effect` blocks in events, decisions, and elsewhere
- [List of conditions](https://vic2.paradoxwikis.com/List_of_conditions) - used in `trigger`, `limit`, `allow`, `potential` blocks, and conditional things like CB types and news
- [List of scopes](https://vic2.paradoxwikis.com/List_of_scopes) - how to scope effects/conditions to a country, province, or pop

### Tutorials
- [Event modding](https://vic2.paradoxwikis.com/Event_modding)
- [How to make a decision](https://vic2.paradoxwikis.com/How_to_make_a_decision)
- [Creating a country](https://vic2.paradoxwikis.com/Creating_a_country)
- [Dynamic localisation](https://vic2.paradoxwikis.com/Dynamic_localisation)
- [IF Emulation](https://vic2.paradoxwikis.com/IF_Emulation)
