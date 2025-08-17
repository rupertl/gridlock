"""Utilities for gridlock."""


import glob
import json
import os
import subprocess
import sys
import yaml


CONFIG_FILE = "config.yaml"
PROMPT_FILE = "prompt.md"
PRESCAN_FILE = "prescan.results"

ATTRIB_DIR = "attributes"
CROPPED_DIR = "cropped"
GRIDS_DIR = "grids"
PAGES_DIR = "pages"
SPLIT_DIR = "split"
TEMPLATES_DIR = "templates"
TEXT_DIR = "text"
MERGED_DIR = "merged"


def read_yaml(file_path):
    """Reads a YAML file and returns its content as a dictionary."""
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            yaml_data = yaml.safe_load(file)
            return yaml_data
        except FileNotFoundError:
            print(f"Error: File not found: '{file_path}'")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"Error reading YAML file {file_path}: {e}")
            sys.exit(1)


def read_config():
    """Read the main config file."""
    return read_yaml(CONFIG_FILE)


def get_config(config, section, key):
    """Get a value from the config map based on section and key, or exit."""
    if section not in config:
        print(f"Section {section} not in config file")
    section = config[section]
    if key not in section:
        print(f"Key {section}.{key} not in config file")
        sys.exit(1)
    return section[key]


def get_num_pages(config):
    """Get the number of pages expected to be produced from the config."""
    if "split" in config and "num_pages" in config["split"]:
        num = config["split"]["num_pages"]
    else:
        last = get_config(config, "split", "last_page")
        first = get_config(config, "split", "first_page")
        num = 1 + last - first
    if num < 1:
        print("Number of pages must be > 0")
        sys.exit(1)
    return num


def read_json(json_file):
    """Read the config file and return a dict of values."""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        print(f"Error: File not found at '{json_file}'")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{json_file}'")
        sys.exit(1)


def run_command(command, silent_if_fail=False):
    """Run a shell command and check output."""
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        if silent_if_fail:
            return
        print(f"Command '{command}' failed with exit code: {e.returncode}")
    except FileNotFoundError:
        print(f"Command '{command.split()[0]}' not found",
              f"while running '{command}'")


# pylint: disable=too-many-arguments,too-many-positional-arguments
def single_task(ensure_dirs, input_file,
                output_file, action,
                command, force):
    """Run a shell command on a single file."""
    for ensure_dir in ensure_dirs:
        mkdir(ensure_dir)
    if force:
        delete_files(output_file)
    if count_files(output_file) == 1:
        print("Skipping")
        return
    run_command(command)
    if count_files(output_file) != 1:
        print(f"Error doing {action} for {input_file} to {output_file}")
        sys.exit(1)


def get_file_key(file_path):
    """Find the page key from a file name, eg for a/b/XXX-123.txt it
    would be 123."""
    filename = os.path.basename(file_path)
    filename_no_ext = os.path.splitext(filename)[0]
    return filename_no_ext


# pylint: disable=too-many-arguments,too-many-positional-arguments
def parallel_task(prefix, input_dir, input_ext, output_dir, output_ext,
                  action, command, force):
    """Run several shell commands in parallel."""
    for ensure_dir in [input_dir, output_dir]:
        mkdir(ensure_dir)
    input_files = glob.glob(f"{input_dir}/{prefix}-*.{input_ext}")
    if len(input_files) == 0:
        print("No input files to process.")
        sys.exit(1)
    output_files = []
    keys = ""
    for input_file in input_files:
        key = get_file_key(input_file)
        output_file = f"{output_dir}/{key}.{output_ext}"
        if force:
            delete_files(output_file)
        if force or count_files(output_file) == 0:
            output_files.append(output_file)
            keys += key + " "
    if len(output_files) == 0:
        print("Skipping as all files processed")
        return
    print(f"Running {action} for {len(output_files)} files")
    # Note: command line length limits may cause problems
    # if more than 100,000 files
    run_command(f"parallel --bar {command} {{}} ::: {keys}",
                silent_if_fail=True)
    done = sum((count_files(item) for item in output_files))
    if done < len(output_files):
        print(f"Failed {action} for {len(output_files) - done} files""")
        sys.exit(1)


def count_files(pattern):
    """Count the number of files matching pattern."""
    return len(glob.glob(pattern))


def delete_files(pattern):
    """Delete files matching pattern."""
    for file_path in glob.glob(pattern):
        os.remove(file_path)


def mkdir(path):
    """Make the diirectory at path, if it does not already exist."""
    try:
        os.mkdir(path)
    except FileExistsError:
        # Expected, continue
        return
    except FileNotFoundError:
        print(f"Could not create directory {path}")
        sys.exit(1)


def file_not_empty(path):
    """Return True if the file indicated by path exists and is not empty."""
    return os.path.exists(path) and os.path.getsize(path) > 0


def get_attrs_file_name(prefix):
    """Return the name of the attributes json file."""
    return prefix + ".json"


def get_page_attrs(page_key):
    """Return the page attributes dict by reading the attributes
    stored in the JSON file."""
    prefix = page_key.split('-')[0]
    all_pages = read_json(get_attrs_file_name(prefix))
    return all_pages[page_key]
