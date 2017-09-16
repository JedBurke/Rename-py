import argparse
from glob import glob
import io
import json
import os
from os import path
from os.path import join
from pathlib import Path
import re
import sys

VERSION = "0.2.0"
PATH_SEPARATOR = ";"

# Prints certain values which the general user wouldn't need.
debug = False

# If "True", dictates that the rename action is not taken.
dry_run = False

# Profiles act as a convenient way to repetitively replace text. This 
# variable dictates which profile is to be used.
profile = None

regex_pattern = ""
regex_replace = ""
file_types = ["*"]

parser = argparse.ArgumentParser(description="Rename files")
parser.add_argument("args")
parser.add_argument("-n", "--dry-run", action="store_true")
parser.add_argument("--version", action="store_true")
parser.add_argument("--debug", action="store_true")
parser.add_argument("-m", "--match-pattern", default=None)
parser.add_argument("-r", "--replace-pattern", default=None)
parser.add_argument("-p", "--profile", default=None)

args = vars(parser.parse_args())

if args["debug"]:
  debug = True

if debug:
  print(args["args"])

if args["dry_run"]:
  dry_run = True

  if debug:
    print(f"Dry Run: {dry_run}")

if args["version"]:
  print(f"Pyren version: {VERSION}")

if args["match_pattern"] is not None:
  regex_pattern = args["match_pattern"]

  if debug:
    print(f"Match Pattern: {regex_pattern}")

if args["replace_pattern"] is not None:
  regex_replace = args["replace_pattern"]
  
  if debug:
    print(f"Replace Pattern: {regex_replace}")

if args["profile"] is not None:
  script_path = path.join(sys.path[0], "rename-profiles.json")

  with open(script_path, "r") as profile_content_file:
    profile_content = profile_content_file.read()

  profiles = json.loads(profile_content)
  profile_str = args["profile"]

  if not profile_str in profiles:
    print(f"Profile \"{profile_str}\" not found")
    print("Aborting.")
    exit()

  profile = profiles[profile_str]
  regex_pattern = profile["match"]
  regex_replace = profile["replace"]
  file_types = profile["ext"]

  if debug:
    print(f"Name: \"{profile_str}\"")
    print(f"Match: \"{regex_pattern}\"")
    print(f"Replace: \"{regex_replace}\"")
    print(f"Available extensions: \"{file_types}\"")

for directory in args["args"].split(PATH_SEPARATOR):
  print(f"Entering \"{directory}\".")

  p = Path(directory)

  if not p.is_dir():
    print("Skipping, not a directory.")
    continue

  files = []
  for ext in file_types:
    files.extend(glob(join(directory, ext)))

  for file in files:
    file_name = Path(file).name

    new_name = re.sub(regex_pattern, regex_replace, file_name)
    new_path = join(directory, new_name)

    if debug:
      print(f"{file_name} -> {new_name}")

    # Don't perform the rename if it's a dry run.
    if not dry_run:
      if not os.path.exists(new_path):
        os.rename(file, new_path)        
      else:
        print(f"Skipping, a file with the name of \"{new_name}\" already exists.")