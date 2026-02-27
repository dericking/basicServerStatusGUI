# Simple Server Status GUI Panel

This project provides a simple graphical user interface (GUI) to monitor the status of a server and manage basic backups (assumed to be on external device). The GUI is built using `ttkbootstrap` and `tkinter`. Makes use of rsync. 

## Features

- Monitor server status using ping or HTTP response code (for when ping isn't allowed).
- Display the most recent online status time and a indicator of current status.
- Display the remaining drive space on backup drive.
- Allows for a manual backup.
- View backup logs.

## Requirements

- Python 3.x
- Dependencies are listed in `requirements.txt`: `ttkbootstrap`, `requests`, and `Pillow` (used by ttkbootstrap for the GUI).

## Installation

### Install script (Bash)

From the project root, run the provided Bash install script to check for Python 3, install dependencies from `requirements.txt`, and create an executable wrapper named `basicServerStatusGUI`:

```bash
./install.sh
```

After installation, run the application with:

```bash
./basicServerStatusGUI
```

To run it from anywhere, add the project directory to your `PATH`, or create a symlink (the script will suggest one if `~/.local/bin` exists):

```bash
ln -sf "$(pwd)/basicServerStatusGUI" ~/.local/bin/basicServerStatusGUI
```

### Manual installation

Install the required Python packages with pip (or use `pip install -r requirements.txt`):

#### Ubuntu Linux
```
sudo apt update
sudo apt install python3 python3-pip
pip3 install -r requirements.txt
```

You may also need tkinter:

```
sudo apt install python3-tk
```

#### macOS
```
brew update
brew install python3
pip3 install -r requirements.txt
```

You may need XQuartz if your Python build is configured for X11:

```
brew install --cask xquartz
```

## Configuration

Copy the config.py.template file to config.py and edit accordingly.



| Parameter       | Description                                      | Default Value                      |
|-----------------|--------------------------------------------------|------------------------------------|
| `GUI_THEME`     | Default TTKBootstrap theme for the GUI           | `superhero`                        |
| `FONT_TYPE`     | Default font type                                | `Helvetica`                        |
| `FONT_SIZE`     | Default font size                                | `12`                               |
| `HEAD_SIZE`     | Default header font size                         | `16`                               |
| `CIRC_SIZE`     | Status circle size                               | `30`                               |
| `WINDOWGEO`     | Window size, width important                     | `400x850`                          |
| `LBLFRMPAD`     | Padding at the bottom of every LabelFrame        | `10`                               |
| `CHECK_TYPE`    | Monitoring type: "RESPONSE" or "PING"            | `RESPONSE`                         |
| `SERVER_URL`    | URL of the server (will strip for PING)          | `https://your.server.url`          |
| `SHORT_NAME`    | Server short name (for labels)                   | `ServerShortName`                  |
| `REFRESHINT`    | Status refresh interval in seconds               | `600`                              |
| `BACKUPUUID`    | UUID of the backup drive                         | `Backup Drive UUID` |
| `MOUNTPOINT`    | Mount point of the backup drive                  | `/your/mount/point`                |
| `BACKUP_DIR`    | Directory for the backup at mount point          | `directoryToSaveBackups/`          |
| `BACKUP_LOG`    | Directory for the backup logs at mount point     | `directoryToSaveLogs/`             |
| `BACKUPLINK`    | Symbolic link to the backup directory on remote server, ideally placed in home directory | `symLinkToBackup`                  |
| `REMOTEUSER`    | Remote user for SSH connection                   | `remoteHostUser`                   |
| `REMOTEHOST`    | Remote host for SSH connection                   | `your.remote.host`                 |
| `SSHKEYAUTH`    | SSH key location for authentication              | `~/.ssh/yourSSHkey`                |
| `LOG_PREFIX`    | Prefix for backup log filenames                  | `backup-changes`                   |

## Usage

Run the application:

- **If you used the install script:**  
  `./basicServerStatusGUI` (or `basicServerStatusGUI` if it is on your `PATH`).

- **Otherwise:**  
  `python3 basicServerStatusGUI.py`  
  (run from the project directory so `config.py` is found.)