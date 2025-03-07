import os
import shutil

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from engine import engine


source_path = input("指定目录路径：")
# 指定目录路径
directory_path = rf'{source_path}'

target_path = input("指定目标文件夹路径：")
# 指定目标文件夹路径
# new_path = rf'B:\study\研究生\研讨厅演武堂\研讨厅\待阅读论文\VLDB SUBGRAPH 2024 Read'
new_path = rf'{target_path}'

Target_Reference = int(input())

# 初始化一个空列表来存储文件名
filenames = []

# 获取目录中的所有条目（包括文件和子目录）
all_entries = os.listdir(directory_path)

# 遍历每个条目，检查是否为文件
for entry in all_entries:
    # 构建完整路径
    full_path = os.path.join(directory_path, entry)
    # 检查是否为文件
    if os.path.isfile(full_path):
        # 将文件名添加到列表中
        filenames.append(entry)

# 生成 URL 列表
pattern_urls = [f"https://scholar.google.com.hk/scholar?hl=zh-CN&q={filename.replace('.bib', '')}" for filename in filenames]

# 初始化 Selenium Engine
Engine = engine('Chrome', pattern_urls)

# 如果目标文件夹不存在，则创建它
if not os.path.exists(new_path):
    os.makedirs(new_path)

# 设置显式等待的最大时间（秒）
wait_time = 20

for i, driver in enumerate(Engine.getPage()):
    filename = filenames[i]
    if os.path.isfile(os.path.join(new_path, filename)):
        print(f"文件 {filename} 已经存在于 {new_path}，跳过")
        continue
    try:
        # 等待引用次数元素出现
        reference_element = WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#gs_res_ccl_mid > div:nth-child(1) > div.gs_ri > div.gs_fl.gs_flb > a:nth-child(3)"))
        )

        # 获取引用次数文本并处理
        reference_text = reference_element.text.replace("被引用次数：", "").strip()

        try:
            reference = int(reference_text)
        except ValueError:
            print(f"无法解析引用次数: {reference_text}，跳过文件 {filename}")
            continue

        if reference < Target_Reference:
            print(f"{filename.replace('.bib', '')} 被引用次数 < 20，没有阅读价值")
        else:
            bibFilename = f"{os.path.splitext(filename)[0]}.bib"
            source_path = os.path.join(directory_path, bibFilename)
            destination_path = os.path.join(new_path, bibFilename)

            if os.path.isfile(source_path):
                # 复制文件
                shutil.copy2(source_path, destination_path)
                print(f"文件 {filename} 成功从 {directory_path} 复制到 {new_path}")
            else:
                print(f"Bib 文件 {bibFilename} 不存在于 {directory_path}")
    except Exception as e:
        print(f"处理文件 {filename} 时出错: {e}")

# 关闭所有浏览器实例
Engine.quit()