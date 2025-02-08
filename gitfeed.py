#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
import tempfile

def get_repo_name(url):
    """
    Extracts the repository name from the given URL.
    Example: https://github.com/user/repo.git -> repo
    """
    url = url.rstrip("/")
    repo_name = url.split("/")[-1]
    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]
    return repo_name

def build_tree_lines(start_path, prefix=""):
    """
    Returns a list of strings representing the directory tree starting at start_path.
    """
    lines = []
    items = sorted(os.listdir(start_path))
    for index, item in enumerate(items):
        path = os.path.join(start_path, item)
        connector = "└── " if index == len(items) - 1 else "├── "
        if os.path.isdir(path):
            line = prefix + connector + item + "/"
            lines.append(line)
            # Choose the appropriate prefix for children based on the connector
            if index == len(items) - 1:
                extension_prefix = prefix + "    "
            else:
                extension_prefix = prefix + "│   "
            lines.extend(build_tree_lines(path, extension_prefix))
        else:
            lines.append(prefix + connector + item)
    return lines

def generate_directory_tree(root_dir, repo_name):
    """
    Generates a list of strings representing the directory structure in a tree-like format.
    """
    lines = ["Directory structure:"]
    # Start with the root directory line using the repo name
    lines.append(f"└── {repo_name}/")
    # Append the tree lines for the content of the repository,
    # indenting each line by 4 spaces.
    lines.extend(build_tree_lines(root_dir, prefix="    "))
    return lines

def main():
    parser = argparse.ArgumentParser(
        description="Script to clone a GitHub repository, generate its directory structure, "
                    "and concatenate the content of all files into a single global file."
    )
    parser.add_argument("repo_url", help="URL of the GitHub repository (can be private).")
    parser.add_argument("--dir_structure_file", help="Name of the output file for the directory structure.",
                        default="directory_structure.txt")
    parser.add_argument("--output_name", help="Name of the global output file with the content of all files.",
                        default="contents.txt")
    parser.add_argument("--exclude-ext", nargs="*", default=[], 
                        help="File extension(s) to exclude from contents.txt. "
                             "Example: --exclude-ext .log .tmp")
    parser.add_argument("--max-file-size", type=float, default=None,
                        help="Maximum file size in MB to include in contents.txt. "
                             "Files larger than this limit will be skipped.")

    args = parser.parse_args()
    
    # Normalize the list of excluded extensions: ensure that each extension starts with '.'
    excluded_extensions = []
    for ext in args.exclude_ext:
        if not ext.startswith("."):
            excluded_extensions.append("." + ext.lower())
        else:
            excluded_extensions.append(ext.lower())
    
    # Extract repository name and create an output directory with that name
    repo_name = get_repo_name(args.repo_url)
    output_dir = os.path.join(os.getcwd(), repo_name)
    os.makedirs(output_dir, exist_ok=True)
    
    # Define output file paths inside the output directory
    dir_structure_file = os.path.join(output_dir, args.dir_structure_file)
    global_file = os.path.join(output_dir, args.output_name)
    
    # Create a temporary directory to clone the repository
    with tempfile.TemporaryDirectory() as tmpdirname:
        print("\x1b[6;33;40m" + f"[i] Cloning repository into temporary directory: {tmpdirname}"+ '\x1b[0m')
        try:
            subprocess.check_call(["git", "clone", args.repo_url, tmpdirname, "--quiet"])
        except subprocess.CalledProcessError as e:
            print("[!] Error cloning repository:", e)
            sys.exit(1)
        
        # Generate and save the directory structure in a tree-like format to a text file
        tree_lines = generate_directory_tree(tmpdirname, repo_name)
        with open(dir_structure_file, "w", encoding="utf-8") as f:
            for line in tree_lines:
                f.write(line + "\n")
        print("\x1b[6;30;42m" + f"[i] Directory structure saved in: {dir_structure_file}"+ '\x1b[0m')

        # Walk through all repository files and concatenate their contents into a global file
        with open(global_file, "w", encoding="utf-8") as global_out:
            for current_root, dirs, files in os.walk(tmpdirname):
                # Exclude the .git directory
                if ".git" in dirs:
                    dirs.remove(".git")
                for file in files:
                    filepath = os.path.join(current_root, file)
                    relative_path = os.path.relpath(filepath, tmpdirname)

                    # Check the file extension
                    file_ext = os.path.splitext(file)[1].lower()
                    if excluded_extensions and file_ext in excluded_extensions:
                        print("\x1b[6;33;40m" +f"[!] Skipping file {relative_path} due to excluded extension ({file_ext})."+ '\x1b[0m')
                        continue

                    # Check the maximum file size if specified
                    if args.max_file_size is not None:
                        try:
                            file_size = os.path.getsize(filepath)
                        except OSError as e:
                            print(f"[!] Could not get size of {relative_path}: {e}")
                            continue
                        # Convert MB to bytes
                        max_size_bytes = args.max_file_size * 1024 * 1024
                        if file_size > max_size_bytes:
                            print("\x1b[6;33;40m" + f"[!] Skipping file {relative_path} as it exceeds the maximum allowed size ({file_size} bytes)." + '\x1b[0m')
                            continue

                    global_out.write("================================================\n")
                    global_out.write(f"File: {relative_path}\n")
                    global_out.write("================================================\n")
                    try:
                        with open(filepath, "r", encoding="utf-8") as file_in:
                            content = file_in.read()
                            global_out.write(content)
                    except Exception as e:
                        global_out.write(f"[!] Error reading file: {e}\n")
                    global_out.write("\n\n")
        print("\x1b[6;30;42m" + f"[i] Global file content saved in: {global_file}" + '\x1b[0m')

if __name__ == "__main__":
    main()
