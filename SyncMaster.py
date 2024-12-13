import argparse
import json
from pathlib import Path
import shutil
import os

def main():
    
    args = parse_commands()

    if args.command == "createConfig":
        create_config()
        return

    _force = args.force
    
    file_path = Path.home() / ".syncMaster.json"
    
    try:
        with file_path.open("r", encoding="utf-8") as file:
            config = json.load(file)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None
    

    config_found = False
    for profile in config["profiles"]:
        if profile["name"] == args.profile:
            if args.command == "backup":
                backup(profile, _force, args.pair)
                config_found = True
            elif args.command == "restore":
                restore(profile, _force, args.pair)
                config_found = True
            break

    if not config_found:
        print(f"Profile '{args.profile}' not found. Available profiles are:")
        for profile in config["profiles"]:
            print(f"  - {profile['name']}")


def parse_commands():
    # Create the main parser
    parser = argparse.ArgumentParser(description="SyncMaster: A tool for quick and easy file backups.")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Sync files to the destination.")
    backup_parser.add_argument("profile", help="The profile name to use.")
    backup_parser.add_argument("-f", "--force", action="store_true", help="Overwrite existing files without prompt.")
    backup_parser.add_argument("-p", "--pair", type=str, help="Specify a specific directory pair to sync.")

    # Restore command
    restore_parser = subparsers.add_parser("restore", help="Recover files from a backup.")
    restore_parser.add_argument("profile", help="The profile name to use.")
    restore_parser.add_argument("-f", "--force", action="store_true", help="Overwrite existing files without prompt.")
    restore_parser.add_argument("-p", "--pair", type=str, help="Specify a specific directory pair to sync.")

    # CreateConfig command
    subparsers.add_parser("createConfig", help="Create the default configuration file.")

    # Parse the arguments
    return parser.parse_args()


def backup(profile, overwrite = False, pair = None):
    
    active_pair = None

    if pair is not None:
        for directory_pair in profile["directoryPairs"]:
            if directory_pair["name"] == pair:
                active_pair = pair
                break
        
        if active_pair is None:
            print(f"Directory Pair '{pair}' not found in profile. Available directory pairs are:")
            for directory_pair in profile["directoryPairs"]:
                print(f"  - {directory_pair['name']}")
            return

    
    source_disk = profile["sourceDisk"]
    destination_disk = profile["destinationDisk"]
    stats = {
        "directory_pair_name": "null",
        "total_files": 0,
        "copied_files": 0,
        "overridden_files": 0,
        "new_files": 0,
        "skipped_files": 0,
    }
    for directory_pair in profile["directoryPairs"]:
        if active_pair is not None and directory_pair["name"] != active_pair:
            continue
        source_path = get_full_path(source_disk, directory_pair["source"])
        destination_path = get_full_path(destination_disk, directory_pair["destination"])
        if source_path.exists():
            stats = copy_to_existing_directory(source_path, destination_path, overwrite)
            stats["directory_pair_name"] = directory_pair["name"]
            print_directory_pair_statistics(stats)
        else:
            print(f"Source directory {source_path} does not exist.")
    return stats

def restore(profile, overwrite = False, pair = None):
    
    active_pair = None

    if pair is not None:
        for directory_pair in profile["directoryPairs"]:
            if directory_pair["name"] == pair:
                active_pair = pair
                break
        
        if active_pair is None:
            print(f"Directory Pair '{pair}' not found in profile. Available directory pairs are:")
            for directory_pair in profile["directoryPairs"]:
                print(f"  - {directory_pair['name']}")
            return

    
    source_disk = profile["sourceDisk"]
    destination_disk = profile["destinationDisk"]
    stats = {}
    for directory_pair in profile["directoryPairs"]:
        if active_pair is not None and directory_pair["name"] != active_pair:
            continue
        source_path = get_full_path(source_disk, directory_pair["source"])
        destination_path = get_full_path(destination_disk, directory_pair["destination"])
        if destination_path.exists():
            stats = copy_to_existing_directory(destination_path, source_path, overwrite)
            stats["directory_pair_name"] = directory_pair["name"]
            print_directory_pair_statistics(stats)
        else:
            print(f"Source directory {source_path} does not exist.")
    return stats


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


def copy_to_existing_directory(source_dir, destination_dir, overwrite=False):
    source_dir = Path(source_dir)
    destination_dir = Path(destination_dir)

    if not source_dir.is_dir():
        raise ValueError(f"Source directory {source_dir} does not exist.")

    if not destination_dir.is_dir():
        destination_dir.mkdir(parents=True, exist_ok=True)

    # Initialize stats for this function call
    stats = {
        "source_dir": source_dir,
        "destination_dir": destination_dir,
        "total_files": 0,
        "copied_files": 0,
        "overridden_files": 0,
        "new_files": 0,
        "skipped_files": 0,
    }

    # Iterate over all files and subdirectories in the source directory
    for item in source_dir.iterdir():
        destination_path = destination_dir / item.name

        if item.is_dir():
            # Recursively copy subdirectories and merge stats
            sub_stats = copy_to_existing_directory(item, destination_path, overwrite)
            
            stats["total_files"] += sub_stats["total_files"]
            stats["copied_files"] += sub_stats["copied_files"]
            stats["overridden_files"] += sub_stats["overridden_files"]
            stats["new_files"] += sub_stats["new_files"]
            stats["skipped_files"] += sub_stats["skipped_files"]


        elif item.is_file():
            stats["total_files"] += 1
            destination_exists = file_exists(destination_path)

            if overwrite and destination_exists:
                # Overwrite files
                shutil.copy2(item, destination_path)
                stats["overridden_files"] += 1
                stats["copied_files"] += 1
                print(f"📄 Overridden: {item.name} -> {destination_path}")
            elif not overwrite and destination_exists:
                # Skip files that already exist
                stats["skipped_files"] += 1
                print(f"⏭️ Skipped: {item.name}")
            elif not destination_exists:
                # Copy new files
                shutil.copy2(item, destination_path)
                stats["new_files"] += 1
                stats["copied_files"] += 1
                print(f"✅ Copied: {item.name} -> {destination_path}")

    return stats

def print_directory_pair_statistics(stats):
    """
    Print the statistics for a completed sync operation.
    """
    print("\n" + "=" * 40)
    print(f"✨ Sync Complete for Directory Pair: {stats['directory_pair_name']}")
    print(f"📂 Source Directory: {stats['source_dir']}")
    print(f"📂 Destination Directory: {stats['destination_dir']}")
    print("=" * 40)
    print(f"📂 Total files processed: {stats['total_files']}")
    print(f"✅ Copied files: {stats['copied_files']}")
    print(f"🆕 New files copied: {stats['new_files']}")
    print(f"♻️ Overwritten files: {stats['overridden_files']}")
    print(f"⏭️ Skipped files: {stats['skipped_files']}")
    print("=" * 40 + "\n")


def file_exists(file_path):
    """
    Check if a file exists at the given path.

    :param file_path: Path to the file (str or Path object)
    :return: True if the file exists, False otherwise
    """
    path = Path(file_path)
    return path.is_file()

def create_config():
    print("Creating config file...")
    return

    # Create the config file
    file_path = Path(__file__).resolve().parent / "default-config.json"
    with file_path.open("r", encoding="utf-8") as file:
            default_config = json.load(file)
    with (Path.home() / ".syncMaster.json").open(".syncMaster.json", "w") as config_file:
        json.dump(default_config, config_file, indent=4)

# Boilerplate to run the program
if __name__ == "__main__":
    main()


