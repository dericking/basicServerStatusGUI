# Simple Server Status GUI Panel

Provides a simple Python-based graphical user interface (GUI) to monitor the status of a server and manage basic backups (assumed to be on external device). The GUI is built using `ttkbootstrap` and `tkinter`.

## Features

- Monitor server status in simple manner using ping or HTTP response code (for when ping isn't allowed).
  - GUI displays current status, and
  - Displays most recent time server was reachable.
- Allows for a manual backup using rsync (Linux or Mac) and is useful for backups in-between cron jobs. 
- View backup logs which open in default system editor
  - Linux via 'xdg-open', and
  - Mac via 'open'.

## Requirements

- Python 3.x
- `ttkbootstrap`
- `requests`

## Installation

Install the required Python packages:

### Ubuntu Linux
```
sudo apt update
sudo apt install python3 python3-pip
pip3 install ttkbootstrap requests
```
### MacOS
```
brew install python3
pip3 install ttkbootstrap requests
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
| `LBLFRMPAD`     | Padding at the bottom of every LabelFrame        | `15`                               |
| `CHECK_TYPE`    | Monitoring type: "RESPONSE" or "PING"            | `RESPONSE`                         |
| `SERVER_URL`    | URL of the server (will strip for PING)          | `https://your.server.url`          |
| `SHORT_NAME`    | Server short name (for labels)                   | `ServerShortName`                  |
| `REFRESHINT`    | Status refresh interval in seconds               | `600`                              |
| `BACKUPUUID`    | UUID of the backup drive                         | `Backup Drive UUID` |
| `MOUNTPOINT`    | Mount point of the backup drive                  | `/your/mount/point`                   |
| `BACKUP_DIR`    | Directory for the backup at mount point          | `directoryToSaveBackups/`           |
| `BACKUP_LOG`    | Directory for the backup logs at mount point     | `directoryToSaveLogs/`              |
| `BACKUPLINK`    | Symbolic link to the backup directory on remote server, ideally plaed in home directory | `symLinkToBackup`                  |
| `REMOTEUSER`    | Remote user for SSH connection                   | `remoteHostUser`                   |
| `REMOTEHOST`    | Remote host for SSH connection                   | `your.remote.host`                 |
| `SSHKEYAUTH`    | SSH key location for authentication              | `~/.ssh/yourSSHkey`                |
| `LOG_PREFIX`    | Prefix for backup log filenames                  | `backup-changes`                   |

## Usage

Run the application using the following command:

```sh
python basicServerStatusGUI.py &
```

I've allowed to run in background for months on end. 
