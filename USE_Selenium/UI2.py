import sys
import time
from urllib.parse import urlparse, urlunparse, ParseResult
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox
from PyQt5.QtCore import QThread, pyqtSignal
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from engine import engine
from modifyBibName import modifyBibName
from save import Save


class ScraperThread(QThread):
    log_signal = pyqtSignal(str)

    def __init__(self, conference, year, url, filters, browser):
        super().__init__()
        self.conference = conference
        self.year = year
        self.url = url
        self.filters = filters
        self.browser = browser
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
            urls = [self.url]
            self.engine = engine(self.browser, urls)
            all_links = {}
            filters = self.filters.split()

            for driver in self.engine.getPage():
                wait = WebDriverWait(driver, 10)
                # #journals\/pvldb\/0001S23 > nav > ul > li:nth-child(2) > div.head > a > img
                # /html/body/div[3]/ul
                # /li[1]/ ==
                # nav/ul/li[2]/div[1]/a
                uls = wait.until(EC.presence_of_all_elements_located((By.XPATH, "/html/body/div[3]/ul[@class='publ-list']")))
                for ul in uls:
                    if 'conf' in driver.current_url:
                        entries = wait.until(lambda d: ul.find_elements(By.CSS_SELECTOR, ".entry.inproceedings"))
                    elif 'journals' in driver.current_url:
                        entries = wait.until(lambda d: ul.find_elements(By.CSS_SELECTOR, ".entry.article"))
                    elif 'books' in driver.current_url:
                        entries = wait.until(lambda d: ul.find_elements(By.CSS_SELECTOR, ".entry.incollection"))
                    elif 'series' in driver.current_url:
                        entries = wait.until(lambda d: ul.find_elements(By.CSS_SELECTOR, ".entry.inproceedings"))
                    else:
                        entries = wait.until(lambda d: ul.find_elements(By.CSS_SELECTOR, ".entry"))
                    for entry in entries:
                        links = wait.until(lambda d: entry.find_elements(By.XPATH, ".//nav/ul/li[2]/div[1]/a"))
                        titles = wait.until(lambda d: entry.find_elements(By.CSS_SELECTOR, ".title"))
                        for link, title in zip(links, titles):
                            if any(filter_word.lower() in title.text.lower() for filter_word in filters):
                                all_links[title.text] = link.get_attribute("href")
                                self.log_signal.emit(f"找到论文：{title.text}")

            filename = f"{self.conference}{self.year}.json"
            Save(all_links, filename)
            self.log_signal.emit(f"论文链接已保存至 {filename}！")

            self.engine.urls = [self.convert_bibtex_url(link) for link in all_links.values()]
            for driver in self.engine.getPage():
                time.sleep(0.1)
            modifyBibName(filename)
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

        # 网址输入框
        self.url_label = QLabel("请输入爬取的网址（dblp期刊会议网址）：")
        layout.addWidget(self.url_label)
        self.url_input = QLineEdit()
        layout.addWidget(self.url_input)

        # 会议名称输入框
        self.conference_label = QLabel("请输入会议期刊名称（icml、vldb、sigmod）：")
        layout.addWidget(self.conference_label)
        self.conference_input = QLineEdit()
        layout.addWidget(self.conference_input)

        # 年份输入框
        self.year_label = QLabel("请输入年份：")
        layout.addWidget(self.year_label)
        self.year_input = QLineEdit()
        layout.addWidget(self.year_input)

        # 过滤关键词输入框
        self.filter_label = QLabel("请输入过滤关键词（空格分隔，小写）：")
        layout.addWidget(self.filter_label)
        self.filter_input = QLineEdit()
        layout.addWidget(self.filter_input)

        # 浏览器选择框
        self.browser_label = QLabel("选择浏览器（默认Chrome，可选Edge）：")
        layout.addWidget(self.browser_label)
        self.browser_select = QComboBox()
        self.browser_select.addItems(["Chrome", "Edge"])
        layout.addWidget(self.browser_select)

        # 按钮
        self.start_button = QPushButton("开始爬取")
        self.start_button.clicked.connect(self.start_scraping)
        layout.addWidget(self.start_button)

        # 输出窗口
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)

        self.setLayout(layout)
        self.setWindowTitle("学术论文爬取工具")
        self.resize(600, 400)

    def log(self, message):
        self.output_text.append(message)

    def start_scraping(self):
        conference = self.conference_input.text().strip()
        year = self.year_input.text().strip()
        url = self.url_input.text().strip()
        filters = self.filter_input.text().strip()
        browser = self.browser_select.currentText()

        if not conference or not year or not url:
            self.log("会议名称、年份和网址不能为空！")
            return

        # 创建并启动爬虫线程
        self.scraper_thread = ScraperThread(conference, year, url, filters, browser)
        self.scraper_thread.log_signal.connect(self.log)
        self.scraper_thread.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    scraper = WebScraperApp()
    scraper.show()
    sys.exit(app.exec_())