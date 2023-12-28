import os
import re
import tkinter as tk
import tkinter.filedialog
from pathlib import Path
from typing import List, Tuple, Union

import PIL
from PIL import ImageTk, Image
from pprint import pprint


# Taken from
#   https://stackoverflow.com/questions/23064549/get-date-and-time-when-photo-was-taken-from-exif-data-using-pil

def get_timestamp_of_media(file_path: Path):

    ex = str(os.path.splitext(file_path)[-1]).lower()
    if ex not in ['.jpg']:
        return None

    print("Jpg: " + ex)
    return 0

    # key = "DateTimeOriginal"
    # tag_by_id: dict = PIL.ExifTags.TAGS
    # try:
    #     im: PIL.Image.Image = PIL.Image.open(str(file_path))
    # except FileNotFoundError:
    #         return -1
    # exif: PIL.Photo.Exif = im.getexif()
    # if not exif:
    #         return -1
    # tag_by_name = {tag_by_id[dec_value]: exif[dec_value] for dec_value in exif if dec_value in tag_by_id}
    # result_list = []
    # if isinstance(key, int):
    #     result_list.append(exif.get(key, None))
    # try:
    #     dec_value = int(key, 16)
    #     result_list.append(exif.get(dec_value, None))
    # except ValueError:
    #     ...
    # result_list.append(tag_by_name.get(key, None))
    # return result_list if len(result_list) > 1 else result_list[0]


selected_folder = ""

root = tk.Tk()
root.grid_rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

frame_main = tk.Frame(root)
# frame_main = tk.Frame(root, bg="gray")

frame_main.grid(sticky='news', pady=5, padx=5)

file_select_entry = tk.Entry(master=frame_main, width=60, background='white')
file_select_entry.insert(0, "Path")
file_select_entry.configure(state='disabled')
file_select_entry.grid(row=0, column=1, pady=5, sticky='nwe')


def select_folder():
    return_dir = tkinter.filedialog.askdirectory()
    # print(return_dir)
    global selected_folder
    selected_folder = return_dir
    file_select_entry.configure(state='normal')
    file_select_entry.delete(0, tk.END)
    file_select_entry.insert(index=0, string=return_dir)
    file_select_entry.configure(state='disabled')


file_selection_button = tk.Button(frame_main, text="Select Folder", command=select_folder)
file_selection_button.grid(row=0, column=2, pady=5, sticky='nw')


def get_images():
    if selected_folder is None:
        return

    print("Getting Images")
    files = os.listdir(selected_folder)

    # Grab all files and find the status of them
    media_files = []
    completed_media_files = []
    directories = []
    other = []
    for file in files:
        full_path = os.path.join(selected_folder, file)
        file_extension = str(os.path.splitext(full_path)[-1]).lower()

        if os.path.isdir(full_path):
            directories.append(full_path)
            continue
        if file_extension not in [".jpg", '.mp4', '.png', '.heic', '.mov']:
            other.append(full_path)
            continue
        if re.match(pattern="[0-9]{8}_[0-9]{6}[.]", string=file):
            completed_media_files.append(full_path)
            continue

        media_files.append(full_path)

    # Stats about what was found
    print(f"Items: {len(files)}")
    print(f"Media files: {len(media_files)}")
    print(f"Non-media files: {len(other)}")
    print(f"Directories: {len(directories)}")
    print(f"Already completed files: {len(completed_media_files)}")
    # print("Files to convert:")
    # pprint(media_files)

    temp_folder = os.path.join(selected_folder, "temp")
    if not os.path.exists(temp_folder):
        os.mkdir(temp_folder)

    files_with_metadata = []
    files_without_metadata = []
    for file in media_files:
        full_path = os.path.join(selected_folder, file)

        date_time = get_timestamp_of_media(full_path)
        if date_time is None:
            files_without_metadata.append(full_path)
            continue
        files_with_metadata.append((full_path, date_time))

    pprint(files_with_metadata)
    pprint(files_without_metadata)


generate_list_button = tk.Button(frame_main, text="List Images", height=1, command=get_images)
generate_list_button.grid(row=1, column=1, columnspan=2, pady=5, padx=200, sticky='nswe')


image_visualization_grid = tk.Label(frame_main, text="Images", height=30)
image_visualization_grid.grid(row=2, column=0, pady=5, sticky='nwe', columnspan=3)
# raw_image = Image.open('image.png')
# scaled_img = raw_image.resize((100,100))
# img = ImageTk.PhotoImage(scaled_img)
# panel = tk.Label(root, image=img, width=100, height=100)
# panel.grid(row=2, column=2, pady=(5,0), sticky='nw')
def rename_images():
    if selected_folder != None:
        print(f"Renaming Images in {selected_folder}")

confirm_button = tk.Button(frame_main, text="Generate", width=10, height=3, command=rename_images)
confirm_button.grid(row=3, column=1, columnspan=2, pady=5, padx=200, sticky='news')

root.mainloop()


