import os
from typing import Tuple, List
import re
from pprint import pprint
from pathlib import Path
import argparse
from PIL import Image
from datetime import datetime
from pillow_heif import register_heif_opener
from random import randint
import exifread

# TODO: Create a return class from the get_ functions for each type that includes info, such as where the filename came from (exif, filename) etc.

class CategorizedMedia:
    def __init__(self, 
                 total: list[str]= [],
                 directories: list[str] = [], 
                 files_to_convert: list[str] = [], 
                 unsupported_type: list[str] = [], 
                 completed: list[str] = []
                 ):
        self.total = total,
        self.directories = directories,
        self.files_to_convert = files_to_convert,
        self.unsupported_type = unsupported_type,
        self.completed = completed

def get_jpg_timestamp(file_path: str) -> str | None: 
    exif = Image.open(file_path).getexif()
    if exif:
        if 36867 in exif.keys(): 
            return exif[36867]
        elif 306 in exif.keys():
            return exif[306]
    # else: 
        # print(f"No exif found: {file_path}")

    # From filename
    timestamp = timestamp_from_filename(file_path)
    if timestamp: return timestamp

    time = os.path.getmtime(file_path)
    timestamp = datetime.fromtimestamp(time).strftime('%Y:%m:%d %H:%M:%S')
    return timestamp

def get_png_timestamp(file_path) -> str | None: 
    file = Image.open(file_path)
    file.load()

    # Try standard exif
    exif = file.getexif()
    if exif:
        if 36867 in exif.keys(): 
            return exif[36867]
        elif 306 in exif.keys():
            return exif[306]
    # else:
        # print(f"No exif found: {file_path}")

    # If the file is from photoshop, we can try and get the date created 
    if 'XML:com.adobe.xmp' in file.info.keys():
        # XML is a binary stream, so we need to remove some characters that mess with the regex
        new_string = ""
        for char in file.info['XML:com.adobe.xmp']:
            if char != '\n':
                new_string += char 
        m = re.match(r'(.*)(<photoshop:DateCreated>)(.*)(<\/photoshop:DateCreated>)(.*)', new_string)
        if m: 
            new_string = m[3].replace("T", " ")
            new_string = new_string.replace("-", ":")
            return new_string

    # From filename
    timestamp = timestamp_from_filename(file_path)
    if timestamp: return timestamp
    
    # From file metadata
    time = os.path.getmtime(file_path)
    timestamp = datetime.fromtimestamp(time).strftime('%Y:%m:%d %H:%M:%S')
    return timestamp

def get_heic_timestamp(file_path: str) -> str | None: 

    # From exif
    register_heif_opener()
    exif = Image.open(file_path).getexif()
    if not exif:
        raise Exception(f'Image {file_path} does not have EXIF data.')
    if 36867 in exif.keys(): 
        return exif[36867]
    elif 306 in exif.keys():
        return exif[306]

    # From filename
    timestamp = timestamp_from_filename(file_path)
    if timestamp: return timestamp

    # From file metadata
    time = os.path.getmtime(file_path)
    timestamp = datetime.fromtimestamp(time).strftime('%Y:%m:%d %H:%M:%S')
    return timestamp

def get_mp4_timestamp(file_path: str) -> str | None: 

    # TODO: There might be a way to get the timestamp from ffmpeg
    # metadata = ffmpeg.probe(file_path)["streams"]

    # From filename
    timestamp = timestamp_from_filename(file_path)
    if timestamp: return timestamp

    # From file metadata
    time = os.path.getmtime(file_path)
    timestamp = datetime.fromtimestamp(time).strftime('%Y:%m:%d %H:%M:%S')
    return timestamp

def get_mov_timestamp(file_path: str) -> str | None: 

    # TODO: There might be a way to get the timestamp from ffmpeg
    # metadata = ffmpeg.probe(file_path)["streams"]

    # From filename
    timestamp = timestamp_from_filename(file_path)
    if timestamp: return timestamp

    # From file metadata
    time = os.path.getmtime(file_path)
    timestamp = datetime.fromtimestamp(time).strftime('%Y:%m:%d %H:%M:%S')
    return timestamp


def get_webp_timestamp(filepath):
    with open(filepath, 'rb') as f:
        tags = exifread.process_file(f, stop_tag="EXIF DateTimeOriginal", details=False)
        time = tags.get("EXIF DateTimeOriginal")
        if time:
            return str(time)
    if not time:
        time = os.path.getmtime(filepath)

    if time:
        timestamp = datetime.fromtimestamp(time).strftime('%Y:%m:%d %H:%M:%S')
        return timestamp
    return None


def timestamp_from_filename(file_path: str) -> str | None:
    # Try a few different regexes
    r = re.match(r".*((\d{4})([:\/-])(\d{2})\3(\d{2}).(\d{2})([:\/-])(\d{2})\3(\d{2}))", file_path);
    if r:
        # print("Getting timestamp from filename: {}".format(file_path))
        year = r[2]
        month = r[4]
        day = r[5]
        hour = r[6]
        miniute = r[8]
        second = r[9]
        timestamp = "{}:{}:{} {}:{}:{}".format(year, month, day, hour, miniute, second)
        # print(timestamp)
        return timestamp

    return None


TIMESTAMP_FUNCTIONS = {
        '.jpg': get_jpg_timestamp,
        '.jpeg': get_jpg_timestamp,
        '.png': get_png_timestamp,
        '.heic': get_heic_timestamp,
        '.mp4': get_mp4_timestamp,
        '.mov': get_mov_timestamp,
        '.webp': get_webp_timestamp 
        }

def get_timestamp_of_media(file_path: str) -> str | None:
    # Get the type of file
    ex = str(os.path.splitext(file_path)[-1]).lower()
    # print(f"Extension: {ex}")

    if ex not in TIMESTAMP_FUNCTIONS.keys():
        print("Filetype not supported")
        return None
    timestamp = TIMESTAMP_FUNCTIONS[ex](file_path)
    return timestamp

def get_filetype(filepath: str) -> str:
    return str(os.path.splitext(filepath)[-1]).lower()

def is_supported(filetype: str) -> bool:
    return filetype in TIMESTAMP_FUNCTIONS.keys()

def timestamp_to_filename(datetime: str) -> str | None:
    
    (date, time) = datetime.split(' ') 
    (year, month, day) = date.split(':')
    (hour, miniute, second) = time.split(':')

    new_filename: str = year + month + day + "_" + hour + miniute + second
    # print(new_filename)
    return new_filename 

def rename_file(old_name: str, new_name: str):

    print("Rename: ", old_name, " -> ", new_name)
    try_name = new_name
    (new_name_base, ex) = os.path.splitext(new_name)
    while os.path.exists(try_name):
        print()
        ri = str(randint(100, 199))
        try_name = new_name_base + "_" + ri + ex
    os.rename(old_name, try_name)

def get_image_list(dir_path: Path) -> CategorizedMedia | None:
    if dir_path is None:
        return

    files = os.listdir(dir_path)

    # Grab all files and find the status of them
    files_to_convert: list[str] = []
    completed_media_files: list[str] = []
    directories: list[str] = []
    unsupported_type: list[str] = []
    for file in files:
        full_path = os.path.join(dir_path, file)
        file_extension = get_filetype(full_path);

        if os.path.isdir(full_path):
            directories.append(full_path)
            continue
        if not is_supported(file_extension):
            unsupported_type.append(full_path)
            continue
        if re.match(pattern="[0-9]{8}_[0-9]{6}.*", string=file): # Pattern: YYYYMMDD_HHMMSS. We don't want to touch these
            completed_media_files.append(file)
            continue

        files_to_convert.append(full_path)

    pprint(unsupported_type)

    media = CategorizedMedia(
            total=files,
            directories = directories,
            files_to_convert = files_to_convert,
            unsupported_type = unsupported_type,
            completed = completed_media_files
            )

    return media 

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='file to rename', type=str)
    parser.add_argument('-d', '--directory', help='directory of files to rename', type=str)
    args = parser.parse_args()

    if args.file:
        date_time = get_timestamp_of_media(args.file)
        if not date_time:
            print(f"Could not get datetime of {date_time}")
            return
        print(f"Datetime is: {date_time}")
        new_filename = timestamp_to_filename(date_time)
        if not new_filename:
            print(f"Could not convert to filename: {date_time}")
            return
        print("{:<20} -> {:<20}".format(args.file, new_filename))
        ans = input("Would you like to rename the files? (y/n)")
        if ans == "y": 
            rename_file(args.file, new_filename)
        else:
            return


    elif args.directory:
        # Index all of the files in the filepath
        media_lists = get_image_list(args.directory)
        if not media_lists:
            raise NotImplementedError

        # Stats about what was found
        print(f"Total: {len(media_lists.total[0])}")
        print(f"Directories: {len(media_lists.directories[0])}")
        print(f"Files to convert: {len(media_lists.files_to_convert[0])}")
        print(f"Unsupported filetype: {len(media_lists.unsupported_type[0])}")
        print(f"Already completed files: {len(media_lists.completed)}")

        success = []
        error = []
        new_filenames: List[Tuple[str, str]] = []

        print("")
        # TODO: Why do I need to get the first index here?
        for file in media_lists.files_to_convert[0]:

            extension = get_filetype(file)
            date_time = get_timestamp_of_media(file)
            
            if date_time is None:
                error.append(file)
                continue
            new_filename = timestamp_to_filename(date_time)
            if not new_filename:
                print(f"Could not convert to filename: {date_time}")
                error.append(file)
                continue

            new_filename = new_filename + extension
            # print("{:<20} -> {:<20}".format(file, new_filename))
            success.append(file)
            directory = os.path.dirname(file)
            # print(directory)
            new_filenames.append((file, os.path.join(directory, new_filename)))


        print('Files to rename: ')
        sorted_filenames = sorted(new_filenames, key= lambda x: x[1])
        for old_filename, new_filename in sorted_filenames:
            print("{:<40} -> {:<40}".format(os.path.split(old_filename)[1], os.path.split(new_filename)[1]))
            # print("{:<40} -> {:>150}".format(old_filename, new_filename))
        
        print('Failed files: ')
        pprint(error)

        print('Unsupported filetypes: ')
        pprint(media_lists.unsupported_type[0])
        print('')

        if len(sorted_filenames) == 0:
            print("No files to convert")
            return
        oldest_timestamp = datetime.strptime(os.path.split(sorted_filenames[0][1])[1].split(".")[0], "%Y%m%d_%H%M%S")
        newest_timestamp = datetime.strptime(os.path.split(sorted_filenames[-1][1])[1].split(".")[0], "%Y%m%d_%H%M%S")
        print(f"Time range of files: {oldest_timestamp.strftime('%a %d %b %Y, %I:%M%p')} -> {newest_timestamp.strftime('%a %d %b %Y, %I:%M%p')}")

        ans = input("Would you like to rename the files? (y/n)")
        if ans == "y": 
            for (old_filename, new_filename) in new_filenames:
                rename_file(old_filename, new_filename)
        else:
            return
     
if __name__ == "__main__":
    main()

