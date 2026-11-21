# DevBuddy Workshop

An intelligent agent built with [Google ADK](https://github.com/google/adk) to assist Python developers with package version checking, update comparison, and vulnerability audits using PyPI and OSV.dev.

## Features

- **Latest Version Lookup:** Checks PyPI in real time for package release information.
- **Version Comparison:** Determines semantic version differences (major, minor, patch) and update status.
- **Vulnerability Checks:** Queries OSV.dev (Google's open-source vulnerability database) for known security issues.

## Setup

1. **Create and activate a virtual environment (Python 3.12+):**
   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install "google-adk[eval]"
   ```

3. **Configure environment variables:**
   Copy `.env.example` to `.env` and provide your API credentials:
   ```bash
   cp .env.example .env
   ```

4. **Run the agent web interface:**
   ```bash
   adk web
   ```
