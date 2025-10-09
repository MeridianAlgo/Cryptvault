# CryptVault

CryptVault delivers AI-assisted cryptocurrency analysis with rich pattern detection and polished charting experiences.

## Documentation Hub

- **Product Overview:** `docs/main_README.md`
- **Setup Guides & Verification:** `docs/setup/SETUP_GUIDE.md`, `docs/setup/INSTALLATION_VERIFIED.md`
- **Policy Documents:** `docs/policies/`
- **Technical Deep Dives & Extras:** `docs/`

## CLI vs Core Application

- **`cryptvault_cli.py`** is the interactive command-line entry point. It orchestrates data ingestion, pattern recognition, model execution, and optional desktop visualization for day-to-day usage.
- **`cryptvault.py`** focuses on terminal-based chart rendering. It offers an expressive ASCII dashboard and low-level access for custom scripts or integrations that need the charting layer without the full CLI orchestration.

Use the CLI for end-to-end analysis, multi-asset comparisons, and automation. Use the core script when you need lightweight chart output or want to embed CryptVault visuals in other tooling.

## Repository Structure

```text
.
├── config/                  # Environment templates and overrides
├── cryptvault/              # Core analysis engine, indicators, ML modules
├── docs/                    # Primary documentation bundle
│   ├── main_README.md       # Detailed platform overview & usage
│   ├── setup/               # Installation & verification guides
│   ├── policies/            # Governance and contribution docs
│   └── ...                  # Additional deep dives and references
├── logs/                    # Runtime logs (`cryptvault.log`)
├── tests/                   # Pytest suite for parsers, indicators, ML
├── cryptvault.py            # Terminal charting application
├── cryptvault_cli.py        # Full-featured CLI and desktop launcher
├── requirements.txt         # Python dependencies
├── setup.py                 # Packaging metadata
└── LICENSE                  # MIT license terms
```

## Next Steps

1. Review `docs/main_README.md` for advanced usage patterns and examples.
2. Copy `config/.env.example` to `.env` if you need to override defaults.
3. Run `python -m pytest tests/` to validate installation.
