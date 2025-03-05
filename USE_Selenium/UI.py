import sys
import time
from urllib.parse import urlparse, urlunparse, ParseResult
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit
from PyQt5.QtCore import QThread, pyqtSignal
from selenium.webdriver.common.by import By
from engine import engine
from modifyBibName import modifyBibName
from save import Save


class ScraperThread(QThread):
    log_signal = pyqtSignal(str)

    def __init__(self, conference, year, filters):
        super().__init__()
        self.conference = conference
        self.year = year
        self.filters = filters
        self.engine = None

    def convert_bibtex_url(self, original_url):
        parsed = urlparse(original_url)
        new_path = parsed.path.replace(".html", ".bib")
        new_query = "param=1"
        new_components = ParseResult(
            scheme=parsed.scheme,
            netloc=parsed.netloc,
            path=new_path,
            params=parsed.params,
            query=new_query,
            fragment=parsed.fragment
        )
        return urlunparse(new_components)

    def run(self):
        try:
            urls = [f"https://dblp.org/db/conf/{self.conference}/{self.conference}{self.year}.html"]
            self.engine = engine('Edge', urls)
            all_links = {}

            for driver in self.engine.getPage():
                uls = driver.find_elements(By.XPATH, "/html/body/div[3]/ul[@class='publ-list']")
                for ul in uls:
                    entries = ul.find_elements(By.CSS_SELECTOR, ".entry.inproceedings")
                    for entry in entries:
                        links = entry.find_elements(By.XPATH, ".//nav/ul/li[2]/div[1]/a")
                        titles = entry.find_elements(By.CSS_SELECTOR, ".title")
                        for link, title in zip(links, titles):
                            for filter_word in self.filters:
                                if filter_word in title.text.lower():
                                    all_links[title.text] = link.get_attribute("href")
                                    self.log_signal.emit(f"找到论文：{title.text}")

            Save(all_links, f"{self.conference}{self.year}.json")
            self.log_signal.emit("论文链接已保存！")

            # 获取 BibTeX 链接
            self.engine.urls = [self.convert_bibtex_url(link) for link in all_links.values()]
            for driver in self.engine.getPage():
                time.sleep(0.1)
            modifyBibName(f"{self.conference}{self.year}")
            self.log_signal.emit("BibTeX 名称修改完成！")

        except Exception as e:
            self.log_signal.emit(f"发生错误：{str(e)}")

        finally:
            if self.engine:
                self.engine.quit()
            self.log_signal.emit("爬取结束")


class WebScraperApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # 会议名称
        self.conference_label = QLabel("请输入会议名称：")
        layout.addWidget(self.conference_label)
        self.conference_input = QLineEdit()
        layout.addWidget(self.conference_input)

        # 年份
        self.year_label = QLabel("请输入年份：")
        layout.addWidget(self.year_label)
        self.year_input = QLineEdit()
        layout.addWidget(self.year_input)

        # 过滤关键词
        self.filters_label = QLabel("请输入过滤关键词（空格分隔）：")
        layout.addWidget(self.filters_label)
        self.filters_input = QLineEdit()
        layout.addWidget(self.filters_input)

        # 按钮
        self.start_button = QPushButton("开始爬取")
        self.start_button.clicked.connect(self.start_scraping)
        layout.addWidget(self.start_button)

        # 输出窗口
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)

        self.setLayout(layout)
        self.setWindowTitle("学术会议论文爬取工具")
        self.resize(600, 400)

    def log(self, message):
        self.output_text.append(message)

    def start_scraping(self):
        conference = self.conference_input.text().strip()
        year = self.year_input.text().strip()
        filters = self.filters_input.text().strip().split()

        if not conference or not year:
            self.log("会议名称和年份不能为空！")
            return

        # 创建并启动爬虫线程
        self.scraper_thread = ScraperThread(conference, year, filters)
        self.scraper_thread.log_signal.connect(self.log)
        self.scraper_thread.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    scraper = WebScraperApp()
    scraper.show()
    sys.exit(app.exec_())
