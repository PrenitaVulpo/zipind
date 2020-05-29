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

   
def save_txt(str_content, str_name):

    text_file = open(f"{str_name}.txt", "w")
    text_file.write(str_content)
    text_file.close()

        
def create_rar_single_file(path_file_rar, path_origin, max_size=None):

    # file_size_bytes = os.path.getsize(path_origin)
    # file_size_mb = max_size / (1024**2)
    create_rar_file(path_file_rar, '"' + path_origin + '"', 
                    max_size=max_size)
        
    
def create_rar_file_from_list_file(path_file_rar, list_files, max_size=None):
    
    # file_size_mb = max_size / (1024**2)
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
                                       'file_size').strip('\n').strip("'")
    max_file_size = int(max_file_size)
    return max_file_size

    
def get_config_dir_output(path_file_config):

    dir_output = handle_config_file(path_file_config, 
                                    'dir_output').strip('\n').strip("'")
    # TODO test dir
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
                                         
                                         
def handle_config_file(path_file, variable, set_value=None):

    config_file = open(path_file, 'r+')
    content_lines = []

    for line in config_file:
            if f'{variable}=' in line:
                line_components = line.split('=')
                str_value = line_components[1]
                
                # update value or show value?
                if set_value is not None:                
                    updated_line = f"{variable}='{set_value}'\n"
                    content_lines.append(updated_line)
                else:
                    config_file.close()
                    return str_value
            else:
                content_lines.append(line)

    config_file.seek(0)
    config_file.truncate()
    config_file.writelines(content_lines)
    config_file.close()

    
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
