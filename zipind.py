"""
    Create by: apenasrr
    Source: https://github.com/apenasrr/zipind
    
    Compresses a folder into independent parts.
    Works in hybrid mode:
    -Compact folder dividing into independent parts, grouping your files in 
     alphanumeric order. 
    -Respects the ordering of folders and files.
    -Respects the internal structure of folders
    -If any file is larger than the defined maximum size, the specific 
     file is partitioned in dependent mode.
     
    Requirement: 
    -Have Winrar installed
    
    Support:
        Compression only to .rar
        
    Last_update: 2020-06-29
"""

import os
import subprocess
from config_handler import handle_config_file

   
def save_txt(str_content, str_name):

    # UTF-8 can't handle with the follow caracter in a folder name: 
    text_file = open(f"{str_name}.txt", "w", encoding='utf_16')
    text_file.write(str_content)
    text_file.close()


def ensure_folder_existence(folders_name):
    
    for folder_name in folders_name:
        existence = os.path.isdir(f'./{folder_name}')
        if existence is False:
            os.mkdir(folder_name)
    
    
def ensure_folders_existence():

    folders_name = ['config', 'output']
    ensure_folder_existence(folders_name)

        
def create_rar_single_file(path_file_rar, path_origin, max_size=None):

    create_rar_file(path_file_rar, '"' + path_origin + '"', 
                    max_size=max_size)
        
    
def create_rar_file_from_list_file(path_file_rar, list_files, max_size=None):
    
    if len(list_files) > 1:
        stringa = '\n\n'.join(list_files)
        save_txt(stringa, 'files_to_zip')
        file = 'files_to_zip.txt'
        create_rar_file(path_file_rar, f'@{file}', max_size)
        os.remove(file)
    else:
        path_file_list = list_files[0]
        create_rar_file(path_file_rar, f'"{path_file_list}"', max_size)
    
            
def clean_cmd():

    clear = lambda: os.system('cls')
    clear()

    
def get_config_max_file_size(path_file_config):

    max_file_size = handle_config_file(path_file_config, 
                                       'file_size', parse=True)
    max_file_size = max_file_size['file_size'][0]
    max_file_size = int(max_file_size)
    return max_file_size

    
def get_config_dir_output(path_file_config):

    dir_output = handle_config_file(path_file_config, 
                                    'dir_output', parse=True)
    dir_output = dir_output['dir_output'][0]
    
    if dir_output == '':
        return None
    else:
        return dir_output
    
    
def set_config_max_file_size(path_file_config, max_file_size):
    
    handle_config_file(path_file_config, 'file_size', max_file_size)

    
def set_config_path_dir_output(path_file_config, path_dir_output):

    handle_config_file(path_file_config, 'dir_output', path_dir_output)


def ask_mb_file():
    
    mb_per_file = int(input('Type the maximum size per part in MB ' +
                            '(Ex.: 400): '))

    return mb_per_file
    
    
def ask_path_dir_output():
    
    path_dir_output = input('Paste the  folder path where the compressed ' +
                            'files should be saved: \n')
    # TODO test dir
    
    return path_dir_output    


def define_path_dir_output(path_file_config, path_dir_output):

    if path_dir_output is not None:
        repeat_path_dir_output = \
            input(f'\n{path_dir_output}\n' + 
                  f'Compress files in the folder above? y/n ')
        print('')
        if repeat_path_dir_output == 'n':
            path_dir_output = ask_path_dir_output()
            set_config_path_dir_output(path_file_config, path_dir_output)
    else:
        path_dir_output = ask_path_dir_output()
        set_config_path_dir_output(path_file_config, path_dir_output)
    
    return path_dir_output

    
def define_mb_per_file(path_file_config, mb_per_file):

    if mb_per_file is not None:
        repeat_size = input(f'Compact in {mb_per_file} ' + 
                            f'MB per file? y/n ')
        print('')
        if repeat_size == 'n':
            mb_per_file = ask_mb_file()
            set_config_max_file_size(path_file_config, mb_per_file)
    else:
        mb_per_file = ask_mb_file()
        set_config_max_file_size(path_file_config, mb_per_file)
    
    return mb_per_file
    
    
def extension_to_ignore(file):

    def get_ignore_extensions():

        def get_file_ignore_extensions():
            
            folder_path = 'config'
            file_name = 'ignore_extensions.txt'
            file_path = os.path.join(folder_path, file_name)
            file = open(file_path, "r", encoding='utf_8')
            list_file = file.readlines()
            file.close()
            
            return list_file 

        list_extension = []
        file = get_file_ignore_extensions()
        for line in file:
            line_lower = line.lower()
            if line_lower.startswith('#'):
                pass
            else:
                list_extension = tuple(line_lower.split(','))
                break
            
        return list_extension

    list_ignore_extensions = get_ignore_extensions()

    if len(list_ignore_extensions) == 0:
        return False
    elif file.endswith(list_ignore_extensions):
        return True
    else:
        return False

        
def zipind(path_dir, mb_per_file=999, path_dir_output=None):
    """
    Compresses a folder into independent parts.
    Requirement: Have Winrar installed
    :input: path_dir: String. Folder path
    :input: mb_per_file: Integer. Max size of each rar file
    :input: path_dir_output: String. Folder path output
    :return: None
    """
    
    abs_path_dir = os.path.abspath(path_dir)
    abs_path_dir_mother = os.path.dirname(abs_path_dir)
    dir_name_base = os.path.basename(abs_path_dir)
    
    # if destination folder is not specified, 
    #  use the parent of the source folder
    if path_dir_output is None:
        rar_path_file_name_base = os.path.join(abs_path_dir_mother, 
                                               dir_name_base)
    else:
        rar_path_file_name_base = os.path.join(path_dir_output, dir_name_base)

    zip_file_no = 1
    bytesprocessed = 0
    bytesperfile =  mb_per_file * (1024**2)
    
    rar_path_file_name = f'{rar_path_file_name_base}_%02d.rar' % zip_file_no
    list_path_files = []

    do_create_rar_by_list = False
    do_create_rar_by_single = False    
    for root, dirs, files in os.walk(path_dir):
        for file in files:
            if extension_to_ignore(file):
                continue
            path_file = os.path.join(root, file)
            filebytes = os.path.getsize(path_file)
            
            # list_file it's about to get too big? compact before
            if bytesprocessed + filebytes > bytesperfile:
                
                do_create_rar_by_list = True
                do_create_rar_by_single = False
                if filebytes > bytesperfile:
                    do_create_rar_by_single = True
                    do_create_rar_by_list = False
                    
            if do_create_rar_by_list:
                # make dir with files in list
                print(f'Creating... {rar_path_file_name}\n')
                create_rar_file_from_list_file(rar_path_file_name, 
                                               list_path_files, mb_per_file)
                bytesprocessed = 0
                list_path_files = []
                do_create_rar_by_list = False
                
                # configure to next file rar
                zip_file_no += 1
                rar_path_file_name = \
                    f'{rar_path_file_name_base}_%02d.rar' % zip_file_no
                do_create_rar_by_single = False                

                # add focus file to another list
                print(f'Add file {path_file}') 
                list_path_files.append(path_file)
                bytesprocessed += filebytes
                
                # skip to another file
                continue
                    
            if do_create_rar_by_single:
                if len(list_path_files) > 0:
                    print(f'Creating... {rar_path_file_name}\n')
                    create_rar_file_from_list_file(rar_path_file_name, 
                                                   list_path_files, 
                                                   mb_per_file)
                    # Configure to next file rar
                    zip_file_no += 1
                    rar_path_file_name = \
                        f'{rar_path_file_name_base}_%02d.rar' % zip_file_no
                    bytesprocessed = 0
                    list_path_files = []
                    
                print(f'{file}\nThe file above is too big. ' +
                      f'Spliting...\n')
                create_rar_single_file(rar_path_file_name, path_file, 
                                       (mb_per_file))
                # configure to next file rar
                zip_file_no += 1
                rar_path_file_name = \
                    f'{rar_path_file_name_base}_%02d.rar' % zip_file_no
                do_create_rar_by_single = False
                # skip to another file
                continue
            
            # Case list not full and focus file is small
            # put file in list
            print(f'Add file {path_file}') 
            list_path_files.append(path_file)
            bytesprocessed += filebytes
    
    # in last file, if list was not empty
    if len(list_path_files) > 0:
        # make dir with files in list
        print(f'Creating... {rar_path_file_name}')
        create_rar_file_from_list_file(rar_path_file_name, 
                                       list_path_files, mb_per_file)
                                         

def create_rar_file(path_file_rar, path_origin, max_size=None):
    
    if max_size is None:
        str_max_size = ''
    else:    
        str_max_size = str(max_size)
    
    # -ep0 -> preserve folders structure
    # -ep1 -> ignore folders structure. copy only files
    subprocess.call(f'"%ProgramFiles%\\WinRAR\\Rar.exe" a -cfg- -ep0 -inul ' +
                    f'-m5 -md4m -r -s -v{str_max_size}M "{path_file_rar}" ' +
                    f'{path_origin}', shell=True)
                    

def main():
    
    path_file_config = os.path.join('config', 'config.txt')
    mb_per_file = get_config_max_file_size(path_file_config)
    path_dir_output = get_config_dir_output(path_file_config)
    ensure_folders_existence()
    
    while True:
        print('Zipind - From a folder, make a splited ZIP with INDependent ' + 
              'parts\n')
              
        # ::. Configuration
        path_dir_input = input('Paste the folder path to be compressed: ')
        path_dir_output = define_path_dir_output(path_file_config, 
                                                 path_dir_output)
        mb_per_file = define_mb_per_file(path_file_config, mb_per_file)
                
        # ::. Start the partition operation
        print(f'Compressing in parts with max size of {mb_per_file} MB...\n')
        zipind(path_dir_input, mb_per_file, path_dir_output)
        
        # ::. Repeat or Finish
        # Condition to repeat or end the script
        n_for_quit = input('\nZipind successfully applied zip generating ' + 
                           'independent parts.\n '+
                           'Apply Zipind to another folder? y/n\n')
        if n_for_quit == 'n':
            return
            
        # Clean cmd screen
        clean_cmd()

        
if __name__ == "__main__":
    main()
    