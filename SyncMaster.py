import argparse
import json
from pathlib import Path
import shutil
import os

def main():
    # Step 1: Create the parser
    parser = argparse.ArgumentParser(
        description="SyncMaster: A tool for quick and easy file backups."
    )

    # Step 2: Add arguments
    # First positional argument: the command
    parser.add_argument(
        "command", 
        choices=["backup", "restore"],  # Limit the allowed commands
        help="Command to execute: 'backup' to sync files, 'restore' to recover."
    )

    # Second positional argument: the profile name
    parser.add_argument(
        "profile",  # Name of the second positional argument
        help="The profile name to use."
    )

    # Step 3: Parse arguments
    args = parser.parse_args()

    file_path = Path(__file__).parent / "profiles.json"
    
    try:
        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None
    
    
    success = False
    for profile in data:
        if profile["name"] == args.profile:
            if args.command == "backup":
                backup(profile)
                success = True
            elif args.command == "restore":
                restore(profile)
                success = True
            break

    if not success:
        print(f"Profile {args.profile} not found.")
        return None


def backup(profile):
    source_disk = profile["sourceDisk"]
    destination_disk = profile["destinationDisk"]
    for directory_pair in profile["directoryPairs"]:
        source_path = get_full_path(source_disk, directory_pair["source"])
        destination_path = get_full_path(destination_disk, directory_pair["destination"])
        if source_path.exists():
            copy_to_existing_directory(source_path, destination_path)
        else:
            print(f"Source directory {source_path} does not exist.")
            return None
    print("Backup completed.")

def restore(profile):
    source_disk = profile["sourceDisk"]
    destination_disk = profile["destinationDisk"]
    for directory_pair in profile["directoryPairs"]:
        source_path = get_full_path(source_disk, directory_pair["source"])
        destination_path = get_full_path(destination_disk, directory_pair["destination"])
        if source_path.exists():
            copy_to_existing_directory(destination_path, source_path)
        else:
            print(f"Source directory {source_path} does not exist.")
    print("Restore completed.")


def get_full_path(disk, relative_path):
    """
    Combine a disk and relative path in an OS-agnostic way.
    """
    if os.name == 'nt':  # Windows
        # Append `:` for Windows if disk is a drive letter
        disk = disk + ":" if len(disk) == 1 and disk.isalpha() else disk

        if "<user>" in relative_path:
            relative_path = resolve_user_wildcard(relative_path)
            return Path(relative_path)


    # Combine the disk and relative path
    return Path(disk) / relative_path

def resolve_user_wildcard(path_str):
    """
    Replace a placeholder with the current user's home directory.
    """
    return path_str.replace("<user>", str(Path.home()))


def copy_to_existing_directory(source_dir, destination_dir):
    source_dir = Path(source_dir)
    destination_dir = Path(destination_dir)

    if not source_dir.is_dir():
        raise ValueError(f"Source directory {source_dir} does not exist.")

    if not destination_dir.is_dir():
        destination_dir.mkdir(parents=True, exist_ok=True)

    # Iterate over all files and subdirectories in the source directory
    for item in source_dir.iterdir():
        destination_path = destination_dir / item.name

        if item.is_dir():
            # Recursively copy subdirectories
            copy_to_existing_directory(item, destination_path)
        elif item.is_file():
            # Copy files (overwrite if they exist)
            shutil.copy2(item, destination_path)
            print(f"Copied file: {item} -> {destination_path}")


# Boilerplate to run the program
if __name__ == "__main__":
    main()


