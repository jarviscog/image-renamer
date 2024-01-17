import os
from typing import Tuple, List
import re
from pprint import pprint
from pathlib import Path
import argparse
from PIL import Image
from datetime import datetime
from pillow_heif import register_heif_opener
import ffmpeg

class CatagorizedMedia:
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

def get_jpg_timestamp(file_path) -> datetime | None: 
    exif = Image.open(file_path).getexif()
    for item in (exif.items()):
        print(f"{item}")
    if not exif:
        raise Exception(f'Image {file_path} does not have EXIF data.')
    if 36867 in exif.keys(): 
        return exif[36867]
    elif 306 in exif.keys():
        return exif[306]
    else:
        return None

def get_png_timestamp(file_path) -> str | None: 
    file = Image.open(file_path)
    file.load()
    exif = file.getexif()
    # for key in exif.keys(): 
        # print(key, exif[key])

    # Try standard exif
    if 36867 in exif.keys(): 
        return exif[36867]
    elif 306 in exif.keys():
        return exif[306]

    # If the file is from photoshop, we can try and get the date created 
    # XML is a binary stream, so we need to remove some characters that mess with the regex
    new_string = ""
    for char in file.info['XML:com.adobe.xmp']:
        if char != '\n':
            new_string += char 
    m = re.match(r'(.*)(<photoshop:DateCreated>)(.*)(<\/photoshop:DateCreated>)(.*)', new_string)
    if m: 
        new_string = m[3].replace("T", " ")
        new_string = new_string.replace("-", ":")
        print(new_string)
        return new_string
    
    return None

def get_heic_timestamp(file_path: str) -> str | None: 
    register_heif_opener()
    file = Image.open(file_path)
    exif = file.getexif()
    # for key in exif.keys():
    #    print(key, exif[key])
    if not exif:
        raise Exception(f'Image {file_path} does not have EXIF data.')
    if 36867 in exif.keys(): 
        return exif[36867]
    elif 306 in exif.keys():
        return exif[306]
    else:
        return None


def get_mp4_timestamp(file_path: str) -> str | None: 

    # metadata = ffmpeg.probe(file_path)["streams"]
    time = os.path.getmtime(file_path)
    pprint(time)
    # for key in exif.keys():
    #    print(key, exif[key])

TIMESTAMP_FUNCTIONS = {
        '.jpg': get_jpg_timestamp,
        '.png': get_png_timestamp,
        '.heic': get_heic_timestamp,
        '.mp4': get_mp4_timestamp 
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

    print("Rename: ", old_name)

def get_image_list(dir_path: Path) -> CatagorizedMedia | None:
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
        if re.match(pattern="[0-9]{8}_[0-9]{6}[.]", string=file): # Pattern: YYYYMMDD_HHMMSS. We don't want to touch these
            completed_media_files.append(file)
            continue

        files_to_convert.append(full_path)

    pprint(unsupported_type)

    media = CatagorizedMedia(
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
        # print("File was supplied")
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
        print("Directory was supplied")

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

            date_time = get_timestamp_of_media(file)
            extension = get_filetype(file)
            
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
        for old_filename, new_filename in new_filenames:
            print("{:<20} -> {:<20}".format(os.path.split(old_filename)[1], os.path.split(new_filename)[1]))
        
        print('Failed files: ')
        pprint(error)

        print('Unsupported filetypes: ')
        pprint(media_lists.unsupported_type[0])
        print('\n')

        ans = input("Would you like to rename the files? (y/n)")
        if ans == "y": 
            for (old_filename, new_filename) in new_filenames:
                print(old_filename)
                rename_file(old_filename, new_filename)
        else:
            return
     



if __name__ == "__main__":
    main()

