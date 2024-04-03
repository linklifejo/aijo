import csv
import os
import shutil
import keyboard
import threading
# Running the sample program
class Hook(threading.Thread):
    def __init__(self):
        super(Hook, self).__init__()  # 부모 클래스 __init__ 실행
        self.daemon = True  # 데몬 쓰레드로 설정
        self.event = False  # f4가 눌리면 event 발생
        self.my_xy = []     # 좌표 저장 리스트
        keyboard.unhook_all()  # 후킹 초기화
        keyboard.add_hotkey('f4', print, args=['\n종료합니다'])  # f4가 눌리면 print 실행
        keyboard.add_hotkey('f2', print, args=['\n[f2키 실행] 금일 주식거래내역 입니다.'])  # f2가 눌리면 print 실행
        
    def run(self):  # run 메소드 재정의
        while True:
            key = keyboard.read_hotkey(suppress=False)  # hotkey를 계속 읽음
            if key == 'f4':  # f4 받은 경우
                self.event = 'f4'  # event 클래스 변수를 True로 설정
                break  # 반복문 탈출
                # # print("\n", self.my_xy)

                # with open(r"config.txt", "w") as f:
                #     for i in self.my_xy:
                #         f.write("{},{}\n".format(i[0], i[1]))
                
            
            elif key == 'f2':
                self.event = 'f2'  # event 클래스 변수를 True로 설정
                # position = pyautogui.position()
                # self.my_xy.append((position.x, position.y))

# import pyautogui
def create_directory(directory_name):
    """Create a new directory."""
    try:
        os.makedirs(directory_name)
    except FileExistsError:
        print(f"Directory '{directory_name}' already exists")

def delete_directory(directory_name):
    """Delete a directory."""
    try:
        shutil.rmtree(directory_name)
    except FileNotFoundError:
        print(f"Directory '{directory_name}' does not exist")

def create_csv(file_name):
    """Create a new CSV file."""
    try:
        
        with open(file_name, mode='w', newline='') as file:
            writer = csv.writer(file)
    except:
        print('error')
def write_csv(file_name, data):
    try:
        """Write data to a CSV file."""
        with open(file_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)
    except:
        print('write error')
def read_csv(file_name):
    try:
        f = []
        """Read and print the content of a CSV file."""
        with open(file_name, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                f.append(row)
            return f
    except:   
        print('read error')         
    return None            


      
def delete_csv(file_name):
    """Delete a CSV file."""
    if os.path.exists(file_name):
        os.remove(file_name)
    else:
        print("The file does not exist")
def write(check='token', *args):
    dir_name = 'database'
    if not os.path.exists(dir_name):
        create_directory(dir_name)
    if check == 'token':
        file_name = 'token.csv'
    else:
        file_name = 'trade.csv'
    full_name = os.path.join(dir_name, file_name)
    outer = []
    inner = []
    for i in args:
        inner.append(i)
    outer.append(inner)
    write_csv(full_name,outer)

def read(check='token'):
    dir_name = 'database'
    if not os.path.exists(dir_name):
        create_directory(dir_name)
    if check == 'token':
        file_name = 'token.csv'
    else:
        file_name = 'trade.csv'
    full_name = os.path.join(dir_name, file_name)
    if os.path.exists(full_name):
        data = read_csv(full_name)
    return data

def database():
    # Create a directory
    dir_name = 'database'
    create_directory(dir_name)

    # Create a CSV file within the directory
    csv_file_name = os.path.join(dir_name, 'trade.csv')
    create_csv(csv_file_name)
    return csv_file_name
    # Write to the CSV file
    # data = [['John Doe', 30, 'New York'], ['Jane Doe', 28, 'Los Angeles']]
    # write_csv(csv_file_name, data)

    # read_csv(csv_file_name)
    # delete_csv(csv_file_name)
    # delete_directory(dir_name)
def istoken():
    dir_name = 'database'
    if not os.path.exists(dir_name):
        create_directory(dir_name)
    full_name = os.path.join(dir_name, 'token.csv')
    if os.path.exists(full_name):
        return True
    else:
        create_csv(full_name)
        return False
    

