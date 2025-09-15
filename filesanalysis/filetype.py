import os
from os.path import join, getsize
def get_file_type(file_path):
    """Get file extension from file path"""
    if '.' not in os.path.basename(file_path):
        return "no_extension"
    file_type = file_path.split('.')[-1].lower()
    return file_type

def get_file_size(file_path):
    for root, dirs, files in os.walk(file_path):
        print(root, "consumes", end=" ")
        print(sum(getsize(join(root, name))/1024 for name in files), end=" ")
        print("kb in", len(files), "non-directory files")


def collect_file_types_recursive(directory_path):
    """
    Recursively collect all file format types in a directory
    
    Args:
        directory_path (str): Path to the directory to analyze
        
    Returns:
        set: Set of all file extensions found
    """
    file_type_set = dict()
    
    try:
        for root, dirs, files in os.walk(directory_path):
            print(files)
            for file in files:
                file_type = get_file_type(file)
                file_type_set[file_type] = file_type_set.get(file_type, 0) + 1
    except PermissionError as e:
        print(f"Permission denied accessing: {e}")
    except FileNotFoundError as e:
        print(f"Directory not found: {e}")
    except Exception as e:
        print(f"Error occurred: {e}")
    
    return file_type_set

if __name__ == "__main__":
    filepath = "/Users/yjli/QUTIT/semester4/ifn712/datacollect/from_orefox"
    file_type_set = collect_file_types_recursive(filepath)
         
    print(sorted(file_type_set.items(), key=lambda x: x[1], reverse=True))
    # get_file_size('/Users/yjli/QUTIT/semester4/ifn712/datacollect/from_orefox/Mt Wheeler EPMA')
 