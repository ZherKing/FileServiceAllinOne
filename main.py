import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os
import ctypes
import threading

class ServiceManager:
    def __init__(self, log_text_widget):
        self.log_text_widget = log_text_widget

    def log(self, message):
        self.log_text_widget.insert(tk.END, message + "\n")
        self.log_text_widget.see(tk.END)

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

    # FTP部分
    def enable_ftp_feature(self):
        self.log("正在启用IIS和FTP服务功能...")
        self.run_command_threaded("dism /online /enable-feature /featurename:IIS-WebServerRole /all")
        self.run_command_threaded("dism /online /enable-feature /featurename:IIS-FTPServer /all")
        self.log("IIS和FTP服务功能已启用")

    def disable_ftp_feature(self):
        self.log("正在禁用IIS和FTP服务功能...")
        self.run_command_threaded("dism /online /disable-feature /featurename:IIS-WebServerRole")
        self.run_command_threaded("dism /online /disable-feature /featurename:IIS-FTPServer")
        self.log("IIS和FTP服务功能已禁用")

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
        self.root.title("FileServiceAllinOne by ZherKing")

        # 创建菜单
        menubar = tk.Menu(root)
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="关于", command=self.show_about)
        menubar.add_cascade(label="帮助", menu=helpmenu)
        root.config(menu=menubar)

        self.title_label = tk.Label(root, text="FileServiceAllinOne", font=("Helvetica", 16))
        self.title_label.pack(pady=10)

        self.log_text = tk.Text(root, height=10, state=tk.NORMAL)
        self.log_text.pack(pady=10)

        self.manager = ServiceManager(self.log_text)

        # FTP部分
        self.ftp_label = tk.Label(root, text="FTP服务管理", font=("Helvetica", 14))
        self.ftp_label.pack(pady=5)

        self.enable_ftp_feature_button = tk.Button(root, text="启用FTP服务", command=self.manager.enable_ftp_feature)
        self.enable_ftp_feature_button.pack(pady=5)

        self.disable_ftp_feature_button = tk.Button(root, text="禁用FTP服务", command=self.manager.disable_ftp_feature)
        self.disable_ftp_feature_button.pack(pady=5)

        self.start_iis_button = tk.Button(root, text="启动 IIS", command=self.manager.start_iis)
        self.start_iis_button.pack(pady=5)

        self.ftp_start_button = tk.Button(root, text="启动 FTP", command=self.manager.start_ftp)
        self.ftp_start_button.pack(pady=5)

        self.ftp_stop_button = tk.Button(root, text="停止 FTP", command=self.manager.stop_ftp)
        self.ftp_stop_button.pack(pady=5)

        # SMB部分
        self.smb_label = tk.Label(root, text="SMB服务管理", font=("Helvetica", 14))
        self.smb_label.pack(pady=5)

        self.smb_start_button = tk.Button(root, text="启动 SMB 服务", command=self.manager.start_smb)
        self.smb_start_button.pack(pady=5)

        self.smb_stop_button = tk.Button(root, text="停用 SMB 服务", command=self.manager.stop_smb)
        self.smb_stop_button.pack(pady=5)

        # NFS部分
        self.nfs_label = tk.Label(root, text="NFS服务管理", font=("Helvetica", 14))
        self.nfs_label.pack(pady=5)

        self.nfs_start_button = tk.Button(root, text="启动 NFS 服务", command=self.manager.start_nfs)
        self.nfs_start_button.pack(pady=5)

        self.nfs_stop_button = tk.Button(root, text="停用 NFS 服务", command=self.manager.stop_nfs)
        self.nfs_stop_button.pack(pady=5)

    def show_about(self):
        messagebox.showinfo("关于", "作者: ZherKing\n版本: 1.0\n日期: 2025-02-24\n\n感谢测试人员：\n@初雨(blog.bronya.space)")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if __name__ == "__main__":
    if not is_admin():
        # 重新启动并请求管理员权限
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    else:
        root = tk.Tk()
        app = App(root)
        root.mainloop()