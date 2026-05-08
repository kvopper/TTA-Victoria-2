---
name: add-ideology
description: Add a new ideology to the TTA mod. Handles all required files: ideologies.txt, national_focus.txt, Election.txt, poptypes, localisation CSVs (cp1252), country party definitions, start decisions, and history files.
---

# Add Ideology to TTA

Add a new ruling-party ideology to the Victoria 2: The Third Age mod. Every ideology must appear in exactly 10 locations or the CI check fails.

## Information to Gather First

Ask the user for the following before starting. Confirm before proceeding.

- **Ideology key**  -  snake_case identifier, e.g. `line_of_uri` (used in code everywhere)
- **Display name**  -  human-readable, e.g. `Line of Uri` (used in localisation)
- **Ideology group**  -  the group in `common/ideologies.txt` this belongs to, e.g. `dwarves_nobility`
- **Color**  -  RGB triple, e.g. `{ 80 80 90 }`
- **Affected countries**  -  list of `TAG` codes and their country file names (e.g. `BLU` / `Ered Luin`)
- **Party name(s)**  -  the `TAG_partyname` key and the leader's display name for each country (e.g. `BLU_uri_vi` / `Uri VI`)
- **Poptype boosts**  -  what culture(s) and/or religion(s) should get a x2 multiplier in poptypes (e.g. `has_pop_religion = dwarven`, `is_culture_group = dwarves`, `has_pop_culture = longbeard`)
- **Party policies**  -  trade, tax, language, diplomatic, war, good_evil_alignment for each country's party block
- **Start flag**  -  usually `set_country_flag = ideologies_<ideology>_active` plus optionally `set_country_flag = nobility_deactivated`
- **Decision file**  -  which `decisions/*.txt` file gets the start decision

In this project, `TAG` is a 3-letter country code. Country files are at `common/countries/CountryName.txt` and `history/countries/TAG - CountryName.txt`.

## Step-by-Step Changes

Work through these in order. Complete each file before moving to the next.

### 1. `common/ideologies.txt`  -  Define the ideology

Find the ideology group (e.g. `dwarves_nobility = {`) and add the new ideology block before its closing `}`. Insert it adjacent to similar ideologies in the group.

```
	<ideology_key> = {
		color = { R G B }

		add_political_reform = { base = 0 modifier = { factor = 1 ruling_party_ideology = <ideology_key> } }
		remove_political_reform = { base = 0 }
		add_social_reform = { base = 0 modifier = { factor = 1 ruling_party_ideology = <ideology_key> } }
		remove_social_reform = { base = 0 }
		add_military_reform = { base = 0 modifier = { factor = 1 ruling_party_ideology = <ideology_key> } }
		add_economic_reform = { base = 0 modifier = { factor = 1 ruling_party_ideology = <ideology_key> } }
	}
```

### 2. `common/national_focus.txt`  -  Promote and demote focuses

**In `promotion_ideologies`**: insert `promote_<ideology_key>` adjacent to related promotes (e.g. near other dwarf ideologies):

```
	promote_<ideology_key> = {
		ideology = <ideology_key>
		loyalty_value = 0.005
	}
```

**In `demotion_ideologies`**: insert `demote_<ideology_key>` in the same relative position:

```
	demote_<ideology_key> = {
		ideology = <ideology_key>
		loyalty_value = -0.005
	}
```

### 3. `localisation/politics.csv`  -  Ideology display name

**CRITICAL: Use Python to write this file  -  it is cp1252 encoded. Edit tool will corrupt non-ASCII characters.**

Insert after the nearest existing ideology's `_uh` line. Use a Python anchor replacement:

```python
path = 'localisation/politics.csv'
with open(path, 'rb') as f:
    content = f.read().decode('cp1252')
anchor = '<adjacent_ideology_key>_uh;<Adjacent display text>;x\n'
insert = '<ideology_key>;<Display Name>;x\n<ideology_key>_uh;<Display Name> supporters will vote for all reforms while in power.;x\n'
content = content.replace(anchor, anchor + insert, 1)
with open(path, 'wb') as f:
    f.write(content.encode('cp1252'))
```

### 4. `localisation/countries.csv`  -  Party leader names

**CRITICAL: Use Python (cp1252).**

For each country's party, add `TAG_partyname;Leader Name;x`. Insert near other entries for the same country (the file is loosely grouped by country):

```python
path = 'localisation/countries.csv'
with open(path, 'rb') as f:
    content = f.read().decode('cp1252')
anchor = '<adjacent_TAG_partyname>;<Adjacent Leader>;x\n'
insert = '<TAG_partyname>;<Leader Name>;x\n'
content = content.replace(anchor, anchor + insert, 1)
with open(path, 'wb') as f:
    f.write(content.encode('cp1252'))
```

If multiple countries share the same party key format, add each one separately.

### 5. `localisation/modifiers and flags.csv`  -  Three entries

**CRITICAL: Use Python (cp1252).**

Three separate inserts are needed. Do all three in one Python script to avoid re-reading the file three times:

```python
path = 'localisation/modifiers and flags.csv'
with open(path, 'rb') as f:
    content = f.read().decode('cp1252')

# promote entry  -  insert after nearest sibling's promote line
content = content.replace(
    'promote_<adjacent_ideology>;Promote <Adjacent>;x\n',
    'promote_<adjacent_ideology>;Promote <Adjacent>;x\npromote_<ideology_key>;Promote <Display Name>;x\n',
    1
)
# demote entry  -  insert after nearest sibling's demote line
content = content.replace(
    'demote_<adjacent_ideology>;Slander <Adjacent>;x\n',
    'demote_<adjacent_ideology>;Slander <Adjacent>;x\ndemote_<ideology_key>;Slander <Display Name>;x\n',
    1
)
# active flag entry  -  insert after nearest sibling's active flag line
content = content.replace(
    'ideologies_<adjacent_ideology>_active;<Adjacent> Active;x\n',
    'ideologies_<adjacent_ideology>_active;<Adjacent> Active;x\nideologies_<ideology_key>_active;<Display Name> Active;x\n',
    1
)

with open(path, 'wb') as f:
    f.write(content.encode('cp1252'))
```

To find the exact adjacent anchor strings, use:
```bash
python3 -c "
with open('localisation/modifiers and flags.csv', 'rb') as f:
    content = f.read().decode('cp1252')
for i, line in enumerate(content.split('\n')):
    if 'adjacent_ideology' in line:
        print(i+1, line)
"
```

### 6. `common/countries/CountryName.txt`  -  Party definition

For each affected country, open the file and add a `party = { ... }` block. Insert it before any existing `party = { ... }` blocks:

```
party = {
	name = "<TAG_partyname>"
	start_date = 2954.1.1
	end_date = 4000.1.1
	ideology = <ideology_key>
	trade_policy = <trade_policy>
	tax_policy = <tax_policy>
	language_policy = <language_policy>
	diplomatic_policy = <diplomatic_policy>
	war_policy = <war_policy>
	good_evil_alignment = <alignment>
}
```

### 7. `decisions/DecisionFile.txt`  -  Start decision

Add the hidden start decision block. This goes inside the `political_decisions = {` block. Insert after any existing start decisions:

```
	<ideology_key>_start_decision = {
		potential = {
			always = no
		}
		effect = {
			set_country_flag = ideologies_<ideology_key>_active
			set_country_flag = nobility_deactivated
		}
	}
```

Omit `set_country_flag = nobility_deactivated` if this ideology coexists with the generic `nobility` ideology rather than replacing it.

### 8. `events/Election.txt`  -  Events 14006 and 14007

Both events have the same structure  -  a series of `state_scope` blocks, one per non-default ideology. Find where the adjacent ideology's block is in each event, then insert immediately after it.

**Event 14006** (positive  -  `factor = 0.1`):

```
		state_scope = {
			random_owned = {
				limit = { owner = { ruling_party_ideology = <ideology_key> } }
				state_scope = {
					any_pop = {
						ideology = {
							factor = 0.1
							value = <ideology_key>
						}
					}
				}
			}
		}
```

**Event 14007** (negative  -  `factor = -0.1`):

Same block, but `factor = -0.1`.

Use grep to find the right insertion point:
```bash
grep -n "ruling_party_ideology = <adjacent_ideology>" events/Election.txt
```

This will show two line numbers  -  one in event 14006, one in 14007. Insert the new `state_scope` block after the closing `}` of the adjacent block at each location.

### 9. `poptypes/*.txt`  -  Eight pop files

Edit these eight files (NOT slaves.txt, tribals.txt, or bankers.txt):
- `aristocrats.txt`, `artisans.txt`, `bureaucrats.txt`, `capitalists.txt`
- `clergymen.txt`, `craftsmen.txt`, `labourers.txt`, `soldiers.txt`

In each file, find where the adjacent ideology's block ends and insert after it:

```
	<ideology_key> = {
		factor = 1
		# Must be active in the realm
		modifier = {
			factor = 0
			NOT = { country = { has_country_flag = ideologies_<ideology_key>_active } }
		}
		modifier = {
			factor = 2
			<culture_or_religion_boost_1>
		}
		modifier = {
			factor = 2
			<culture_or_religion_boost_2>
		}
		modifier = {
			factor = 2
			ruling_party_ideology = <ideology_key>
		}
	}
```

Common boost conditions:
- `has_pop_religion = dwarven`  -  dwarven religion
- `is_culture_group = dwarves`  -  any dwarf culture
- `has_pop_culture = longbeard`  -  specific dwarf culture
- `has_pop_religion = human_faith`  -  human religion
- `is_culture_group = mannish`  -  any human culture

Use `grep -n "<adjacent_ideology>" poptypes/aristocrats.txt` to find the insertion point, then apply the same relative location in all 8 files (the ideology ordering is consistent across all pop files).

### 10. `history/countries/TAG - CountryName.txt`  -  Starting state

For each affected country, make three changes:

1. Change `ruling_party = <old_party>` to `ruling_party = <TAG_partyname>`
2. Update `upper_house = { ... }` to use the new ideology:
   ```
   upper_house = {
   	<ideology_key> = 100
   }
   ```
3. Add `decision = <ideology_key>_start_decision` at the end of the file.

## Validation

After all changes, run the check script from the repo root:

```bash
python scripts/check-ideologies.py
```

Fix any reported issues before committing. Common mistakes:
- Forgot one of the 8 poptypes
- Localisation anchor not found (Python `replace` silently does nothing if anchor doesn't match exactly  -  verify with a read-back check)
- Wrong TAG in countries.csv
- Missing `_uh` entry in politics.csv

## Common Pitfalls

- **Localisation files are cp1252, not UTF-8.** Never use Edit/Write tools on them. Always use Python with `open(path, 'rb')` / `.decode('cp1252')` / `.encode('cp1252')`.
- **Python `str.replace()` is silent on no-match.** Always verify by reading back and searching for the new line after writing.
- **Party name in history must match the `name` in the country file exactly**  -  e.g. `ruling_party = DOU_skorgrim` requires `name = "DOU_skorgrim"` in `Dourhands.txt`.
- **The `upper_house` block replaces the old one**  -  don't append to it, replace it entirely.
- **Election.txt has two insertion points**  -  one each for events 14006 and 14007. Don't miss the second one.
