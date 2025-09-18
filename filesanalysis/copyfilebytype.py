 
import os
import shutil

def copyfile_to_new_path(filetype, filepath, new_path):
    count = 0
    os.makedirs(new_path, exist_ok=True)
    for root, dirs, files in os.walk(filepath):
        for file in files:
            if file.endswith(filetype):
                shutil.copy(os.path.join(root, file), new_path)
                count += 1
    print(f"Copied {count} files")

if __name__ == "__main__":
    typename = "json"
    filetype = "." + typename
    filepath = "/Users/yjli/QUTIT/semester4/ifn712/datacollect/from_orefox"
    new_path = "/Users/yjli/QUTIT/semester4/ifn712/datacollect/databytype/" + typename
    copyfile_to_new_path(filetype, filepath, new_path)
