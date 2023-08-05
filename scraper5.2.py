'''
# -*- coding: utf-8 -*-
# @version  : Python 3.10.4
# @Time     : 2023/02/08
# @functionality: download the phonetic,meaning and voice of a word from https://www.iciba.com/
# @Last edited time: 2023/08/05 16:30
'''

import sys
import os
from fake_useragent import UserAgent
import requests
import json
import time
from asyncore import write
# from asyncio import write Python 3.12
import csv
from tkinter.filedialog import *
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import subprocess

file_path = askdirectory(initialdir=sys.path[0], title='请选择根目录')

# 5秒静音mp3文件
silent_file = file_path + "/" + "5_seconds_silence.mp3"
# 构建伪装代理
# ua = UserAgent()
headers = {
    # "User-Agent":ua.random
    "User-Agent": 'Mozilla/5.0'
}
# chapters = ['chapter1', 'chapter2', 'chapter3', 'chapter4', 'chapter5',
#             'chapter6', 'chapter7', 'chapter8', 'chapter9', 'chapter10',
#             'chapter11', 'chapter12', 'chapter13', 'chapter14', 'chapter15',
#             'chapter16', 'chapter17', 'chapter18', 'chapter19', 'chapter20',
#             'chapter21', 'chapter22']
# chapters = ['chapter21', 'chapter22']

chapters = ['input_list']

for chapter in chapters:
    print(chapter)

    input_file_path = file_path + "/" + chapter + ".txt"  # 单词文件
    output_file_path = file_path + "/" + chapter + "_result.csv"  # 输出文件
    with open(input_file_path, encoding='utf-8') as file_obj:
        lines = file_obj.readlines()
    # 打开输出文件
    csvfile = open(output_file_path, 'a', encoding='utf-8', newline='')
    csvfile.truncate(0)  # 清空文件
    writer = csv.writer(csvfile)
    # 创建目录
    original_folder = file_path + '/' + 'No5s/' + chapter  # 发音文件本地保存路径
    with_5s_folder = file_path + '/' + 'Yes5s/' + chapter  # 插入静音后的发音文件保存路径
    os.makedirs(original_folder, exist_ok=True)  # 创建多级目录
    os.makedirs(with_5s_folder, exist_ok=True)

    chrome_options = webdriver.ChromeOptions()  # 实例化配置对象
    chrome_options.add_argument('--headless')  # 无界面模式
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument(
        '--blink-setting=imagesEnable=false')  # 不加载图片，提升速度
    chrome_options.add_argument('--disable-extension')  # 禁用扩展
    browser = webdriver.Chrome(
        executable_path='/snap/bin/chromium.chromedriver', chrome_options=chrome_options)
    word_url = "https://www.iciba.com/"
    countWord = 0  # 单词计数器
    for line in lines:
        # 初始化
        no_uk_audio = False  # 英式声音文件标志
        no_en_audio = False  # 美式声音文件标志
        not_specified_audio = False  # 声音文件标志(未注明英式或美式情况)
        word = line.rstrip("\n")  # 单词
        # 去除多余的空格,并将空格替换为+,应对词组如：speed up,stepping stone
        word = "+".join(word.split())
        print('\t', word)
        phonetic = " "  # 音标
        meaning = " "  # 翻译
        url_uk_voice = ""  # 英式发音文件地址
        url_en_voice = ""  # 美式发音文件地址

        browser.get(word_url)
        WebDriverWait(browser, 1000).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'Contact_footer___Mjbg')))
        time.sleep(1)
        # 模拟输入
        browser.find_element(
            By.CSS_SELECTOR, '[type="search"]').send_keys(word + '\n')  # 加一个回车符相当于提交
        # browser.find_element(By.CSS_SELECTOR, ".Banner_input__JFqWg").click()

        # 异常处理：常见于单词拼写错误，金山词霸翻译找不到场合
        try:
            # 加载页面
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'FoldBox_fold__j7cgz')))
        except:
            print('\t'*2, "Error")
            pass
        # 模拟点击发音小喇叭
        try:
            browser.find_element(
                By.XPATH, '//ul[@class="Mean_symbols__fpCmS"]/li[contains(text(),"英")]/child::img').click()  # 英式发音

            time.sleep(1)
            url_uk_voice = browser.find_element(
                By.TAG_NAME, "audio").get_attribute("src")
            # print(url_uk_voice)
        except:
            no_uk_audio = True
            print('\t'*2, "没有英式发音")
            pass

        try:
            browser.find_element(
                By.XPATH, '//ul[@class="Mean_symbols__fpCmS"]/li[contains(text(),"美")]/child::img').click()  # 美式发音
            time.sleep(1)
            url_en_voice = browser.find_element(
                By.TAG_NAME, "audio").get_attribute("src")
            # print(url_en_voice)
        except:
            no_en_audio = True
            print('\t'*2, "没有美式发音")
            pass
        time.sleep(1)  # 非常重要 显性延迟，以保证同步
        if no_en_audio and no_uk_audio:  # 如 word="weather man"
            try:
                browser.find_element(
                    By.XPATH, '//ul[@class="Mean_symbols__fpCmS"]/li/child::img').click()  # 美式发音
                time.sleep(1)
                url_not_specified_voice = browser.find_element(
                    By.TAG_NAME, "audio").get_attribute("src")
                # print(url_en_voice)
            except:
                not_specified_audio = True
                print('\t'*2, "没有发音文件")
                pass
        try:
            phonetic = browser.find_element(
                By.CLASS_NAME, "Mean_symbols__fpCmS").text  # 英美音标

            meaning = browser.find_element(
                By.CLASS_NAME, "Mean_part__UI9M6").text  # 翻译结果

        except:
            print('\t'*2, "没有音标")
            pass
        # print("%s   %s   %s   %s   %s" %
        #       (word, phonetic, meaning, url_uk_voice, url_en_voice))
        data = (word, phonetic, meaning, url_uk_voice, url_en_voice)
        writer.writerow(data)  # 写入数据
        csvfile.flush()  # 实时保存 以防程序意外退出而使数据没有保存
        time.sleep(1)  # 非常重要 模拟人工操作所需时间间隔，以欺骗网站反爬机制
        browser.refresh()

        # 下载英式音频文件
        if not no_uk_audio:
            uk_filename = original_folder + \
                '/' + str(countWord) + '_' + word + '_uk.mp3'
            # 创建文件
            os.makedirs(os.path.dirname(uk_filename), exist_ok=True)
            voi_uk = requests.get(url_uk_voice, headers=headers)
            # 写入数据
            with open(uk_filename, 'wb') as f:
                f.write(voi_uk.content)
            # 插入静音文件
            uk_5s_filename = with_5s_folder + \
                '/' + str(countWord) + '_' + word + '_uk_5s.mp3'
            cmd_line = "ffmpeg -loglevel quiet -y -i " + \
                uk_filename + " -i " + silent_file + " " + \
                "-filter_complex '[0:0] [1:0] concat=n=2:v=0:a=1 [a]' -map [a] " +\
                uk_5s_filename
            subprocess.run(cmd_line, shell=True)
        # 下载美式音频文件
        if not no_en_audio:
            en_filename = original_folder + \
                '/' + str(countWord) + '_' + word + '_en.mp3'
            # 创建文件
            os.makedirs(os.path.dirname(en_filename), exist_ok=True)
            voi_en = requests.get(url_en_voice, headers=headers)
            # 写入数据
            with open(en_filename, 'wb') as f:
                f.write(voi_en.content)
            # 插入静音文件
            en_5s_filename = with_5s_folder + \
                '/' + str(countWord) + '_' + word + '_en_5s.mp3'
            cmd_line = "ffmpeg -loglevel quiet -y -i " + \
                en_filename + " -i " + silent_file + " " + \
                "-filter_complex '[0:0] [1:0] concat=n=2:v=0:a=1 [a]' -map [a] " +\
                en_5s_filename
            subprocess.run(cmd_line, shell=True)
        # 下载单独音频文件
        if no_en_audio and no_uk_audio and not not_specified_audio:
            not_specified_filename = original_folder + \
                '/' + str(countWord) + '_' + word + '.mp3'
            # 创建文件
            os.makedirs(os.path.dirname(not_specified_filename), exist_ok=True)
            voi_not_specified = requests.get(
                url_not_specified_voice, headers=headers)
            # 写入数据
            with open(not_specified_filename, 'wb') as f:
                f.write(voi_not_specified.content)
            # 插入静音文件
            not_specified_5s_filename = with_5s_folder + \
                '/' + str(countWord) + '_' + word + '_5s.mp3'
            cmd_line = "ffmpeg -loglevel quiet -y -i " + not_specified_filename + \
                " -i " + silent_file + " " + \
                "-filter_complex '[0:0] [1:0] concat=n=2:v=0:a=1 [a]' -map [a] " +\
                not_specified_5s_filename
            subprocess.run(cmd_line, shell=True)
        countWord += 1

csvfile.close()
browser.close()
browser.quit()
print("完成，请到相应文件夹查看！")