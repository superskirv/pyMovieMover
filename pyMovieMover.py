import tkinter as tk
from tkinter import ttk, Scrollbar, filedialog, messagebox
import os, re, threading, time
from queue import Queue
#import hashlib
#
#   Version 1.2b
#   Last Update: 2023dec16
#   Created by: ChatGPT4 and Super.Skirv
#

global file_types, user_destinations
#String must end with directories full name as 'movies', 'shows', or 'anime'(which is the same as shows.)
#String probably needs double backwards slashs(on windows), maybe linux also.
#Relative paths probably work here also.
#You can add as many locations here as you want. They just wont work if they dont meet the above requirements. Unless you change things...
user_destinations = ["Z:\\plex\\movies", "Z:\\plex\\shows", "Z:\\plex\\anime"]
#User defined file types to move.
file_types = [".mp4", ".avi", ".mkv"]

class FileCopier:
    def __init__(self, queue, tree, current_dest_label):
        self.queue = queue
        self.tree = tree  # Updated reference to tree
        self.current_dest_label = current_dest_label
        self.stop_copy = False
        self.currently_copying = False
        self.paused = False
        self.kill_copy = False
        self.retry = 0
    def copy_next_file(self):
        if not self.queue.empty():
            self.currently_copying = True
            src, dest = self.queue.get()
            threading.Thread(target=self.copy_file_thread, args=(src, dest)).start()
    def get_file_md5(self, file_path):
        # Calculate the MD5 hash of a file
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(4096)  # Read in 4K chunks
                if not data:
                    break
                md5.update(data)
        return md5.hexdigest()
    def get_subfolder(self, src, dest):
        file_name = os.path.basename(src)
        dir_type = os.path.basename(dest)
        if dir_type == "movies":
            subfolder = self.get_movie_letter(file_name)
            if subfolder:
                return subfolder
            else:
                return False
        elif dir_type == "shows" or dir_type == "anime":
            show_name = self.get_show_name(file_name)
            season_num = self.get_season(file_name)

            # print('show_name: ',show_name)
            # print('season_num: ',season_num)
            # print('file_name: ',file_name)

            season_name = None
            if "extra" in file_name:
                season_name = 'Extras'
                season_num = None
            elif not show_name:
                return False
            elif season_num:
                season_name = 'Season ' + season_num
            else:
                return False
            subfolders = os.path.join(show_name, season_name)
            return subfolders
        else:
            return False
    def get_movie_letter(self, string):
        if string.lower().startswith("the"):
            string = re.sub(r'^the[^a-zA-Z0-9]*', '', string, flags=re.IGNORECASE)

        subfolder = os.path.basename(string)[0].upper()
        if any(char.isdigit() for char in subfolder):
            return "#"
        else:
            return subfolder
    def get_season(self, string):
        pattern = r'^(.*?)(?:S(\d{2})E\d{2}|s(\d{2})e\d{2})'
        match = re.search(pattern, string)
        if match:
            season_group = match.group(2) or match.group(3)
            season = season_group if season_group else None
            return season
        else:
            return False
    def get_show_name(self, string):
        pattern = r'^(.*?)(?:S(\d{2})E\d{2}|s(\d{2})e\d{2}|S(\d{2})E\d{2}-E\d{2}|s(\d{2})e\d{2}-e\d{2})'
        match = re.search(pattern, string)
        #print("--match: ",match)
        if match:
            show_name_group = match.group(1)
            show_name = ' '.join(word.capitalize() for word in show_name_group.split('.'))
            stripped_string = show_name.rstrip('-').strip()
            return stripped_string
        else:
            pattern = r'^(.*?)(?:S\d{2})'
            match = re.search(pattern, string)
            #print("--match: ",match)
            if match:
                show_name = match.group(1)
                formatted_show_name = ' '.join(word.capitalize() for word in show_name.split('.'))      #Need to search for underscores and spaces as well as periods.
                stripped_string = show_name.rstrip('-').strip()
                return stripped_string
            else:
                return "0000-Show-Name"
    def copy_file_thread(self, src, dest):
        self.stop_copy = False
        self.currently_copying = True
        self.kill_copy = False
        self.paused = False
        dest_loc = dest
        # Create the subfolder based on the first letter of the file name
        subfolder = self.get_subfolder(src, dest)
        if not subfolder:
            self.update_gui_error(f"Could not determine where to put file. File/Destination name might be weird. {src}")
            self.kill_copy = True
        dest_folder = os.path.join(dest, subfolder)
        self.set_current_destination_label(os.path.join(dest_folder, os.path.basename(src)))

        # Check and create destination folder if it doesn't exist
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder, exist_ok=True)

        dest = os.path.join(dest_folder, os.path.basename(src))

        # Check if the file already exists in the destination folder
        # if os.path.exists(dest):
        #     # Calculate MD5 hash of source and destination files
        #     src_md5 = self.get_file_md5(src)
        #     dest_md5 = self.get_file_md5(dest)
        #
        #     # Compare MD5 hashes
        #     if src_md5 == dest_md5:
        #         self.update_gui_error(f"File already exists and has the same content: {os.path.basename(src)}")
        #         self.copy_next_file()  # Skip to the next file
        #     else:
        #         os.remove(dest)

        buffer_size = 1024 * 1024  # 1MB
        file_size = os.path.getsize(src)
        copied = 0
        start_time = time.time()

        if not os.path.exists(dest):
            try:
                with open(src, 'rb') as fsrc, open(dest, 'wb') as fdst:
                    while True:
                        if self.stop_copy:
                            os.remove(dest)  # Delete partially copied file
                            break
                        if self.kill_copy:
                            break
                        if self.paused:
                            time.sleep(1)  # Pause for 1 second
                            continue
                        buffer = fsrc.read(buffer_size)
                        if not buffer:
                            break

                        fdst.write(buffer)
                        copied += len(buffer)
                        elapsed_time = time.time() - start_time
                        speed = copied / elapsed_time if elapsed_time > 0 else 0
                        eta = (file_size - copied) / speed if speed > 0 else 0
                        self.update_gui_progress(copied / file_size, speed, eta, dest)
                        percent = copied / file_size
            except PermissionError as e:
                self.retry += 1
                if self.retry > 3:
                    print(f"An Permission Error occurred: {e}\nDeleting partial file and skipping.", dest)
                    os.remove(dest)
                else:
                    print(f"An Permission Error occurred: \nRetring file {3-self.retry} more times before skipping.", dest)
                    os.remove(dest)
            except Exception as e:
                self.retry += 1
                if self.retry > 3:
                    #self.update_gui_error(f"Current file will be deleted. An error occurred: {e}")
                    print(f"An error occurred: {e}\nCurrent file will be deleted.", dest)
                    os.remove(dest)
                else:
                    #self.update_gui_error(f"An error occurred: {e}\nRetring file 3 times before skiping.")
                    print(f"An error occurred: \nRetring file {3-self.retry} more times before skipping.", dest)
                    os.remove(dest)
        if self.retry <= 0 or self.retry > 3:
            children = self.tree.get_children()
            if children:
                self.tree.delete(children[0])
            self.retry = 0
        else:
            subfolder = copier.get_subfolder(file, dest_loc)
            tree.insert("", "end", values=(os.path.basename(file), os.path.join(dest_loc, subfolder) if subfolder else dest_loc))
            self.queue.put((file, dest_loc))

        self.currently_copying = False
        self.copy_next_file()
    def update_gui_progress(self, ratio, speed, eta, dest):
        percentage = int(ratio * 100)
        progress_var.set(percentage)
        speed_label.config(text=f"Speed: {speed / 1024 / 1024:.2f} MB/s")
        eta_label.config(text=f"ETA: {eta:.1f}s")

        # Update the Treeview with file information
        file_info = os.path.basename(dest)
        dest_folder = os.path.dirname(dest)
    def update_gui_error(self, message):
        messagebox.showerror("Error", message)
    def skip_current_file(self):
        if self.currently_copying:
            self.stop_copy = True
    def toggle_pause(self):
        self.paused = not self.paused
    def set_current_destination_label(self, dest):
        self.current_dest_label.config(text=f"{dest}")
def find_movie_files(directory, extensions=None):
    global file_types
    if extensions is None:
        extensions = file_types

    movie_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(tuple(extensions)):
                movie_files.append(os.path.join(root, file))
    return movie_files
def add_to_queue():
    source_dir = source_entry.get()
    if not source_dir:
        messagebox.showerror("Error", "Please select a source directory.")
        return

    files_to_copy = find_movie_files(source_dir)
    if not files_to_copy:
        messagebox.showinfo("Info", "No movie files found in the selected directory.")
        return

    dest = dest_entry.get()  # Get the selected destination folder

    if not dest:
        messagebox.showerror("Error", "Please select a destination directory.")
        return

    for file in files_to_copy:
        queue.put((file, dest))
        subfolder = copier.get_subfolder(file, dest)
        tree.insert("", "end", values=(os.path.basename(file), os.path.join(dest, subfolder) if subfolder else dest))
def start_copying():
    if not dest_entry.get():
        messagebox.showerror("Error", "Please select a destination directory.")
        return
    if queue.empty():
        messagebox.showinfo("Info", "No files in the queue to copy.")
        return
    if not copier.currently_copying:
        copier.copy_next_file()
def delete_selected():
    selected_item = tree.selection()
    if selected_item:
        tree.delete(selected_item[0])
        remove_from_queue(selected_item[0])
def stop_copy():
    copier.stop_copy = True
def clear_queue():
    if tree.get_children():
        tree.delete(*tree.get_children())
        remove_from_queue()
def remove_from_queue(index=None):
    if index is not None:
        queue.queue.queue = [item for i, item in enumerate(queue.queue.queue) if i != index]
    else:
        queue.queue.queue.clear()

app = tk.Tk()
app.title("Movie File Copier")

queue = Queue()

# Top Button Frame
button_frame = tk.Frame(app)
button_frame.pack(fill=tk.X)
#Queue Main Frame
queue_main_frame = tk.Frame(app)
queue_main_frame.pack(fill=tk.BOTH, expand=True)
# Progress Frame - Positioned at the bottom
progress_frame = tk.Frame(app)
progress_frame.pack(fill=tk.X, side=tk.BOTTOM)

# Add a label to show the current job's copy destination
current_destination_label = tk.Label(progress_frame, text="Destination: N/A")
current_destination_label.pack(side=tk.TOP)

copier = FileCopier(queue, None, current_destination_label)

source_entry = tk.Entry(button_frame)
source_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
source_button = tk.Button(button_frame, text="Select Source", command=lambda: [source_entry.delete(0, tk.END), source_entry.insert(0, filedialog.askdirectory())])
source_button.pack(side=tk.LEFT)

dest_var = tk.StringVar()
dest_entry = ttk.Combobox(button_frame, textvariable=dest_var, state="readonly", values=user_destinations)
dest_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

# Queue List Frame
queue_list_frame = tk.Frame(queue_main_frame)
queue_list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Create a vertical scrollbar
tree_scrollbar = Scrollbar(queue_list_frame, orient="vertical")

# Create the Treeview with the vertical scrollbar
tree = ttk.Treeview(
    queue_list_frame,
    columns=("File", "Destination"),
    show="headings",
    selectmode="browse",
    yscrollcommand=tree_scrollbar.set  # Link the Treeview to the scrollbar
)
tree.heading("File", text="File")
tree.heading("Destination", text="Destination")
tree.column("File", anchor="w", width=200)
tree.column("Destination", anchor="w", width=400)
tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Set the scrollbar command to update the view
tree_scrollbar.config(command=tree.yview)
tree_scrollbar.pack(side=tk.RIGHT, fill="y")

copier = FileCopier(queue, tree, current_destination_label)

# Queue Button Frame
queue_button_frame = tk.Frame(queue_main_frame)
queue_button_frame.pack(fill=tk.X)

queue_button = tk.Button(queue_button_frame, text="Add to Queue", command=add_to_queue)
queue_button.pack()

start_button = tk.Button(queue_button_frame, text="Start Copying", command=start_copying)
start_button.pack()

pause_button = tk.Button(queue_button_frame, text="Pause/Resume", command=copier.toggle_pause)
pause_button.pack()

pause_button = tk.Button(queue_button_frame, text="Stop", command=stop_copy)
pause_button.pack()

skip_button = tk.Button(queue_button_frame, text="Skip Current File", command=copier.skip_current_file)
skip_button.pack()

delete_button = tk.Button(queue_button_frame, text="Delete Selected", command=delete_selected)
delete_button.pack()

clear_button = tk.Button(queue_button_frame, text="Clear Queue", command=clear_queue)
clear_button.pack()

# Arrange "Speed" and "ETA" labels next to each other
speed_label = tk.Label(progress_frame, text="Speed: 0 MB/s")
speed_label.pack(side=tk.LEFT)

eta_label = tk.Label(progress_frame, text="ETA: 0 seconds")
eta_label.pack(side=tk.LEFT)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=200, mode="determinate", variable=progress_var)
progress_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True)

app.mainloop()
