import os
import requests
import hashlib
from bs4 import BeautifulSoup
from markdownify import markdownify
import markdown
import pdfkit
from urllib.parse import urljoin

class HtmlToMdPdfConverter:
    def __init__(self, output_dir="output", wkhtmltopdf_path=None):
        """
        :param output_dir: 输出文件的文件夹
        :param wkhtmltopdf_path: 如果 wkhtmltopdf 没有在环境变量中，需要指定其具体路径 (Windows 常用)
        """
        self.output_dir = output_dir
        self.images_dir = os.path.join(output_dir, "images")
        
        # 创建目录
        os.makedirs(self.images_dir, exist_ok=True)
        
        # PDFKit 配置
        self.pdf_config = None
        if wkhtmltopdf_path:
            self.pdf_config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

    def download_image(self, img_url):
        """
        下载图片并返回本地绝对路径
        """
        try:
            # 给图片生成一个基于URL的唯一文件名，防止文件名冲突或特殊字符
            img_hash = hashlib.md5(img_url.encode('utf-8')).hexdigest()
            # 简单假设后缀为jpg，实际情况可以从Header Content-Type获取
            filename = f"{img_hash}.jpg" 
            file_path = os.path.join(self.images_dir, filename)
            
            # 如果文件已存在，直接返回
            if os.path.exists(file_path):
                return os.path.abspath(file_path)

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(img_url, headers=headers, stream=True, timeout=10)
            
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                return os.path.abspath(file_path)
            else:
                print(f"下载失败: {img_url} (Status: {response.status_code})")
                return None
        except Exception as e:
            print(f"下载出错: {img_url} ({e})")
            return None

    def process(self, html_content, target_div_selector, output_name, base_url="", keep_temp_files=False):
        """
        执行转换主逻辑
        :param html_content: 原始 HTML 字符串
        :param target_div_selector: CSS 选择器 (例如 'div#content' 或 '.article-body')
        :param output_name: 输出文件的前缀名
        :param base_url: 如果图片链接是相对路径，需要提供 base_url
        :param keep_temp_files: 是否保留临时文件（md文件和images文件夹），默认False删除
        """

        # 调试：打印所有参数
        print("=" * 60)
        print("🔍 process 方法参数:")
        print(f"  html_content 类型: {type(html_content)}, 长度: {len(html_content) if html_content else 0}")
        print(f"  target_div_selector: {repr(target_div_selector)}")
        print(f"  output_name: {repr(output_name)}")
        print(f"  base_url: {repr(base_url)}")
        print(f"  keep_temp_files: {keep_temp_files}")
        print(f"  self.output_dir: {repr(self.output_dir)}")
        print(f"  self.images_dir: {repr(self.images_dir)}")
        print("=" * 60)

        # 1. 解析 HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        target_div = soup.select_one(target_div_selector)

        if not target_div:
            raise ValueError(f"未找到指定的 DIV 元素: {target_div_selector}")

        print(f"✅ 成功找到目标 DIV，内容长度: {len(str(target_div))} 字符")

        # 2. 处理图片
        images = target_div.find_all('img')
        print(f"发现 {len(images)} 张图片，开始处理...")
        
        for img in images:
            original_src = img.get('src')
            if not original_src:
                continue
                
            # 处理相对路径
            full_url = urljoin(base_url, original_src)
            
            local_path = self.download_image(full_url)
            
            if local_path:
                # 在Markdown中使用相对路径（相对于markdown文件）
                # 在HTML中使用绝对路径（pdfkit需要）
                relative_path = os.path.relpath(local_path, self.output_dir)
                img['src'] = local_path  # 先替换为绝对路径用于pdfkit
                img['data-md-src'] = relative_path  # 保存相对路径信息
                print(f"已替换: {original_src} -> {local_path} (相对: {relative_path})")

        # 3. 转换为 Markdown
        # markdownify 会读取修改后的 soup (此时 src 已经是本地路径了)
        md_content = markdownify(str(target_div), heading_style="ATX")

        # 4. 将Markdown中的图片路径改为相对路径
        # 查找所有图片引用并替换为相对路径
        import re
        def replace_absolute_with_relative(match):
            abs_path = match.group(1)
            try:
                rel_path = os.path.relpath(abs_path, self.output_dir)
                return f']({rel_path})'
            except ValueError:
                # 在不同驱动器上时，保持绝对路径
                return match.group(0)

        # 匹配 ](绝对路径) 格式
        md_content = re.sub(r'\]\((file://)?[A-Za-z]:[^\)]+\)', replace_absolute_with_relative, md_content)

        md_file_path = os.path.join(self.output_dir, f"{output_name}.md")
        with open(md_file_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        print(f"Markdown 已生成: {md_file_path}")

        # 5. 生成 PDF
        # 为了生成的 PDF 好看，我们需要先把 Markdown 转回 HTML (加上样式)，再转 PDF
        # 这里也可以直接用修改后的 target_div HTML，但转一圈 MD 可以保证排版是"Markdown风格"的

        # 将Markdown中的相对路径转回绝对路径用于PDF生成
        md_for_pdf = md_content

        # 检查 self.output_dir 是否有效
        if self.output_dir is None:
            raise ValueError("self.output_dir 是 None！无法继续处理。")

        def replace_relative_with_absolute(match):
            rel_path = match.group(1)
            if rel_path is None:
                print("  ⚠️  WARNING: rel_path is None!")
                return match.group(0)
            abs_path = os.path.abspath(os.path.join(self.output_dir, rel_path))
            return f']({abs_path})'

        print("🔄 转换相对路径为绝对路径...")
        md_for_pdf = re.sub(r'\]\((?!http)([^\)]+)\)', replace_relative_with_absolute, md_for_pdf)

        print("🔄 转换 Markdown 为 HTML...")
        html_for_pdf = markdown.markdown(md_for_pdf, extensions=['extra'])
        
        # 添加一些基本的 CSS 让 PDF 好看点
        styled_html = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: "Microsoft YaHei", sans-serif; margin: 20px; }}
                img {{ max-width: 100%; height: auto; display: block; margin: 10px 0; }}
                pre {{ background: #f4f4f4; padding: 10px; border-radius: 5px; }}
                code {{ background: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
                blockquote {{ border-left: 4px solid #ddd; padding-left: 10px; color: #666; }}
            </style>
        </head>
        <body>
            {html_for_pdf}
        </body>
        </html>
        """
        
        pdf_file_path = os.path.join(self.output_dir, f"{output_name}.pdf")
        print(f"📄 PDF 文件路径: {pdf_file_path}")
        print(f"📄 PDF 配置: {self.pdf_config}")

        options = {
            'enable-local-file-access': None,  # 允许访问本地图片
            'encoding': 'UTF-8'
        }

        try:
            print("🖨️  开始生成 PDF...")
            pdfkit.from_string(styled_html, pdf_file_path, configuration=self.pdf_config, options=options)
            print(f"✅ PDF 已生成: {pdf_file_path}")

            # 清理临时文件（如果不需要保留）
            if not keep_temp_files:
                self.cleanup_temp_files(md_file_path)
        except OSError as e:
            print("PDF 生成失败。请确保已安装 wkhtmltopdf 并配置了路径。")
            print(f"错误详情: {e}")

    def cleanup_temp_files(self, md_file_path):
        """
        清理临时文件：删除markdown文件和images文件夹
        :param md_file_path: markdown文件路径
        """
        try:
            # 删除markdown文件
            if os.path.exists(md_file_path):
                os.remove(md_file_path)
                print(f"已删除临时文件: {md_file_path}")

            # 删除images文件夹
            if os.path.exists(self.images_dir):
                import shutil
                shutil.rmtree(self.images_dir)
                print(f"已删除临时文件夹: {self.images_dir}")

        except Exception as e:
            print(f"清理临时文件时出错: {e}")

# ================= 使用示例 =================

# 模拟一段 HTML 输入
dummy_html = """
<html>
<body>
    <div id="article-content">
        <h1>Python 自动化指南</h1>
        <p>这是一个段落，下面有一张图片。</p>
        <img src="https://www.python.org/static/community_logos/python-logo-master-v3-TM.png" alt="Python Logo">
        <p>这是结尾。</p>
        <ul>
            <li>列表项 1</li>
            <li>列表项 2</li>
        </ul>
    </div>
</body>
</html>
"""

if __name__ == "__main__":
    # 如果你是 Windows 且 wkhtmltopdf 没在环境变量，取消下面注释并填入实际路径
    wkhtmltopdf_path = r"C:\Users\30136\Desktop\csdn\wkhtmltox-0.12.6-1.mxe-cross-win64\wkhtmltox\bin\wkhtmltopdf.exe"
    # wkhtmltopdf_path = None 

    converter = HtmlToMdPdfConverter(output_dir="results", wkhtmltopdf_path=wkhtmltopdf_path)

    with open("example.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    dummy_html = html_content
    # print(dummy_html)
    
    converter.process(
        html_content=dummy_html, 
        target_div_selector="#content_views", 
        output_name="my_document"
    )