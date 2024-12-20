# SyncHero

SyncHero is a Python-based tool that automates copying files between directories. It is originally made to backup my game save files to an external disk.

## Installation

Since SyncHero isn't submitted to the PyPI library, you can install it directly from GitHub:

```bash
pip install git+https://github.com/Yunus-38/SyncHero.git
```

## Usage

1. **Create a Configuration File**
   Run the following command to generate a default `.syncHero.json` in your home directory:
   ```bash
   synchero createConfig
   ```

2. **Edit the Configuration File**
   Open the generated `.syncHero.json` and define your profiles. Each profile contains:
   - A `name`
   - `sourceDisk` and `destinationDisk`
   - `directoryPairs` specifying source and destination directories

   Here's the default `.syncHero.json`:

   ```json
   {
     "constants": {
       "": ""
     },
     "encryptionKeys": [
       {
         "name": "",
         "value": ""
       }
     ],
     "profiles": [
       {
         "name": "",
         "sourceDisk": "C",
         "destinationDisk": "I",
         "directoryPairs": [
           {
             "name": "",
             "source": "",
             "destination": ""
           }
         ]
       }
     ]
   }
   ```

3. **Example Profile**
   Below is an example profile with two directory pairs:

   ```json
   {
     "profiles": [
       {
         "name": "ProjectBackup",
         "sourceDisk": "C",
         "destinationDisk": "D",
         "directoryPairs": [
           {
             "name": "Documents",
             "source": "Users/YourName/Documents",
             "destination": "Backups/Documents"
           },
           {
             "name": "Pictures",
             "source": "<user>/Pictures",
             "destination": "Backups/Pictures"
           }
         ]
       }
     ]
   }
   ```
   The `<user>` wildcard is replaced in the script with your user's home directory.

4. **Run SyncHero**
   To copy files from the "source" to "destination" on each directory pair of a profile, run:
   ```bash
   synchero backup <ProfileName>
   ```
   To copy the opposite way, run:
   ```bash
   synchero restore <ProfileName>
   ```

   Flags: 
   `-f` or `--force`
   Overrides files if same file exists in target directory.

## Planned Features

- **Encryption and Decryption**
  - Encrypt backups and decrypt during restores for added security.

- **Dynamic Directory Parts**
  - Define reusable constants for parts of directory paths, simplifying configuration in `directoryPairs`. This is similar to the <user> wildcard.
