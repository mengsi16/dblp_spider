# dblp_spider
dblp会议/期刊爬虫，主要是下载bib文档，下载地址默认是系统的下载文件（还没添加改下载地址输入框）。并且可以快速从谷歌文献中爬取每个论文的被引用量，从而判断该论文是否有阅读的意义。
![image](https://github.com/user-attachments/assets/03e26097-f35c-4a31-9526-a0ad829b3674)

### 文件目录
```bash
USE_Selenium
├─ engine.py
├─ get_reference.py
├─ get_reference_UI.py
├─ modifyBibName.py
├─ save.py
├─ Selenium_Get_DBLP.py
├─ UI.py
└─ UI2.py
```
爬虫核心逻辑在Selenium_Get_DBLP.py以及engine.py（这里可以自己随意DIY）
可以使用UI2.py打开一个简易的UI爬虫界面。
get_reference.py 可以快速筛选引用量达标的论文出来。~~（还没有做UI界面）~~
get_reference_UI.py是get_reference.py的pyqt5前端UI界面

## 运行UI2.py
<p align="center"><img src="https://github.com/user-attachments/assets/f32ab61d-f458-4bf3-b6fd-14d890365c8c" alt="描述文字" width="500"></p>

## 运行get_reference_UI.py
<p align="center"><img src="https://github.com/user-attachments/assets/133ab7c9-74d3-4167-a1a8-31550f8f806a" alt="描述文字" width="500"></p>

非常简陋。
