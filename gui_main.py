import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import os
import sys
import json
from urllib.parse import urljoin
from main import HtmlToMdPdfConverter
import threading


class CSDNPDFerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CSDN PDFer - 博客转PDF工具")
        self.root.geometry("700x650")

        # 配置文件路径
        self.config_file = os.path.join(os.path.expanduser("~"), "csdn_pdfer_config.json")

        # 加载配置
        self.config = self.load_config()

        # wkhtmltopdf 路径配置
        self.wkhtmltopdf_path = self.find_wkhtmltopdf()

        self.create_widgets()

    def find_wkhtmltopdf(self):
        """尝试查找wkhtmltopdf的安装位置，优先查找exe同目录下"""
        # 获取程序运行目录（无论是开发环境还是打包后的exe）
        if getattr(sys, 'frozen', False):
            # 打包后的exe，获取exe所在目录
            base_dir = os.path.dirname(sys.executable)
        else:
            # 开发环境，获取脚本所在目录
            base_dir = os.path.dirname(os.path.abspath(__file__))

        # 优先查找exe同目录下的wkhtmltopdf
        exe_relative_path = os.path.join(base_dir, "wkhtmltopdf.exe")
        if os.path.exists(exe_relative_path):
            return exe_relative_path

        # 如果同目录下没有，查找其他常见位置
        possible_paths = [
            r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
            r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe",
            os.path.join(base_dir, "wkhtmltopdf", "wkhtmltopdf.exe"),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None

    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
        return {"last_output_path": os.path.expanduser("~")}

    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置文件失败: {e}")

    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        row = 0

        # 标题
        title_label = ttk.Label(main_frame, text="CSDN PDFer", font=("Microsoft YaHei", 16, "bold"))
        title_label.grid(row=row, column=0, columnspan=3, pady=(0, 20))
        row += 1

        # URL 输入
        ttk.Label(main_frame, text="CSDN文章URL:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.url_entry = ttk.Entry(main_frame, width=50)
        self.url_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        row += 1

        # 输出路径
        ttk.Label(main_frame, text="输出PDF路径:").grid(row=row, column=0, sticky=tk.W, pady=5)

        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

        self.output_path_entry = ttk.Entry(path_frame, width=40)
        self.output_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        browse_button = ttk.Button(path_frame, text="浏览...", command=self.browse_output_path)
        browse_button.pack(side=tk.LEFT, padx=5)
        row += 1

        # 设置默认输出路径
        default_output = self.config.get("last_output_path", os.path.expanduser("~"))
        self.output_path_entry.insert(0, default_output)

        # 文件名前缀
        ttk.Label(main_frame, text="文件名前缀:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.filename_entry = ttk.Entry(main_frame, width=50)
        self.filename_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        self.filename_entry.insert(0, "csdn_article")
        row += 1

        # wkhtmltopdf 路径状态
        if self.wkhtmltopdf_path:
            status_text = f"wkhtmltopdf: 已找到"
            status_color = "green"
        else:
            status_text = "wkhtmltopdf: 未找到，请手动安装"
            status_color = "red"

        status_label = ttk.Label(main_frame, text=status_text, foreground=status_color)
        status_label.grid(row=row, column=0, columnspan=3, pady=5)
        row += 1

        # 开始按钮
        self.start_button = ttk.Button(main_frame, text="开始转换", command=self.start_conversion)
        self.start_button.grid(row=row, column=0, columnspan=3, pady=20)
        row += 1

        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        row += 1

        # 日志输出区域
        ttk.Label(main_frame, text="转换日志:").grid(row=row, column=0, sticky=tk.W, pady=(10, 5))
        row += 1

        self.log_text = scrolledtext.ScrolledText(main_frame, height=15, width=70, state=tk.DISABLED)
        self.log_text.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        # 配置最后一行的权重
        main_frame.rowconfigure(row, weight=1)

    def browse_output_path(self):
        """浏览输出路径"""
        current_path = self.output_path_entry.get()
        if not current_path or not os.path.exists(current_path):
            current_path = os.path.expanduser("~")

        path = filedialog.askdirectory(initialdir=current_path, title="选择输出目录")
        if path:
            self.output_path_entry.delete(0, tk.END)
            self.output_path_entry.insert(0, path)

    def log(self, message):
        """添加日志"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()

    def start_conversion(self):
        """开始转换"""
        url = self.url_entry.get().strip()
        output_path = self.output_path_entry.get().strip()
        filename_prefix = self.filename_entry.get().strip()

        # 验证输入
        if not url:
            messagebox.showerror("错误", "请输入CSDN文章URL")
            return

        if not output_path:
            messagebox.showerror("错误", "请选择输出路径")
            return

        if not filename_prefix:
            messagebox.showerror("错误", "请输入文件名前缀")
            return

        # 保存配置
        self.config["last_output_path"] = output_path
        self.save_config()

        # 禁用开始按钮
        self.start_button.config(state=tk.DISABLED)
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

        # 在新线程中执行转换
        thread = threading.Thread(target=self.convert_article, args=(url, output_path, filename_prefix))
        thread.daemon = True
        thread.start()

    def convert_article(self, url, output_path, filename_prefix):
        """转换文章（在新线程中运行）"""
        try:
            self.root.after(0, lambda: self.progress.start())
            self.root.after(0, lambda: self.log(f"开始处理: {url}"))

            # 获取HTML内容
            import requests
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            self.root.after(0, lambda: self.log("正在下载HTML内容..."))
            response = requests.get(url, headers=headers, timeout=15)

            if response.status_code != 200:
                raise Exception(f"无法访问URL: HTTP {response.status_code}")

            html_content = response.text
            self.root.after(0, lambda: self.log("HTML内容下载完成"))

            # 创建转换器
            self.root.after(0, lambda: self.log("初始化转换器..."))
            converter = HtmlToMdPdfConverter(output_dir=output_path, wkhtmltopdf_path=self.wkhtmltopdf_path)

            # 执行转换
            self.root.after(0, lambda: self.log("开始转换..."))

            # 在主线程中调用转换器（因为需要更新GUI）
            def do_convert():
                try:
                    converter.process(
                        html_content=html_content,
                        target_div_selector="#content_views",
                        output_name=filename_prefix,
                        base_url=url,
                        keep_temp_files=False  # 不保留临时文件
                    )
                    self.root.after(0, lambda: self.log("="*50))
                    self.root.after(0, lambda: self.log("转换完成！临时文件已清理。"))
                    self.root.after(0, lambda: self.log(f"PDF文件: {os.path.join(output_path, filename_prefix + '.pdf')}"))
                    self.root.after(0, lambda: self.log("="*50))
                    self.root.after(0, lambda: messagebox.showinfo("成功", f"转换完成！\n\nPDF已保存到:\n{os.path.join(output_path, filename_prefix + '.pdf')}"))
                except Exception as e:
                    self.root.after(0, lambda: self.log(f"错误: {str(e)}"))
                    self.root.after(0, lambda: messagebox.showerror("错误", f"转换失败:\n{str(e)}"))
                finally:
                    self.root.after(0, lambda: self.progress.stop())
                    self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))

            do_convert()

        except Exception as e:
            self.root.after(0, lambda: self.log(f"错误: {str(e)}"))
            self.root.after(0, lambda: messagebox.showerror("错误", f"下载失败:\n{str(e)}"))
            self.root.after(0, lambda: self.progress.stop())
            self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))


def main():
    root = tk.Tk()
    app = CSDNPDFerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
