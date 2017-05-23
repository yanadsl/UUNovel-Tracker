import easygui
import requests
from bs4 import BeautifulSoup
import os
import sys

# 全/半形轉換
dict = {"Ａ": "A", "Ｂ": "B", "Ｃ": "C", "Ｄ": "D", "Ｅ": "E", "Ｆ": "F", "Ｇ": "G", "Ｈ": "H", "Ｉ": "I", "Ｊ": "J", "Ｋ": "K",
        "Ｌ": "L", "Ｍ": "M", "Ｎ": "N", "Ｏ": "", "Ｐ": "P", "Ｑ": "Q", "Ｒ": "R", "Ｓ": "S", "Ｔ": "T", "Ｕ": "U", "Ｖ": "V",
        "Ｗ": "W", "Ｘ": "X", "Ｙ": "Y", "Ｚ": "Z", "ａ": "a", "ｂ": "b", "ｃ": "c", "ｄ": "d", "ｅ": "e", "ｆ": "f", "ｇ": "g",
        "ｈ": "h", "ｉ": "i", "ｊ": "j", "ｋ": "k", "ｌ": "l", "ｍ": "m", "ｎ": "n", "ｏ": "o", "ｐ": "p", "ｑ": "q", "ｒ": "r",
        "ｓ": "s", "ｔ": "t", "ｕ": "u", "ｖ": "v", "ｗ": "w", "ｘ": "x", "ｙ": "y", "ｚ": "z", "．": ".", "（": "(", "）": ")"}


def str_full_to_half(textLine):
    newTextLine = textLine
    for key, value in dict.items():
        newTextLine = newTextLine.replace(key, value)
    return newTextLine


def receive_url_data(site, timeout=10):
    try:
        menu = requests.get(site, timeout=timeout)
        return menu.text
    except requests.ConnectionError:
        easygui.msgbox("網路有問題", 'connection refuse or DNS error')
    except requests.HTTPError:
        easygui.msgbox("網路有問題", 'HTTP error')
    except requests.Timeout:
        easygui.msgbox("網路有問題", 'Time out')
    input('Press Enter to exit')
    sys.exit(0)


def search(Filiter, NovelName, NovelSite, LastChapter):
    BaseSite = "http://www.uukanshu.com"

    content = receive_url_data(BaseSite + NovelSite)

    # get things into Beautifulsoup
    soup = BeautifulSoup(content, "html5lib")

    # find <a> tag(.a) from <div> tag with name "zuixin"(find_all) and find 1 result
    # find_all return a list , so use [0] to specify what i want
    a_newest_chapter = soup.find_all("div", "zuixin", limit=1)[0].a

    # use contents to get only the content inside without <a>/</a> tag
    # check if there's a new chapter
    if a_newest_chapter.contents[0] != LastChapter:
        # 抓取清單，反轉，pop掉第一個(第一章)
        # 當抓到與上一個章節相同名稱後 find_flag = 1
        # 紀錄後面章節的url
        a_chapter_name = soup.find_all("div", "zhangjie clear", limit=1)[0].find_all("a")
        a_chapter_name.reverse()
        a_chapter_name.pop()
        find_flag = 0
        NewChapterUrlList = []
        for s in range(0, len(a_chapter_name)):
            if not find_flag:
                if a_chapter_name[s].contents[0] == LastChapter:
                    find_flag = 1
            else:
                LastChapter = a_chapter_name[s].contents[0]
                NewChapterUrlList.append(a_chapter_name[s].get('href'))

        # 開啟內容頁面
        ChapterNameList = []
        for url in NewChapterUrlList:
            content = receive_url_data(BaseSite + url)

            soup = BeautifulSoup(content, "html.parser")
            # delete div "ad_content"
            for ad_div in soup.find_all("div", "ad_content"):
                ad_div.extract()
            contentbox = soup.find_all("div", "contentbox", limit=1)[0].div.contents
            title = soup.html.head.title.contents[0].replace("_UU看书", "")
            s = title
            for text in contentbox:
                tmp = str(text)
                if tmp != "<br/>":
                    if tmp.find('flag'):
                        s += (tmp + '\n')
            s = s.replace(" ", "")
            # filiter
            s = str_full_to_half(s)
            for name in Filiter:
                s = s.replace(name, "")
            # get desktop path
            # from   http://wiki.alarmchang.com/index.php?title=Python_使用環境變數讀取Desktop_桌面路徑
            desktop = os.path.join(os.environ["HOMEDRIVE"], os.environ["HOMEPATH"], "Desktop")
            try:
                FileName = (title.replace(" ", "") + ".txt")
                with open(desktop + "\\" + FileName, 'w', encoding='utf8') as f:
                    f.write(s)
                    ChapterNameList.append(title)
            except IOError:
                easygui.msgbox("無法建造檔案", "QQ請找作者回報")

        # Thread(target=showmsg, args=(NovelName + "更新啦！\n" + '\n'.join(ChapterNameList), u"就跟你說去看小說啦")).start()
        # easygui.msgbox(NovelName + "更新啦！\n" + '\n'.join(ChapterNameList), "就跟你說去看小說啦")
        # openfile
        # 先開的視窗(舊章節)會被蓋在下面，故用reverse
        ChapterNameList.reverse()
        desktop = os.path.join(os.environ["HOMEDRIVE"], os.environ["HOMEPATH"], "Desktop")
        for name in ChapterNameList:
            try:
                os.startfile((desktop + "\\" + name.replace(" ", "") + ".txt"))
            except IOError:
                easygui.msgbox("無法開啟下載檔案", "QQ請找作者回報")
                sys.exit(0)
        return LastChapter
    else:
        print("nothing")


# Main Entry Point
try:
    flag = 0
    f = open("config.txt", "r", encoding='utf8')
    fread = f.read()
    config = fread.split("\"")
    quantity = int((len(config) - 3) / 6)
    print(str(quantity) + " Books to find")
    for things in config:
        if not things.find("Filter"):
            Filter = things[8:]
            Filter = Filter.split(",")
        if not things.find("NovelName"):
            NovelName = things[10:]
        if not things.find("NovelSite"):
            NovelSite = things[10:]
        if not things.find("LastChapter"):
            LastChapter = things[12:]
            NewChapter = search(Filter, NovelName, NovelSite, LastChapter)
            if NewChapter is not None:
                flag = 1
                fread = fread.replace(LastChapter, NewChapter)
    f.close()
    # update config
    if flag:
        try:
            with open("config.txt", "w", encoding='utf8') as f:
                f.write(fread)
        except IOError:
            easygui.msgbox("設定檔寫入有問題", "QQ請找作者回報")

except IOError:
    msg = "設定檔有問題喔，按下確認重新建立"
    title = "UUNovel-Tracker"
    if easygui.ynbox(msg, title, choices=("是", "否")):  # show a Continue/Cancel dialog
        pass  # user chose Continue
    else:  # user chose Cancel
        sys.exit(0)

    msg = "首次小說設定"
    title = "UUNovel-Tracker"
    fieldNames = ["過濾字串", "小說名稱", "小說網址", "上個章節名"]
    fieldValues = ["UU看书（ www.uukanshu.com ),ex1,ex2",
                   "全职法师", "/b/29676", "第一千一百四十九章 1念万钧，群链"]  # initial values
    fieldValues = easygui.multenterbox(msg, title, fieldNames, fieldValues)

    # make sure that none of the fields was left blank
    while 1:
        if fieldValues is None:
            break
        errmsg = ""
        for i in range(len(fieldNames)):
            if fieldValues[i].strip() == "":
                errmsg += '"%s" 不能為空.\n' % fieldNames[i]
        if errmsg == "":
            break  # no problems found
        fieldValues = easygui.multenterbox(msg + "\n" + errmsg, title, fieldNames, fieldValues)
    with open("config.txt", "w", encoding='utf8') as f:
        f.write("\"Filiter:" + fieldValues[0] + "\"\n"
                "\"NovelName:" + fieldValues[1] + "\"\n"
                "\"NovelSite:" + fieldValues[2] + "\"\n"
                "\"LastChapter:" + fieldValues[3] + "\"")
