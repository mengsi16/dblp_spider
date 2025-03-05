import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager


class engine(object):
    def __init__(self, engineName='Edge', urls=[], *args):
        self.engineName = engineName
        self.urls = urls

        # Edge 浏览器的 User-Agent
        edge_user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"
        )

        if self.engineName == 'Edge':
            options = webdriver.EdgeOptions()
            prefs = {
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            }
            options.add_experimental_option("prefs", prefs)
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            options.add_argument(f"user-agent={edge_user_agent}")

            service = Service(EdgeChromiumDriverManager().install())
            self.driver = webdriver.Edge(service=service, options=options)

        elif self.engineName == 'Chrome':
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            options.add_argument(f"user-agent={edge_user_agent}")

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)

        # 执行 JavaScript 代码修改 navigator.webdriver
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def getDriver(self):
        return self.driver

    def quitDriver(self):
        self.driver.quit()

    def getPage(self, url=None):
        try:
            if not url:
                for url in self.urls:
                    self.driver.get(url)
                    time.sleep(3)
                    yield self.driver
            else:
                self.driver.get(url)
                time.sleep(3)
                yield self.driver
        finally:
            pass

    def quit(self):
        self.driver.quit()
        print("浏览器已关闭")
