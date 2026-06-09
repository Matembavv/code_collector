"""
Script for collecting project code into a single text file.
Reads configuration from code_collector_config.json, traverses project folders,
ignores files and folders specified in .gitignore,
and saves all code to an output file.
"""

import os
import json
import fnmatch
from pathlib import Path
from typing import List, Set
from datetime import datetime


def load_config(config_path: str = "code_collector_config.json") -> dict:
    """Loads configuration from a JSON file."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in '{config_path}': {e}")
        exit(1)


def parse_gitignore(project_root: str) -> List[str]:
    """Parses .gitignore file and returns a list of patterns to ignore."""
    gitignore_path = os.path.join(project_root, '.gitignore')
    patterns = []
    
    if os.path.exists(gitignore_path):
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(line)
        except Exception as e:
            print(f"Warning: Could not read .gitignore: {e}")
    
    return patterns


def should_ignore(path: str, ignore_patterns: List[str], project_root: str) -> bool:
    """
    Checks if a path should be ignored based on patterns.
    """
    try:
        rel_path = os.path.relpath(path, project_root)
    except ValueError:
        return False
    
    parts = Path(rel_path).parts
    for part in parts:
        if part.startswith('.') and part != '.':
            return True
    
    for pattern in ignore_patterns:
        if not pattern:
            continue
        
        if pattern.startswith('!'):
            continue

        pattern = pattern.rstrip('/')
        
        if fnmatch.fnmatch(os.path.basename(path), pattern):
            return True
        
        if fnmatch.fnmatch(rel_path, pattern):
            return True

        path_parts = rel_path.replace('\\', '/').split('/')
        pattern_parts = pattern.replace('\\', '/').split('/')
        
        for i in range(len(path_parts) - len(pattern_parts) + 1):
            if fnmatch.fnmatch('/'.join(path_parts[i:i+len(pattern_parts)]), 
                              '/'.join(pattern_parts)):
                return True
    
    return False


def collect_files(project_root: str, extensions: List[str], 
                 ignore_patterns: List[str]) -> List[str]:
    """
    Collects all files with specified extensions, ignoring specified patterns.
    """
    collected_files = []
    
    for root, dirs, files in os.walk(project_root):
        dirs_to_remove = []
        for d in dirs:
            dir_path = os.path.join(root, d)
            if should_ignore(dir_path, ignore_patterns, project_root):
                dirs_to_remove.append(d)
        
        for d in dirs_to_remove:
            dirs.remove(d)
        
        for file in files:
            file_path = os.path.join(root, file)
            
            _, ext = os.path.splitext(file)
            if ext.lower() in [e.lower() for e in extensions]:
                if not should_ignore(file_path, ignore_patterns, project_root):
                    collected_files.append(file_path)
    
    return sorted(collected_files)


def read_file_content(file_path: str) -> str:
    """Reads file content with handling of various encodings."""
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
        except Exception as e:
            return f"Error reading file: {e}"
    
    return "Error: Unsupported file encoding"


def format_header(file_path: str, project_root: str) -> str:
    """Formats a header for a file."""
    try:
        rel_path = os.path.relpath(file_path, project_root)
    except ValueError:
        rel_path = file_path
    
    path_display = f"{rel_path}"
    
    separator = "=" * 63
    header = f"{separator}\n{path_display:^64}\n{separator}"
    
    return header


def generate_output_filename(base_name: str = "collection") -> str:
    """
    Generates an output filename with date and time.
    Format: collection_YY-MM-DD_HH-MM.txt
    """
    now = datetime.now()
    date_time_str = now.strftime("%y-%m-%d_%H-%M")
    filename = f"{base_name}_{date_time_str}.txt"
    return filename


def save_project_code(config: dict) -> None:
    """Main function for saving project code."""
    project_root = os.path.abspath(config.get('project_root', './'))
    
    output_file = config.get('output_file', None)
    if output_file is None or output_file == "":
        base_name = config.get('output_base_name', 'collection')
        output_file = generate_output_filename(base_name)
    
    extensions = config.get('file_extensions', ['.py'])
    exclude_folders = config.get('exclude_folders', [])
    additional_patterns = config.get('additional_ignore_patterns', [])
    
    if not os.path.exists(project_root):
        print(f"Error: Project folder '{project_root}' does not exist.")
        exit(1)
    
    ignore_patterns = parse_gitignore(project_root)
    
    ignore_patterns.extend(exclude_folders)
    ignore_patterns.extend(additional_patterns)
    
    ignore_patterns.append('collection_*.txt')
    ignore_patterns.append(output_file)
    
    files = collect_files(project_root, extensions, ignore_patterns)
    
    if not files:
        print("No files found with specified extensions.")
        return
    
    try:
        with open(output_file, 'w', encoding='utf-8') as out:
            now = datetime.now()
            out.write(f"Project: {project_root}\n")
            out.write(f"Generated: {now.strftime('%Y-%m-%d %H:%M')}\n")
            out.write(f"Total files: {len(files)}\n\n")
            
            for i, file_path in enumerate(files, 1):
                header = format_header(file_path, project_root)
                out.write(header + "\n\n")
                
                content = read_file_content(file_path)
                out.write(content)
                out.write("\n\n")
        
        print(f"Project code saved to: {output_file}")
        
    except Exception as e:
        print(f"Error saving file: {e}")
        exit(1)

if __name__ == "__main__":
    config = load_config()
    save_project_code(config)
