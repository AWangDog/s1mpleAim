from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtUiTools import QUiLoader

# uiLoader 实例化
uiLoader = QUiLoader()

# 加载 login 窗口
class login:
    def __init__(self):
        # 加载 login 窗口
        self.ui = QUiLoader().load('ui\\login.ui')
        self.ui.UID_Text.setPlainText(self.get_UID().hexdigest())
        self.ui.UID_Button.clicked.connect(self.copy_UID)
        self.ui.Key_Button.clicked.connect(self.login)
        self.ui.Try_Button.clicked.connect(self.trial_period)
        self.ui.setFixedSize(389, 134)
        if self.try_day() == False:
            self.ui.Try_Label.setText('试用期已过, 请联系管理员获取key')
            self.ui.Try_Button.setEnabled(False)
        else:
            self.ui.Try_Label.setText(f'试用期还有{self.try_day()}天')
    
    from functools import lru_cache
    # 获取登录列表
    def get_login_list(self):
        import requests
        import urllib3
        import warnings
        url = "https://raw.kkgithub.com/AWangDog/s1mpleAim/main/Login.json"
        warnings.filterwarnings("ignore")
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.get(url, verify=False)
        return response.json()

    # 生成 UID
    def get_UID(self):
        import uuid, platform, wmi, hashlib
        # 获取 MAC 地址
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0,2*6,2)][::-1])
        # 获取 CPU 序列号
        cpu_id = platform.processor()
        # 获取主板 smBIOS UUID
        c = wmi.WMI()
        for s in c.Win32_ComputerSystemProduct():
            smBIOS_UUID = s.UUID
        # SHA256 加密
        UID = hashlib.sha256((smBIOS_UUID + cpu_id + mac).encode('utf-8'))
        return UID
    
    # 复制 UID 到剪贴板
    def copy_UID(self):
        import pyperclip
        pyperclip.copy(self.get_UID().hexdigest())
    
    # 登录
    def login(self):
        from datetime import datetime
        matching_items = [item for item in self.get_login_list() if item.get('UID') == self.get_UID().hexdigest() and item.get('Key') == self.ui.KeyInput.text()]
        if matching_items:
            time = (datetime.strptime(matching_items[0].get('time'), "%Y/%m/%d_%H:%M:%S") - datetime.now()).days
            if time < 0:
                QMessageBox.about(self.ui,'登录失败',f'登录失败, Key已过期, 请找管理员续费')
            else:
                QMessageBox.about(self.ui,'登录成功',f'登录成功, Key还有{time}天到期')
        else:
            QMessageBox.about(self.ui,'登录失败',f'登录失败, 请检查Key是否正确')

    # 试用期剩余天数
    def try_day(self):
        from cryptography.fernet import Fernet
        import datetime, os, base64
        file_path = os.path.join(os.environ['APPDATA'], 's1mpleAim', 'trialPeriod.txt')
        encoded_key = base64.urlsafe_b64encode(self.get_UID().digest())
        cipher_suite = Fernet(encoded_key)
        now_time = datetime.datetime.now()
        trial_period_time = cipher_suite.encrypt((datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S").encode('utf-8'))
        if os.path.exists(file_path):
            with open(file_path, 'rb') as file:
                trial_period_time = file.read()
        else:
            if not os.path.exists(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))
            with open(file_path, 'wb') as file:
                file.write(trial_period_time)
        file.close()
        trial_period_time = cipher_suite.decrypt(trial_period_time).decode('utf-8')
        trialPeriod = datetime.datetime.strptime(trial_period_time, "%Y-%m-%d %H:%M:%S")
        time = (trialPeriod - now_time).days
        if now_time > trialPeriod:
            return False
        else:
            return time
    
    # 试用
    def trial_period(self):
        if self.try_day() == False:
            self.ui.Try_Label.setText('试用期已过, 请联系管理员获取key')
            self.ui.Try_Button.setEnabled(False)
            QMessageBox.about(self.ui,'登录失败',f'登录失败, 试用期已过, 请联系管理员获取key')
        else:
            self.ui.Try_Label.setText(f'试用期还有{self.try_day()}天')
            QMessageBox.about(self.ui,'登录成功',f'登录成功，试用期还有{self.try_day()}天')

app = QApplication([])
login = login()
login.ui.show()
app.exec()

