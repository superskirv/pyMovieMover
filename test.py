import os, re, time

def removed_brackets(name):
    pattern = re.compile(r'\[.*?\]')
    string = re.sub(pattern, '', name)

    pattern = re.compile(r'\(.*?\)')
    string = re.sub(pattern, '', string)
    return string
def get_show_name(name):
    string = removed_brackets(name)

    if re.search(r'^(.*?)(?:S(\d{2})E\d{2}|s(\d{2})e\d{2}|S(\d{2})E\d{2}-E\d{2}|s(\d{2})e\d{2}-e\d{2})', string):
        match = re.search(r'^(.*?)(?:S(\d{2})E\d{2}|s(\d{2})e\d{2}|S(\d{2})E\d{2}-E\d{2}|s(\d{2})e\d{2}-e\d{2})', string)

        show_name_group = match.group(1)
        show_name = ' '.join(word.capitalize() for word in show_name_group.split('.'))
        show_name_with_spaces = show_name.replace('_', ' ').replace('-', ' ').title()
        stripped_string = show_name_with_spaces.rstrip('-').strip()

        return stripped_string
    elif re.search(r'^(.*?)(?:S\d{2})', string):
        match = re.search(r'^(.*?)(?:S\d{2})', string)

        show_name = match.group(1)
        formatted_show_name = ' '.join(word.capitalize() for word in show_name.split('.'))      #Need to search for underscores and spaces as well as periods.
        show_name_with_spaces = formatted_show_name.replace('_', ' ').replace('-', ' ').title()
        stripped_string = show_name_with_spaces.rstrip('-').strip()

        return stripped_string
    elif re.search(r'^([\w\s]+)\.\d+x\d+.*\.(.+)$', string):
        match = re.search(r'^([\w\s]+)\.\d+x\d+.*\.(.+)$', string)

        show_name_group = match.group(1)
        show_name_with_spaces = show_name_group.replace('_', ' ').replace('-', ' ').title()
        stripped_string = show_name_with_spaces.rstrip('-').strip()

        return stripped_string
    elif re.search(r'^([\w\s]+)[-_]\d+x\d+.*?[._](.+)$', string):
        match = re.search(r'^([\w\s]+)[-_]\d+x\d+.*?[._](.+)$', string)

        show_name_group = match.group(1)
        show_name_with_spaces = show_name_group.replace('_', ' ').replace('-', ' ').title()
        stripped_string = show_name_with_spaces.rstrip('-').strip()

        return stripped_string
    else:
        return "0000-Bad-Name"
def get_season(string):
    if re.search(r'^(.*?)(?:S(\d{2})E\d{2}|s(\d{2})e\d{2})', string): #S01E22 (season 01 episode 22)
        match = re.search(r'^(.*?)(?:S(\d{2})E\d{2}|s(\d{2})e\d{2})', string)

        season_group = match.group(2) or match.group(3)
        season = season_group if season_group else None

        return season
    elif re.search(r'^(.*?)(?:(\d{1})x\d{2})', string): #1x22 (season 1 X episode 22)
        match = re.search(r'^(.*?)(?:(\d{1})x\d{2})', string)

        season_group = match.group(2) or match.group(3)
        season = season_group if season_group else None
        season = season.zfill(2)

        return season
    elif re.search(r'^(.*?)(?:(\d{2})x\d{2})', string): #11x22 (season 11 X episode 22)
        match = re.search(r'^(.*?)(?:(\d{2})x\d{2})', string)

        season_group = match.group(2) or match.group(3)
        season = season_group if season_group else None

        return season
    else:
        return False
def get_subfolder(src, dest):
    file_name = os.path.basename(src)
    dir_type = os.path.basename(dest)
    if True:
        show_name = get_show_name(file_name)
        season_num = get_season(file_name)

        print('file_name: ',file_name)
        print('show_name: ',show_name)
        print('season_num: ',season_num)

        season_name = None
        if "extra" in file_name:
            season_name = 'Extras'
            season_num = None
        elif season_num:
            season_name = 'Season ' + season_num
        else:
            ##Failed to find sub folder from file name, trying folder name.
            last_folder = os.path.basename(dest)
            print('last_folder', last_folder)

            pattern = r'Season (\d+)'
            match = re.search(pattern, last_folder)
            if match:
                season_num = match.group(1)
                season_num = season_num.zfill(2)

            string = removed_brackets(last_folder)
            print('string', string)

            if "-" in string:
                parts = string.split("-")
            elif "." in string:
                parts = string.split(".")
            elif "_" in string:
                parts = string.split("_")
            else:
                show_name = string.strip()
                return f"{show_name}\\Season {season_num}"

            max_letters_count = 0
            save_string = ""
            for part in parts:
                print('part',part)
                non_letters_count = sum(1 for char in part if char.isalpha() == False)

                if len(part) - non_letters_count > max_letters_count:
                    max_letters_count = len(part) - non_letters_count
                    save_string = part
            print('save_string',save_string)
            show_name = save_string
            season_num = "XX"
            season_name = 'Season ' + season_num
            if not show_name:
                return "0003-Bad-Show-Name\\0000-Bad-Season-Name"
        subfolders = os.path.join(show_name, season_name)
        return subfolders
    else:
        return "0004-Bad-Show-Name\\0000-Bad-Season-Name"
def list_files(folder_path):
    try:
        # Get the list of files in the specified folder
        files = os.listdir(folder_path)

        # Print the file names with extensions
        for file in files:
            out = get_subfolder(file,folder_path)
            print("--FILE CHECKER: ",out, file)

    except FileNotFoundError:
        print(f"The specified folder '{folder_path}' does not exist.")
    except PermissionError:
        print(f"Permission denied to access '{folder_path}'.")

# Replace 'your_folder_path' with the actual path of the folder you want to examine
folder_path = 'Z:\\Torrents\Completed\\[Anime Time] Spy x Family (Season 01) [BD] [Dual Audio][1080p][HEVC 10bit x265][AAC][Eng Sub] [Batch]'
list_files(folder_path)
