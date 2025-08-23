# miningftw

This folder is ready to push to Git. It includes your miner sheets, config, and placeholders for scripts/reports.

## Structure
```
data/
  btc_miner_sheet.csv        # latest canonical BTC table
  etc_miner_sheet.csv        # latest canonical ETC table
  btc_miner_sheet_v1.csv     # previous BTC (if available)
  etc_miner_sheet_v1.csv     # previous ETC (if available)
config/
  settings.yaml              # example knobs (tariff, pool fee, C6 count, price path)
scripts/
  update_table.py            # placeholder (apply edits; shift v2->v1 if you choose)
  run_profitability.py       # placeholder (compute P&L from config + data)
reports/
  .gitkeep
.github/workflows/
  validate-and-build.yml     # optional CI stub
README.md
.gitignore
requirements.txt
```

## Notes
- Columns are unit-annotated: BTC hashrate in TH/s, ETC hashrate in GH/s, power in W.
- If you keep two working versions locally (v1/v2), treat `data/*_v1.csv` as previous and `data/*_v2.csv` as latest; this starter uses *canonical* files (`*_miner_sheet.csv` as latest) to keep the repo simple.