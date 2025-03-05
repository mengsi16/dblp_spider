import time
from urllib.parse import urlparse, urlunparse, ParseResult

from selenium.webdriver.common.by import By

from engine import engine
from modifyBibName import modifyBibName
from save import Save

try:
    # 访问 ICML 2024 会议页面
    conference = input("例子：icml\n请输入会议名称：")
    year = input("例子：2024\n请输入年份：")
    filters = input("例子：llm neural\n请输入过滤关键词：").split()
    urls = [f"https://dblp.org/db/conf/{conference}/{conference}{year}.html"]
    engine = engine('Edge', urls)
    all_links = {}
    for driver in engine.getPage():
        # 批量爬取 XPath 指定的链接
        uls = driver.find_elements(By.XPATH, "/html/body/div[3]/ul[@class='publ-list']")
        print(uls)
        for ul in uls:
            # 获取当前ul下的所有论文条目
            entries = ul.find_elements(By.CSS_SELECTOR, ".entry.inproceedings")
            print("get links")
            # print(entries)
            for entry in entries:
                # 在条目内相对查找链接
                links = entry.find_elements(By.XPATH, ".//nav/ul/li[2]/div[1]/a")
                titles = entry.find_elements(By.CSS_SELECTOR, ".title")  #conf\/icml\/ZhaoBMG24 > cite > span.title
                for link, titles in zip(links, titles):
                    for filter in filters:
                        if filter in titles.text.lower():
                            all_links[titles.text] = link.get_attribute("href")

        Save(all_links, f"{conference}{year}")


    def convert_bibtex_url(original_url):
        # 解析原始URL
        parsed = urlparse(original_url)

        # 修改路径：将.html替换为.bib
        new_path = parsed.path.replace(".html", ".bib")

        # 构建新的查询参数
        new_query = "param=1"

        # 组装新的URL组件
        new_components = ParseResult(
            scheme=parsed.scheme,
            netloc=parsed.netloc,
            path=new_path,
            params=parsed.params,
            query=new_query,
            fragment=parsed.fragment
        )

        return urlunparse(new_components)

    # 更新urls
    engine.urls = []
    for title, link in all_links.items():
        engine.urls.append(convert_bibtex_url(link))
    for driver in engine.getPage():
        time.sleep(0.5)
    modifyBibName(f"{conference}{year}")

finally:
    engine.quit()
