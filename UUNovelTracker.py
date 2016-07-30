# coding:utf-8
from bs4 import BeautifulSoup
import urllib2
import easygui
import os
from threading import Thread
# making everything utf-8 in case of encoding error
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


# using thread with this to make a non-blocking msg
def showmsg(msg, title):
    easygui.msgbox(msg, title)


# 全/半形轉換
dict = {"Ａ":"A","Ｂ":"B","Ｃ":"C","Ｄ":"D","Ｅ":"E","Ｆ":"F","Ｇ":"G","Ｈ":"H","Ｉ":"I","Ｊ":"J","Ｋ":"K",
        "Ｌ":"L","Ｍ":"M","Ｎ":"N","Ｏ":"","Ｐ":"P","Ｑ":"Q","Ｒ":"R","Ｓ":"S","Ｔ":"T","Ｕ":"U","Ｖ":"V",
        "Ｗ":"W","Ｘ":"X","Ｙ":"Y","Ｚ":"Z","ａ":"a","ｂ":"b","ｃ":"c","ｄ":"d","ｅ":"e","ｆ":"f","ｇ":"g",
        "ｈ":"h","ｉ":"i","ｊ":"j","ｋ":"k","ｌ":"l","ｍ":"m","ｎ":"n","ｏ":"o","ｐ":"p","ｑ":"q","ｒ":"r",
        "ｓ":"s","ｔ":"t","ｕ":"u","ｖ":"v","ｗ":"w","ｘ":"x","ｙ":"y","ｚ":"z","．":".","（":"(","）":")"}
def str_full_to_half(textLine):
    key = dict.keys()
    value = dict.values()
    newTextLine = textLine
    for alphabet in range(0, 54):
        newTextLine = newTextLine.replace(key[alphabet], value[alphabet])
    return newTextLine


def search(Filiter, NovelName, NovelSite, LastChapter):
    BaseSite = "http://www.uukanshu.com"
    menu = urllib2.urlopen(BaseSite + NovelSite)
    content = menu.read().decode('gbk')

    # get things into Beautifulsoup
    # since what i need is on the top of the site , only input 1/4 into it
    soup = BeautifulSoup(content, "html.parser")

    # find <a> tag(.a) from <div> tag with name "zuixin"(find_all) and find 1 result
    # find_all return a list , so use [0] to specify what i want
    a = soup.find_all("div", "zuixin", limit=1)[0].a

    # use contents to get only the content inside without <a>/</a> tag
    # check if there's a new chapter
    if a.contents[0] != LastChapter:
        # 抓取清單，反轉，pop掉第一個(第一章)
        # 當抓到與上一個章節相同名稱後 find_flag = 1
        # 紀錄後面章節的url
        a = soup.find_all("div", "zhangjie clear", limit=1)[0].find_all("a")
        a.reverse()
        a.pop()
        find_flag = 0
        NewChapterUrlList = []
        for s in range(0, len(a)):
            if not find_flag:
                if a[s].contents[0] == LastChapter:
                    find_flag = 1
            else:
                LastChapter = a[s].contents[0]
                NewChapterUrlList.append(a[s].get('href'))

        # 開啟內容頁面
        ChapterNameList = []
        for url in NewChapterUrlList:
            Novel = urllib2.urlopen(BaseSite + url)
            content = Novel.read().decode('gbk')

            soup = BeautifulSoup(content, "html.parser")
            # delete div "ad_content"
            soup.find_all("div", "ad_content", limit=1)[0].extract()
            contentbox = soup.find_all("div", "contentbox", limit=1)[0].div.contents
            title = soup.html.head.title.contents[0].replace("_UU看书", "")
            s = title
            for text in contentbox:
                tmp = str(text).encode()
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
                FileName = (title.replace(" ", "") + ".txt").encode().decode()
                with open(desktop + "\\" + FileName, 'w') as f:
                    f.write(s)
                    ChapterNameList.append(title)
            except:
                easygui.msgbox("無法建造檔案", "QQ請找作者回報")

        Thread(target=showmsg, args=(NovelName + "更新啦！\n" + '\n'.join(ChapterNameList), u"就跟你說去看小說啦")).start()
        #easygui.msgbox(NovelName + "更新啦！\n" + '\n'.join(ChapterNameList), "就跟你說去看小說啦")
        # openfile
        # 先開的視窗(舊章節)會被蓋在下面，故用reverse
        ChapterNameList.reverse()
        for name in ChapterNameList:
            try:
                os.startfile((desktop + "\\" + name.replace(" ", "") + ".txt").encode().decode())
            except:
                easygui.msgbox("無法開啟下載檔案", "QQ請找作者回報")
        return LastChapter
    else:
        print "nothing"


# Main Entry Point
try:
    flag = 0
    f = open("config.txt", "r")
    fread = f.read()
    a = fread.split("\"")
    quantity = (len(a) - 2) / 6
    print str(quantity) + " Books to find"
    for things in a:
        if not things.find("Filiter"):
            Filiter = things[8:]
            Filiter = Filiter.split(",")
        if not things.find("NovelName"):
            NovelName = things[10:]
        if not things.find("NovelSite"):
            NovelSite = things[10:]
        if not things.find("LastChapter"):
            LastChapter = things[12:]
            NewChapter = search(Filiter, NovelName, NovelSite, LastChapter)
            if NewChapter is not None:
                flag = 1
                fread = fread.replace(LastChapter, NewChapter)
    f.close()
    # update config
    if flag:
        try:
            with open("config.txt", "w") as f:
                f.write(fread)
        except:
            easygui.msgbox("設定檔寫入有問題", "QQ請找作者回報")

except:
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
        if fieldValues is None: break
        errmsg = ""
        for i in range(len(fieldNames)):
            if fieldValues[i].strip() == "":
                errmsg += '"%s" 不能為空.\n' % fieldNames[i]
        if errmsg == "": break  # no problems found
        fieldValues = easygui.multenterbox(msg + "\n" + errmsg, title, fieldNames, fieldValues)
    with open("config.txt", "w") as f:
        f.write("\"Filiter:" + fieldValues[0] + "\"\n"
                "\"NovelName:" + fieldValues[1] + "\"\n"
                "\"NovelSite:" + fieldValues[2] + "\"\n"
                "\"LastChapter:" + fieldValues[3] + "\"")
