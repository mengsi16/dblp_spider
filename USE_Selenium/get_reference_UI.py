import sys
import os
import shutil
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
                             QPushButton, QTextEdit, QFileDialog)
from PyQt5.QtCore import QThread, pyqtSignal
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from engine import engine


class ScholarWorker(QThread):
    log_signal = pyqtSignal(str)

    def __init__(self, source_path, target_path, target_reference):
        super().__init__()
        self.source_path = source_path
        self.target_path = target_path
        self.target_reference = target_reference

    def run(self):
        directory_path = self.source_path
        new_path = self.target_path

        if not os.path.exists(directory_path):
            self.log_signal.emit("源目录不存在！")
            return
        if not os.path.exists(new_path):
            os.makedirs(new_path)
            self.log_signal.emit(f"创建目标目录: {new_path}")

        filenames = [f for f in os.listdir(directory_path) if f.endswith('.bib')]
        pattern_urls = [f"https://scholar.google.com.hk/scholar?hl=zh-CN&q={filename.replace('.bib', '')}" for filename
                        in filenames]

        self.log_signal.emit("启动 Selenium 浏览器...")
        Engine = engine('Chrome', pattern_urls)

        wait_time = 20
        for i, driver in enumerate(Engine.getPage()):
            filename = filenames[i]
            try:
                reference_element = WebDriverWait(driver, wait_time).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,
                                                    "#gs_res_ccl_mid > div:nth-child(1) > div.gs_ri > div.gs_fl.gs_flb > a:nth-child(3)"))
                )
                reference_text = reference_element.text.replace("被引用次数：", "").strip()

                try:
                    reference = int(reference_text)
                except ValueError:
                    self.log_signal.emit(f"无法解析引用次数: {reference_text}，跳过 {filename}")
                    continue

                if reference < self.target_reference:
                    self.log_signal.emit(f"{filename} 被引用次数 < {self.target_reference}，跳过")
                else:
                    source_path = os.path.join(directory_path, filename)
                    destination_path = os.path.join(new_path, filename)
                    shutil.copy2(source_path, destination_path)
                    self.log_signal.emit(f"复制 {filename} 到 {new_path}")
            except Exception as e:
                self.log_signal.emit(f"处理 {filename} 时出错: {e}")

        Engine.quit()
        self.log_signal.emit("任务完成！")


class ScholarApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.source_label = QLabel("指定目录路径:")
        layout.addWidget(self.source_label)
        self.source_input = QLineEdit(os.getcwd())
        layout.addWidget(self.source_input)

        self.source_button = QPushButton("选择文件夹")
        self.source_button.clicked.connect(self.select_source_folder)
        layout.addWidget(self.source_button)

        self.target_label = QLabel("指定目标文件夹路径:")
        layout.addWidget(self.target_label)
        self.target_input = QLineEdit(os.getcwd())
        layout.addWidget(self.target_input)

        self.target_button = QPushButton("选择文件夹")
        self.target_button.clicked.connect(self.select_target_folder)
        layout.addWidget(self.target_button)

        self.reference_label = QLabel("引用次数阈值:")
        layout.addWidget(self.reference_label)
        self.reference_input = QLineEdit("20")
        layout.addWidget(self.reference_input)

        self.run_button = QPushButton("运行爬取")
        self.run_button.clicked.connect(self.run_script)
        layout.addWidget(self.run_button)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        self.setLayout(layout)
        self.setWindowTitle("Scholar 引用爬取工具")
        self.resize(500, 400)

    def select_source_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择源目录")
        if folder:
            self.source_input.setText(folder)

    def select_target_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择目标目录")
        if folder:
            self.target_input.setText(folder)

    def log(self, message):
        self.log_output.append(message)
        QApplication.processEvents()

    def run_script(self):
        source_path = self.source_input.text()
        target_path = self.target_input.text()
        target_reference = int(self.reference_input.text())

        self.worker = ScholarWorker(source_path, target_path, target_reference)
        self.worker.log_signal.connect(self.log)
        self.worker.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScholarApp()
    window.show()
    sys.exit(app.exec_())