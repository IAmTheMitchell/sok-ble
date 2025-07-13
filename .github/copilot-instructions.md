# Background
sok-ble is a library written in Python. Its purpose is to connect to SOK LiFePO4 batteries over Bluetooth low energy and send and receive modbus commands. sok-ble then parses the responses and returns usable data. The primary intent is for sok-ble to be utilized/wrapped/consumed by sok-ha, a custom integration for Home Assistant; however, sok-ble may be used by any 3rd party and must remain independent of Home Assistant.

# Documentation
- Use Markdown for all documentation

# Python
- Use uv to manage Python and all python packages
- Use 'uv add [package_name]' instead of 'uv pip install [package_name]'

# Testing
- Use pytest for Python testing
- Ensure all code is formatted and linted with Ruff.

# Files
- Do not create binary files, such as Lambda zip files.
- Do not modify CHANGELOG.md. This is handled by CI.

# Commits
- Use conventional commits for all changes 
    - Prefix all commit messages with fix:; feat:; build:; chore:; ci:; docs:; style:; refactor:; perf:; or test: as appropriate.
    