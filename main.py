import tkinter as tk
from tkinter import messagebox
from ttkthemes import ThemedTk
from tkinter import ttk
import subprocess
import sys
import os
import ctypes
import threading


class ServiceManager:
    def __init__(self, log_text_widget):
        self.log_text_widget = log_text_widget
        self.log_welcome_message()

    def log(self, message):
        self.log_text_widget.insert(tk.END, message + "\n")
        self.log_text_widget.see(tk.END)

    def log_welcome_message(self):
        welcome_message = "欢迎使用 FileServiceAllinOne! 作者：ZherKing\n项目链接：https://github.com/ZherKing/FileServiceAllinOne"
        self.log(welcome_message)

    def run_command(self, command):
        try:
            completed_process = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            self.log(completed_process.stdout)
            if completed_process.returncode != 0:
                raise subprocess.CalledProcessError(completed_process.returncode, command)
        except subprocess.CalledProcessError as e:
            self.log(f"执行命令失败: {command}\n{e.stderr}")
            messagebox.showerror("错误", f"执行命令失败: {command}")

    def run_command_threaded(self, command):
        thread = threading.Thread(target=self.run_command, args=(command,))
        thread.start()

    def check_service_status(self):
        try:
            completed_process = subprocess.run(
                "dism /online /Get-Features /English",
                check=True,
                capture_output=True,
                text=True,
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            features = completed_process.stdout

            ftp_status = "IIS-FTPServer" in features and "Enabled" in features.split("IIS-FTPServer")[1].split(" ")[2]
            smb_status = "SMB1Protocol" in features and "Enabled" in features.split("SMB1Protocol")[1].split(" ")[2]
            nfs_status = "ServicesForNFS-Server" in features and "Enabled" in \
                         features.split("ServicesForNFS-Server")[1].split(" ")[2]

            self.log(f"FTP服务状态: {'启用' if ftp_status else '禁用'}")
            self.log(f"SMB服务状态: {'启用' if smb_status else '禁用'}")
            self.log(f"NFS服务状态: {'启用' if nfs_status else '禁用'}")
        except subprocess.CalledProcessError as e:
            self.log(f"检查服务状态失败: {e}")
            messagebox.showerror("错误", f"检查服务状态失败: {e}")

    # FTP部分
    def enable_ftp_feature(self):
        self.log("正在启用IIS和FTP服务功能...")
        self.run_command_threaded("dism /online /enable-feature /featurename:IIS-WebServerRole /all")
        self.run_command_threaded("dism /online /enable-feature /featurename:IIS-FTPServer /all")
        self.log("IIS和FTP服务功能已启用")

    def start_ftp(self):
        self.log("正在启动FTP服务器...")
        self.run_command_threaded("net start ftpsvc")
        self.log("FTP服务器已启动")
        messagebox.showinfo("信息", "FTP服务器已启动")

    def stop_ftp(self):
        self.log("正在停止FTP服务器...")
        self.run_command_threaded("net stop ftpsvc")
        self.log("FTP服务器已停止")
        messagebox.showinfo("信息", "FTP服务器已停止")

    def start_iis(self):
        self.log("正在启动IIS...")
        self.run_command_threaded("start inetmgr")
        self.log("IIS已启动")
        messagebox.showinfo("信息", "IIS已启动")

    # SMB部分
    def start_smb(self):
        self.log("正在启用 SMB 服务...")
        self.run_command_threaded("dism /online /enable-feature /featurename:SMB1Protocol /all")
        self.log("SMB 服务已启动")
        messagebox.showinfo("信息", "SMB服务已经启用（可能需要重启）")

    def stop_smb(self):
        self.log("正在停止SMB服务器...")
        self.run_command_threaded("dism /online /disable-feature /featurename:SMB1Protocol")
        self.log("SMB服务器已停止")
        messagebox.showinfo("信息", "SMB服务器已停止")

    # NFS部分
    def start_nfs(self):
        self.log("正在启用 NFS 服务...")
        self.run_command_threaded("dism /online /enable-feature /featurename:ServicesForNFS-Server /all")
        self.log("NFS 服务已启用")
        messagebox.showinfo("信息", "NFS 服务已启用")

    def stop_nfs(self):
        self.log("正在停止 NFS 服务...")
        self.run_command_threaded("dism /online /disable-feature /featurename:ServicesForNFS-Server")
        self.log("NFS 服务器已停止")
        messagebox.showinfo("信息", "NFS 服务已停止")


class App:
    def __init__(self, root):
        self.root = root
        self.root.title(f"FileServiceAllinOne {version}")

        self.log_text = tk.Text(root, height=10, state=tk.NORMAL, font=("Microsoft YaHei", 10))
        self.log_text.pack(pady=10)

        self.manager = ServiceManager(self.log_text)

        # 创建菜单
        menubar = tk.Menu(root)

        # 帮助菜单
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="关于", command=self.show_about)
        menubar.add_cascade(label="帮助", menu=helpmenu)

        # 检查菜单
        checkmenu = tk.Menu(menubar, tearoff=0)
        checkmenu.add_command(label="检查服务状态", command=self.manager.check_service_status)
        menubar.add_cascade(label="检查", menu=checkmenu)

        # 主题菜单
        thememenu = tk.Menu(menubar, tearoff=0)
        themes = ['breeze', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative']
        for theme in themes:
            thememenu.add_command(label=theme, command=lambda t=theme: self.change_theme(t))
        menubar.add_cascade(label="主题", menu=thememenu)

        root.config(menu=menubar)

        self.title_label = tk.Label(root, text="FileServiceAllinOne", font=("Microsoft YaHei", 16))
        self.title_label.pack(pady=10)

        # FTP部分
        self.ftp_frame = ttk.Frame(root)
        self.ftp_frame.pack(pady=10, fill='x')

        self.ftp_label = tk.Label(self.ftp_frame, text="FTP服务管理", font=("Microsoft YaHei", 14))
        self.ftp_label.grid(row=0, columnspan=2, pady=5)

        self.enable_ftp_feature_button = ttk.Button(self.ftp_frame, text="启用FTP服务",
                                                    command=self.manager.enable_ftp_feature)
        self.enable_ftp_feature_button.grid(row=1, column=0, padx=5)

        self.start_iis_button = ttk.Button(self.ftp_frame, text="启动 IIS", command=self.manager.start_iis)
        self.start_iis_button.grid(row=1, column=1, padx=5)

        self.ftp_start_button = ttk.Button(self.ftp_frame, text="启动 FTP", command=self.manager.start_ftp)
        self.ftp_start_button.grid(row=2, column=0, padx=5)

        self.ftp_stop_button = ttk.Button(self.ftp_frame, text="停止 FTP", command=self.manager.stop_ftp)
        self.ftp_stop_button.grid(row=2, column=1, padx=5)

        # SMB部分
        self.smb_frame = ttk.Frame(root)
        self.smb_frame.pack(pady=10, fill='x')

        self.smb_label = tk.Label(self.smb_frame, text="SMB服务管理", font=("Microsoft YaHei", 14))
        self.smb_label.grid(row=0, columnspan=2, pady=5)

        self.smb_start_button = ttk.Button(self.smb_frame, text="启动 SMB 服务", command=self.manager.start_smb)
        self.smb_start_button.grid(row=1, column=0, padx=5)

        self.smb_stop_button = ttk.Button(self.smb_frame, text="停用 SMB 服务", command=self.manager.stop_smb)
        self.smb_stop_button.grid(row=1, column=1, padx=5)

        # NFS部分
        self.nfs_frame = ttk.Frame(root)
        self.nfs_frame.pack(pady=10, fill='x')

        self.nfs_label = tk.Label(self.nfs_frame, text="NFS服务管理", font=("Microsoft YaHei", 14))
        self.nfs_label.grid(row=0, columnspan=2, pady=5)

        self.nfs_start_button = ttk.Button(self.nfs_frame, text="启动 NFS 服务", command=self.manager.start_nfs)
        self.nfs_start_button.grid(row=1, column=0, padx=5)

        self.nfs_stop_button = ttk.Button(self.nfs_frame, text="停用 NFS 服务", command=self.manager.stop_nfs)
        self.nfs_stop_button.grid(row=1, column=1, padx=5)

    def change_theme(self, theme):
        self.root.set_theme(theme)

    def show_about(self):
        messagebox.showinfo(f"关于",
                            f"作者: ZherKing\n版本: {version}\n日期: 2025-02-28\n\n感谢测试人员：\n@初雨(blog.bronya.space)")


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


if __name__ == "__main__":
    version = 2.0
    if not is_admin():
        # 重新启动并请求管理员权限
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    else:
        root = ThemedTk(theme="arc")  # 默认主题为 'arc'
        app = App(root)
        root.mainloop()