# Code Collector

A script for collecting project source code into a single text file. Recursively traverses project directories, collects files with specified extensions, and saves their contents into one output file. Ignores files and folders based on `.gitignore` and configuration settings.

## How It Works

1. Loads configuration from `code_collector_config.json`
2. Parses `.gitignore` to determine which files and folders to ignore
3. Recursively walks through all project directories
4. Collects files with specified extensions, excluding ignored ones
5. Formats each file with a separator header
6. Saves all content into a single text file with a timestamp in the filename

## Usage

1. Create a `code_collector_config.json` file:
```json
{
    "project_root": "./",
    "file_extensions": [".py", ".js", ".html", ".css"],
    "exclude_folders": ["node_modules", "venv"],
    "additional_ignore_patterns": ["*.min.js"]
}
```

2. Run the script:
```bash
python code_collector.py
```

The result is saved to a file named `collection_YY-MM-DD_HH-MM.txt`.
