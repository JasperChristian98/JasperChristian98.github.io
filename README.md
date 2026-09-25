# McDraft — source-preserving modular build

This repository is an **incremental modularisation** of the supplied 25,514-line `Draft (1)(6).py`, preserving its features and original execution order. The `mcdraft/stages/` files are coherent, ordered source chunks. They **share an explicit execution context through `mcdraft/pipeline.py`**; they are *not* yet separately importable, dependency-injected packages. This avoids silently breaking the many cross-stage global dependencies in the existing dashboard. The manifest and offline tests confirm no original source was omitted or reordered.

## Install / run locally

Requires Python 3.12.

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python run.py
```

The build writes `index.html`, `fpl_draft_history.json` and `draft_player_mapping_audit.csv` in the repository root. Open `index.html` in your browser, or enable GitHub Pages with deployment from the root of the `main` branch. Runtime requires access to the official Premier League Draft and Classic FPL APIs.

## Migrate your current GitHub repo

1. Back up the repository and its `fpl_draft_history.json` first; **copy that existing history into this repository root** before the first run, otherwise the dashboard starts a new history.
2. Replace the included header-only `draft_player_mapping.csv` with your **actual current** mapping CSV. The uploaded `.py` did not include the mapping file, so the archive cannot supply your manual corrections. Running with the empty template could misattribute players; inspect `draft_player_mapping_audit.csv` after your first run.
3. Copy these files and `.github/workflows/update-dashboard.yml` to your repository, **replacing the old scheduled workflow** to prevent concurrent legacy and modular runs.
4. If GitHub Pages is already publishing `index.html` from `main`, leave that setting alone. Otherwise set **Settings → Pages → Deploy from a branch → main / (root)**.
5. Run the workflow manually once before relying on the automated schedule.

The GitHub Actions workflow runs every 10 minutes Friday–Monday and 20 minutes Tuesday–Thursday. GitHub cron uses UTC, can delay or skip runs when busy and is not a guaranteed real-time scheduler. Configure Actions workflow permissions to permit read/write if pushes fail.

## Module guide

| Stage | Purpose |
|---|---|
| 01_collect | FPL Draft snapshots, ID mapping, gameweek history |
| 02_enrich | Current FPL data, injuries, ownership, transfers |
| 03_match_analytics | Fixtures, results, team analytics |
| 04_visualisations | Plotly charts and HTML helpers |
| 05_forecasts | Fixture projections, ratings and simulations |
| 06_live_and_planning | Live Centre, planner, trade and waiver models |
| 07_pages | Page HTML, player and squad views, analytics |
| 08_page_data | Page payloads and base styles |
| 09_client_assets | Browser JavaScript and additional CSS |
| 10_cup_and_template | Cup logic, editorial content and main HTML |
| 11_publish | Template substitution and output generation |

**Important:** Files in `stages/` are not independently executable or safe to reorder. Use `python run.py`, which guarantees their order and context. Keep `mcdraft/manifest.json` in sync if manually modifying stage source: source-preservation tests intentionally fail after changes until you explicitly update the manifest. When iterating on the modular code later, replacing exact-source checks with behavioural fixtures is the next step.

## Reliability notes

- All original feature-producing code is retained verbatim. An existing bug remains an existing bug; source preservation is not proof of runtime correctness.
- The offline checks cover extraction completeness, parsing and important feature functions. **A live, end-to-end API build has not been run here** and should be validated manually via GitHub Actions after migration.
- The pipeline restores your previous `index.html` if a build fails; it does **not** roll back history changes already made during collection. Back up historical JSON before migration.
- The script's original API calls, notebook display code, and global state have not been rewritten. A future full refactor should introduce explicit typed objects/data contracts and fixture-backed integration tests.

## Decision Centre (Overview)

The Overview now has a **Decision Centre** card. It reuses the existing five-GW
planner and Manager War Room data; it does **not** run a second forecasting model.
It prioritises flagged projected starters, next-GW upgrades, distinct longer-term
opportunities, positional mismatches and approaching poor squad weeks. Up to four
nonduplicated cards link to the existing detailed pages. It is a read-only
briefing: no waiver or lineup changes are submitted.

`mcdraft/decision_centre.py` is a standalone, unit-tested module. The pipeline
integrates it after stage 07, attaches its CSS and JS after stage 09, and inserts
the Overview card after stage 10. The original 11 legacy stages remain unchanged,
so the original-source preservation checks continue to pass.

## Matchup stats and trade packages

My Team → Stats includes completed-fixture records, weekly schedule luck,
opponent records, and player contributions from captured starting lineups.
Expected league points average the points a manager would earn against every
other completed score that week (three for a win, one for a draw). Fixture luck
is actual minus expected league points; it is not a player-performance forecast.
Missing historical lineups are shown as missing coverage, not inferred.

The Negotiation Room searches position-compatible 1-for-1, 2-for-2 and 3-for-3
packages. The first results rotate through all three sizes, and filters select
the partner, package size and negotiation type. Labels always use the selected
manager's perspective: Ambitious asks for a value upgrade, Safe gives the partner
a value advantage without reducing their modelled fit, and Even has similar
values and acceptable fit on both sides. These are model judgements, not measured
acceptance probabilities. Trade Lab and Trade History have separate tabs;
loading an offer selects the entire package in Trade Lab.

`mcdraft/matchup_stats.py` and `mcdraft/trade_negotiation.py` are integrated by the
pipeline without modifying the preserved legacy stages.
