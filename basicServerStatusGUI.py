from tkinter import messagebox, Listbox, Scrollbar, VERTICAL, RIGHT, Y, END, SINGLE
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import shutil
import requests
import threading
import time
import os
import subprocess
import datetime

# Import configuration file
import config  

class MonitorGUIApp:
    def __init__(self, master):
        self.master = master
        self.master.title(f"{config.SHORT_NAME}")
        self.master.geometry(f"{self.get_window_geometry()}+{self.get_screen_width()}+0")

        # Load settings from config.py
        self.server_url = config.SERVER_URL
        self.refresh_interval = config.REFRESHINT
        # self.theme = config.GUI_THEME   # Unused variable removed

        # Initialize backup logs
        self.backup_logs = self.get_backup_logs()

        style = ttk.Style()
        style.theme_use(config.GUI_THEME)

        #################################################################
        # Frame for Theme Selection
        theme_frame = ttk.Frame(master)
        theme_frame.pack(pady=10, padx=10, fill=X)
        # Select theme label for those who want to be different
        self.theme_label = ttk.Label(theme_frame, text="Theme:", font=(config.FONT_TYPE, config.FONT_SIZE, "bold"))
        self.theme_label.pack(side=LEFT, padx=5)
        # Default theme
        self.theme_var = ttk.StringVar(value=config.GUI_THEME)
        self.theme_dropdown = ttk.Combobox(
            theme_frame, values=style.theme_names(), textvariable=self.theme_var, state="readonly"
        )
        self.theme_dropdown.pack(side=LEFT, fill=X, expand=True)
        self.theme_dropdown.bind("<<ComboboxSelected>>", self.change_theme)

        #################################################################
        # Server Status Section
        server_status_frame = ttk.LabelFrame(master, text=f"{config.SHORT_NAME} Server Status",borderwidth=10, relief="groove", bootstyle=INFO)
        server_status_frame.pack(pady=config.LBLFRMPAD, padx=10, fill=X)

        # Frame for grid layout
        status_frame = ttk.Frame(server_status_frame)
        status_frame.pack(pady=0)
        # Labels for Status and Last Checked (Header Row)
        self.status_label = ttk.Label(status_frame, text="Status", font=(config.FONT_TYPE, config.FONT_SIZE, 'bold'))
        self.status_label.grid(row=0, column=0, padx=20, pady=5, sticky="n")
        # Last checked text label
        self.last_checked_label = ttk.Label(status_frame, text="Most Recently 'Online'", font=(config.FONT_TYPE, config.FONT_SIZE, 'bold'))
        self.last_checked_label.grid(row=0, column=1, padx=20, pady=5, sticky="n")
        # Status Indicator (Circle) and Time Label (Second Row)
        self.indicator = ttk.Label(status_frame, text="●", font=(config.FONT_TYPE, config.CIRC_SIZE), bootstyle="secondary")
        self.indicator.grid(row=1, column=0, padx=20, pady=5, sticky="ns")
        # Default time label before running
        self.time = ttk.Label(status_frame, text="0000/00/00 00:00:00", font=(config.FONT_TYPE, config.FONT_SIZE, 'bold'))
        self.time.grid(row=1, column=1, padx=20, pady=5, sticky="ns")
        # Frame for Buttons
        button_frame = ttk.Frame(server_status_frame)
        button_frame.pack(pady=5, fill=X, padx=20)
        # Start Button (Initial State: SECONDARY)
        self.startbutton = ttk.Button(
            button_frame, text="Start Monitoring", command=self.start_monitoring, bootstyle=SECONDARY
        )
        self.startbutton.pack(side=LEFT, expand=True, fill=X, padx=5, ipadx=2, ipady=5)
        # Stop Button (Initial State: SECONDARY)
        self.stopbutton = ttk.Button(
            button_frame, text="Paused...", command=self.stop_monitoring, bootstyle=SECONDARY
        )
        self.stopbutton.pack(side=LEFT, expand=True, fill=X, padx=5, ipadx=2, ipady=5)
        self.stop_event = threading.Event()

        #################################################################
        # Local Backup Space Section
        local_backup_frame = ttk.LabelFrame(master, text=f"{config.SHORT_NAME} Local Backup Drive Information", bootstyle=INFO)
        local_backup_frame.pack(pady=config.LBLFRMPAD, padx=10, fill=X)
        
        # Display BACKUPUUID and MOUNTPOINT
        backupuuid_label = ttk.Label(local_backup_frame, text=f"BACKUPUUID: {config.BACKUPUUID}", font=(config.FONT_TYPE, config.TINY_SIZE))
        backupuuid_label.pack(pady=5)
        
        mountpoint_label = ttk.Label(local_backup_frame, text=f"MOUNTPOINT: {config.MOUNTPOINT}", font=(config.FONT_TYPE, config.TINY_SIZE))
        mountpoint_label.pack(pady=0)
        
        # Check if backup drive can be properly mounted -- Need this check for people 
        # who aren't familiar with managing external drives
        can_mount = False
        can_see_backup = False
        can_see_log = False
        mounted = False
        # Check if the mount point exists and is accessible
        if os.path.exists(config.MOUNTPOINT):
            can_mount = True
        if os.path.exists(os.path.join(config.MOUNTPOINT, config.BACKUP_DIR)):
            can_see_backup = True
        if os.path.exists(os.path.join(config.MOUNTPOINT, config.BACKUP_LOG)):
            can_see_log = True
        if can_mount and can_see_backup and can_see_log:
            mounted = True
        else:
            can_mount, can_see_backup, can_see_log = mount_and_check_drive()
        # Check again after attempting to mount
        if can_mount and can_see_backup and can_see_log:
            mounted = True
        else:
            mounted = False

        if mounted:
            usage    = shutil.disk_usage(config.MOUNTPOINT)
            free_GB  = round(usage.free / (1024**3))
            total_GB = round(usage.total / (1024**3))
            free_pct = int((usage.free / usage.total) * 100)
            used_pct = 100 - free_pct

            if used_pct < 75:
                meter_color = "SUCCESS"
            elif used_pct < 90:
                meter_color = "WARNING"
            else:
                meter_color = "DANGER"
        else:
            meter_color = "DANGER"
            used_pct = 100

        # Create a container frame for the Meter and drive info
        meter_container = ttk.Frame(local_backup_frame)
        meter_container.pack(anchor="center", pady=10)
        
        horizontal_gap = 20

        # Meter
        space_meter = ttk.Meter(
            meter_container,
            amounttotal=100,
            amountused=used_pct,
            showtext=False,
            meterthickness=15,
            metersize=100,
            interactive=False,
            stripethickness=9,
            bootstyle=meter_color
        )
        space_meter.grid(row=0, column=0, padx=(0, horizontal_gap//2), pady=10)

        # Place the meter in the left side of the grid
        meter_percent_label = ttk.Label(
            meter_container,
            text=f"{used_pct}%\nused" if mounted else "ERROR",
            bootstyle=meter_color,
            font=(config.FONT_TYPE, config.FONT_SIZE, 'bold')
        )
        meter_percent_label.place(in_=space_meter, relx=0.5, rely=0.5, anchor="center")

        # Place spacer in the middle grid
        spacer = ttk.Frame(meter_container, width=horizontal_gap)
        spacer.grid(row=0, column=1)

        # Add drive information to the right side.
        drive_info_frame = ttk.Frame(meter_container)
        drive_info_frame.grid(row=0, column=2, padx=(horizontal_gap, 0), pady=10)

        if mounted:
            drive_header = ttk.Label(
                drive_info_frame,
                text="Drive Information",
                font=(config.FONT_TYPE, config.FONT_SIZE, "underline")
            )
            drive_header.pack(anchor="center", pady=5)
            total_label = ttk.Label(
                drive_info_frame,
                text=f"Total: {total_GB} GB",
                font=(config.FONT_TYPE, config.FONT_SIZE)
            )
            total_label.pack(anchor="center")
            used_label = ttk.Label(
                drive_info_frame,
                text=f"Used: {total_GB - free_GB} GB",
                font=(config.FONT_TYPE, config.FONT_SIZE)
            )
            used_label.pack(anchor="center")
            available_label = ttk.Label(
                drive_info_frame,
                text=f"Available: {free_GB} GB",
                font=(config.FONT_TYPE, config.FONT_SIZE)
            )
            available_label.pack(anchor="center")
        else:
            drive_header = ttk.Label(
                drive_info_frame,
                text="Drive Information",
                font=(config.FONT_TYPE, config.FONT_SIZE, "underline")
            )
            drive_header.pack(anchor="center", pady=5)
            if can_mount:
                mount_fail_label = ttk.Label(
                    drive_info_frame,
                    text="Mount Point: Found",
                    font=(config.FONT_TYPE, config.FONT_SIZE)
                )
            else: 
                mount_fail_label = ttk.Label(
                    drive_info_frame,
                    text="Mount Point: Not Found",
                    bootstyle="DANGER",
                    font=(config.FONT_TYPE, config.FONT_SIZE)
                )
            mount_fail_label.pack(anchor="center", pady=5)
            if can_see_backup:
                backup_fail_label = ttk.Label(
                    drive_info_frame,
                    text="Backup Dir: Found",
                    font=(config.FONT_TYPE, config.FONT_SIZE)
                )
            else: 
                backup_fail_label = ttk.Label(
                    drive_info_frame,
                    text="Backup Dir: Not Found",
                    bootstyle="DANGER",
                    font=(config.FONT_TYPE, config.FONT_SIZE)
                )
            backup_fail_label.pack(anchor="center", pady=5)
            if can_see_log:
                log_fail_label = ttk.Label(
                    drive_info_frame,
                    text="Log Dir: Found",
                    font=(config.FONT_TYPE, config.FONT_SIZE)
                )
            else: 
                log_fail_label = ttk.Label(
                    drive_info_frame,
                    text="Log Dir: Not Found",
                    bootstyle="DANGER",
                    font=(config.FONT_TYPE, config.FONT_SIZE)
                )
            log_fail_label.pack(anchor="center", pady=5)

        #################################################################
        # Backup Status Section
        backup_status_frame = ttk.LabelFrame(master, text=f"{config.SHORT_NAME} Backup Status", bootstyle=INFO)
        backup_status_frame.pack(pady=config.LBLFRMPAD, padx=10, fill=X)

        # Get backup logs
        self.backup_logs = self.get_backup_logs()
        # Latest Backup Label
        self.latest_backup_label = ttk.Label(backup_status_frame, text="Last Backup: Not Found", font=(config.FONT_TYPE, config.FONT_SIZE, 'bold'))
        self.latest_backup_label.pack(pady=10)
        self.update_latest_backup_date()
        # Frame for Backup Button
        backup_button_frame = ttk.Frame(backup_status_frame)
        backup_button_frame.pack(pady=(0,15))
        # Backup Button
        self.backup_button = ttk.Button(
            backup_button_frame, text="Run Backup Now", command=self.run_backup, bootstyle=PRIMARY
        )
        self.backup_button.pack()

        #################################################################
        # Backup List Section
        backup_list_frame = ttk.LabelFrame(master, text=f"{config.SHORT_NAME} Backup List", bootstyle=INFO)
        backup_list_frame.pack(pady=config.LBLFRMPAD, padx=10, fill=X)

        # Listbox for backup logs
        logfile_frame = ttk.Frame(backup_list_frame)
        logfile_frame.pack(pady=10, padx=10, fill=X)
        self.log_listbox = Listbox(logfile_frame, height=5, font=(config.FONT_TYPE, config.FONT_SIZE), selectmode=SINGLE)
        self.log_listbox.pack(side=LEFT, fill=X, expand=True, padx=5)
        for log in self.backup_logs:
            self.log_listbox.insert(END, log)
        self.log_listbox.bind("<<ListboxSelect>>", self.on_log_select)
        # Scrollbar for the listbox
        self.scrollbar = Scrollbar(logfile_frame, orient=VERTICAL, command=self.log_listbox.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.log_listbox.config(yscrollcommand=self.scrollbar.set)
        # New frame for Open Log Button
        open_log_frame = ttk.Frame(backup_list_frame)
        open_log_frame.pack(pady=10)
        self.open_log_button = ttk.Button(open_log_frame, text="Open Log", command=self.open_selected_log, bootstyle=SECONDARY, state=DISABLED)
        self.open_log_button.pack(anchor='e')

        # Close Button
        self.close_button = ttk.Button(
            master, text=f"Close {config.SHORT_NAME} Status Monitor", command=self.on_closing, bootstyle=DANGER
        )
        self.close_button.pack(side=BOTTOM, pady=30)
        # Start server monitoring when the GUI starts
        self.start_monitoring()
        # Run quick_backup_check at startup and schedule it to run every hour (3600000 ms)
        self.quick_backup_check()
        self.master.after(3600000, self.schedule_quick_backup_check)

    def get_screen_width(self):
        """Get the screen width to position the window on the top right-hand side."""
        return self.master.winfo_screenwidth() - int(config.WINDOWGEO.split('x')[0])

    def get_window_geometry(self):
        """Get the window geometry with the screen height."""
        screen_height = self.master.winfo_screenheight()
        return f"{config.WINDOWGEO.split('x')[0]}x{screen_height}"

    def on_log_select(self, event):
        """Enable the open log button when a log is selected."""
        if self.log_listbox.curselection():
            self.open_log_button.config(state=NORMAL, bootstyle=PRIMARY)
        else:
            self.open_log_button.config(state=DISABLED, bootstyle=SECONDARY)

    def open_selected_log(self):
        """Opens the selected backup log in the default text editor (cross-platform)."""
        import sys
        selected_log = self.log_listbox.get(self.log_listbox.curselection())
        if selected_log:
            log_path = os.path.join(config.MOUNTPOINT, config.BACKUP_LOG, selected_log)
            try:
                if sys.platform.startswith("linux"):
                    subprocess.run(["xdg-open", log_path])  # Linux
                elif sys.platform == "darwin":
                    subprocess.run(["open", log_path])      # macOS -- Jim uses Mac
                else:
                    messagebox.showerror("Error", "Opening logs is not supported on this platform.")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open log: {str(e)}")

    def change_theme(self, event):
        """Change the application theme based on dropdown selection."""
        new_theme = self.theme_var.get()
        style = ttk.Style()
        style.theme_use(new_theme)

    def update_latest_backup_date(self):
        """Update the label with the latest backup date and set the color based on the date."""
        if self.backup_logs:
            latest_log = self.backup_logs[0]
            latest_backup_date = datetime.datetime.strptime(latest_log[:10], "%Y-%m-%d")
            days_since_backup = (datetime.datetime.now() - latest_backup_date).days

            if days_since_backup > 14:
                self.latest_backup_label.config(bootstyle=DANGER)
            elif days_since_backup > 7:
                self.latest_backup_label.config(bootstyle=WARNING)
            else:
                self.latest_backup_label.config(bootstyle=SUCCESS)

            self.latest_backup_label.config(text=f"Last Backup: {latest_log[:10]} [{days_since_backup} days]")
        else:
            self.latest_backup_label.config(text="Last Backup: Not Found")

    def get_backup_logs(self):
        """Retrieve available backup logs."""
        log_dir = os.path.join(config.MOUNTPOINT, config.BACKUP_LOG)
        if os.path.exists(log_dir):
            logs = sorted(
                [log for log in os.listdir(log_dir) if not log.startswith('.') and not log.endswith('.swp')],
                reverse=True
            )
            return logs
        return []

    def start_monitoring(self):
        """Starts monitoring in separate thread."""
        self.startbutton.config(text="Monitoring...", bootstyle=PRIMARY)
        self.stopbutton.config(text="Pause/Stop Monitoring", bootstyle=SECONDARY)
        self.stop_event.clear()
        # Change thread target to check_active()
        self.monitor_thread = threading.Thread(target=self.check_active, daemon=True)
        self.monitor_thread.start()

    # Renamed and modified function
    def check_active(self):
        """Checks server status using RESPONSE or PING based on config.CHECK_TYPE."""
        if config.CHECK_TYPE.upper() == "RESPONSE":
            while not self.stop_event.is_set():
                now = time.strftime('%Y/%m/%d %H:%M:%S %p')
                try:
                    response = requests.get(self.server_url, timeout=5)
                    if response.status_code == 200:
                        self.indicator.config(bootstyle=SUCCESS)
                        self.time.config(text=now)
                    else:
                        self.indicator.config(bootstyle=DANGER)
                except requests.RequestException:
                    self.indicator.config(bootstyle=DANGER)
                self.indicator.update_idletasks()
                self.quick_backup_check()
                time.sleep(self.refresh_interval)
        elif config.CHECK_TYPE.upper() == "PING":
            host = self.server_url.replace("https://", "").replace("http://", "").split("/")[0]
            while not self.stop_event.is_set():
                now = time.strftime('%Y/%m/%d %H:%M:%S %p')
                try:
                    result = subprocess.run(["ping", "-c", "1", host],
                                            stdout=subprocess.DEVNULL,
                                            stderr=subprocess.DEVNULL, timeout=5)
                    if result.returncode == 0:
                        self.indicator.config(bootstyle=SUCCESS)
                        self.time.config(text=now)
                    else:
                        self.indicator.config(bootstyle=DANGER)
                except Exception:
                    self.indicator.config(bootstyle=DANGER)
                self.indicator.update_idletasks()
                self.quick_backup_check()
                time.sleep(self.refresh_interval)
        else:
            while not self.stop_event.is_set():
                now = time.strftime('%Y/%m/%d %H:%M:%S %p')
                try:
                    response = requests.get(self.server_url, timeout=5)
                    if response.status_code == 200:
                        self.indicator.config(bootstyle=SUCCESS)
                        self.time.config(text=now)
                    else:
                        self.indicator.config(bootstyle=DANGER)
                except requests.RequestException:
                    self.indicator.config(bootstyle=DANGER)
                self.indicator.update_idletasks()
                self.quick_backup_check()   # Added: quickly check days since last backup
                time.sleep(self.refresh_interval)
                
    def schedule_quick_backup_check(self):
        """Schedules quick backup check once every hour."""
        self.quick_backup_check()
        self.master.after(3600000, self.schedule_quick_backup_check)

    def quick_backup_check(self):
        """Calculates days since last backup and updates the Last Backup label."""
        if self.backup_logs:
            try:
                latest_log = self.backup_logs[0]
                latest_backup_date = datetime.datetime.strptime(latest_log[:10], "%Y-%m-%d")
                days_since_backup = (datetime.datetime.now() - latest_backup_date).days
                self.latest_backup_label.config(text=f"Last Backup: {latest_log[:10]} [{days_since_backup} days]")
            except Exception:
                self.latest_backup_label.config(text="Last Backup: Error")
        else:
            self.latest_backup_label.config(text="Last Backup: Not Found")

    def stop_monitoring(self):
        """Stops monitoring."""
        self.stopbutton.config(text="Paused...", bootstyle=WARNING)
        self.startbutton.config(text="Start Monitoring", bootstyle=SECONDARY)
        self.indicator.config(bootstyle=WARNING)
        self.stop_event.set()

    def run_backup(self):
        """Runs the backup process in a separate thread to prevent UI freezing."""
        threading.Thread(target=self.run_backup_process, daemon=True).start()

    def run_backup_process(self):
        """Runs the backup process in a new terminal window."""
        BKUPDATE = datetime.datetime.now().strftime("%Y-%m-%d")
        rsync_command = [
            "gnome-terminal", "--geometry=120x24", "--", "bash", "-c", 
            f"rsync -avh --copy-links -e 'ssh -i {config.SSHKEYAUTH}' "
            f"{config.REMOTEUSER}@{config.REMOTEHOST}:~/{config.BACKUPLINK} "
            f"{config.MOUNTPOINT}/{config.BACKUP_DIR}/ --log-file={config.MOUNTPOINT}/{config.BACKUP_LOG}/{BKUPDATE}-{config.LOG_PREFIX}.log; "
            "read -p 'Press Enter to close...'"
        ]

        print(rsync_command)
        process = subprocess.Popen(rsync_command)  # Runs in a new terminal
        process.wait()                             # Wait for process to finish
        
        if process.returncode == 0:
            print(f"{config.SHORT_NAME} Files backed up at {os.path.join(os.getcwd(), config.BACKUP_DIR)}")
            self.backup_logs = self.get_backup_logs()
            self.log_listbox.delete(0, END)
            for log in self.backup_logs:
                self.log_listbox.insert(END, log)
            self.update_latest_backup_date()
        else:
            print("Backup failed:", process.stderr.read())

    def on_closing(self):
        """Handles window closing."""
        self.stop_event.set()
        self.master.destroy()

def mount_and_check_drive():
    import os, subprocess, sys
    can_mount_temp = False
    can_see_backup_temp = False
    can_see_log_temp = False

    try:
        result = subprocess.run(["mountpoint", "-q", config.MOUNTPOINT],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        can_see_backup = os.path.isdir(os.path.join(config.MOUNTPOINT, config.BACKUP_DIR))
        can_see_log = os.path.isdir(os.path.join(config.MOUNTPOINT, config.BACKUP_LOG))

        if result.returncode != 0 or not (can_see_backup and can_see_log):
            # Determine platform and choose terminal command accordingly.
            if sys.platform.startswith("darwin"):
                # MacOS version using osascript to launch Terminal and run the mount command.
                mount_cmd = f'sudo mount -t auto -U {config.BACKUPUUID} {config.MOUNTPOINT}; read -p "Press Enter to close..."'
                full_cmd = ['osascript', '-e', f'tell application "Terminal" to do script "{mount_cmd}"']
            else:
                # Linux version
                mount_cmd = f"sudo mount -t auto -U {config.BACKUPUUID} {config.MOUNTPOINT}; read -p 'Press Enter to close...'"
                full_cmd = ["gnome-terminal", "--", "bash", "-c", mount_cmd]

            subprocess.run(full_cmd)
            # Re-check the mount point after the terminal command completes
            result = subprocess.run(["mountpoint", "-q", config.MOUNTPOINT],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                can_mount_temp = True
                can_see_backup_temp = os.path.isdir(os.path.join(config.MOUNTPOINT, config.BACKUP_DIR))
                can_see_log_temp = os.path.isdir(os.path.join(config.MOUNTPOINT, config.BACKUP_LOG))
        return can_mount_temp, can_see_backup_temp, can_see_log_temp
    except Exception as e:
        print("Error in mount_and_check_drive:", e)
        return False, False, False

if __name__ == "__main__":
    root = ttk.Window(themename=config.GUI_THEME)
    # Set the window to always be on top
    root.attributes("-topmost", True)
    app = MonitorGUIApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
