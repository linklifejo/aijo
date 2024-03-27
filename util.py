import subprocess
class InetError(Exception):
    def __init__(self, message="Something went wrong"):
        super().__init__(message)

def my_function():
    raise InetError("A specific error message")

def clear():
    subprocess.run('cls', shell=True)
def kill_exe(program='chrome.exe'):
    try:
        subprocess.run(['taskkill', '/F', '/IM', program], check=True)
        print("Successfully terminated.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
        return False

def iswindow():
    if subprocess.os.name == 'nt':
        return True
    return False        
def run_exe(command):
    if iswindow:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return True
        return False
    
def main():
    try:
        my_function()
    except InetError as e:
        print(f"Caught an error: {e}")  
if __name__ == "__main__":
    main()

