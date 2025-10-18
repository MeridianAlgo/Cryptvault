# Contributing to CryptVault

Thank you for your interest in contributing to CryptVault! This project is an educational tool for cryptocurrency analysis using AI/ML and charting. Contributions help improve pattern recognition, documentation, and usability while keeping the focus on research and learning.

## Code of Conduct
- Be respectful and inclusive.
- Follow the MIT License terms.
- Avoid contributions that promote financial advice or trading. CryptVault is for education only.

## How to Contribute

1. **Fork the Repository**:
   - Fork https://github.com/MeridianAlgo/Cryptvault to your GitHub account.

2. **Set Up Your Environment**:
   - Clone your fork: `git clone https://github.com/MeridianAlgo/Cryptvault.git`
   - Install dependencies: `pip install -r requirements.txt`
   - Copy `config/.env.example` to `.env` and configure as needed.
   - Run tests: `python -m pytest tests/` to verify setup.

3. **Make Changes**:
   - Create a branch: `git checkout -b feature/your-feature-name`
   - Focus on areas like:
     - Improving AI/ML models (e.g., new pattern detections).
     - Enhancing charting in `cryptvault.py` or CLI in `cryptvault_cli.py`.
     - Adding tests in `tests/`.
     - Updating docs in `docs/` (e.g., examples in `main_README.md`).
   - Ensure code is Pythonic, well-commented, and follows PEP 8.
   - Do not introduce dependencies without updating `requirements.txt`.

4. **Test Your Changes**:
   - Run the full test suite: `python -m pytest tests/`
   - Manually test CLI and charting features.
   - Check logs in `logs/` for issues.

5. **Commit and Push**:
   - Commit with clear messages: `git commit -m "Add new pattern recognition for XYZ"`
   - Push to your fork: `git push origin feature/your-feature-name`

6. **Open a Pull Request**:
   - Go to the original repo and create a PR from your branch.
   - Describe changes, reference issues if applicable, and explain educational value.
   - PRs will be reviewed for quality, relevance, and security.

## Issue Reporting
- Use GitHub Issues for bugs, feature requests, or questions.
- Provide details: Steps to reproduce, environment, and logs from `cryptvault.log`.

## Recognition
- Contributors are credited in release notes and `docs/` if applicable.

We appreciate all contributions that align with CryptVault's educational mission!`
