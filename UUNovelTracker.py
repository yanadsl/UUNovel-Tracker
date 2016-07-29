# coding:utf-8
from bs4 import BeautifulSoup
import urllib2
import easygui
import os

# making everything utf-8 in case of encoding error
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


# 全/半形轉換
def str_full_to_half(textLine):
    # adapt from https://sites.google.com/site/richchihlee/portal/python/chin-convert-1
    myTextLine = textLine

    myTextLine = myTextLine.replace("Ａ", "A")
    myTextLine = myTextLine.replace("Ｂ", "B")
    myTextLine = myTextLine.replace("Ｃ", "C")
    myTextLine = myTextLine.replace("Ｄ", "D")
    myTextLine = myTextLine.replace("Ｅ", "E")
    myTextLine = myTextLine.replace("Ｆ", "F")
    myTextLine = myTextLine.replace("Ｇ", "G")
    myTextLine = myTextLine.replace("Ｈ", "H")
    myTextLine = myTextLine.replace("Ｉ", "I")
    myTextLine = myTextLine.replace("Ｊ", "J")
    myTextLine = myTextLine.replace("Ｋ", "K")
    myTextLine = myTextLine.replace("Ｌ", "L")
    myTextLine = myTextLine.replace("Ｍ", "M")
    myTextLine = myTextLine.replace("Ｎ", "N")
    myTextLine = myTextLine.replace("Ｏ", "O")
    myTextLine = myTextLine.replace("Ｐ", "P")
    myTextLine = myTextLine.replace("Ｑ", "Q")
    myTextLine = myTextLine.replace("Ｒ", "R")
    myTextLine = myTextLine.replace("Ｓ", "S")
    myTextLine = myTextLine.replace("Ｔ", "T")
    myTextLine = myTextLine.replace("Ｕ", "U")
    myTextLine = myTextLine.replace("Ｖ", "V")
    myTextLine = myTextLine.replace("Ｗ", "W")
    myTextLine = myTextLine.replace("Ｘ", "X")
    myTextLine = myTextLine.replace("Ｙ", "Y")
    myTextLine = myTextLine.replace("Ｚ", "Z")
    myTextLine = myTextLine.replace("ａ", "a")
    myTextLine = myTextLine.replace("ｂ", "b")
    myTextLine = myTextLine.replace("ｃ", "c")
    myTextLine = myTextLine.replace("ｄ", "d")
    myTextLine = myTextLine.replace("ｅ", "e")
    myTextLine = myTextLine.replace("ｆ", "f")
    myTextLine = myTextLine.replace("ｇ", "g")
    myTextLine = myTextLine.replace("ｈ", "h")
    myTextLine = myTextLine.replace("ｉ", "i")
    myTextLine = myTextLine.replace("ｊ", "j")
    myTextLine = myTextLine.replace("ｋ", "k")
    myTextLine = myTextLine.replace("ｌ", "l")
    myTextLine = myTextLine.replace("ｍ", "m")
    myTextLine = myTextLine.replace("ｎ", "n")
    myTextLine = myTextLine.replace("ｏ", "o")
    myTextLine = myTextLine.replace("ｐ", "p")
    myTextLine = myTextLine.replace("ｑ", "q")
    myTextLine = myTextLine.replace("ｒ", "r")
    myTextLine = myTextLine.replace("ｓ", "s")
    myTextLine = myTextLine.replace("ｔ", "t")
    myTextLine = myTextLine.replace("ｕ", "u")
    myTextLine = myTextLine.replace("ｖ", "v")
    myTextLine = myTextLine.replace("ｗ", "w")
    myTextLine = myTextLine.replace("ｘ", "x")
    myTextLine = myTextLine.replace("ｙ", "y")
    myTextLine = myTextLine.replace("ｚ", "z")
    myTextLine = myTextLine.replace("．", ".")
    return myTextLine


def search(Filiter, NovelName, NovelSite, LastChapter):
    BaseSite = "http://www.uukanshu.com"
    menu = urllib2.urlopen(BaseSite + NovelSite)
    content = menu.read().decode('gbk')

    # get things into Beautifulsoup
    # since what i need is on the top of the site , only input 1/4 into it
    soup = BeautifulSoup(content[:len(content) / 4], "html.parser")

    # find <a> tag(.a) from <div> tag with name "zuixin"(find_all) and find 1 result
    # find_all return a list , so use [0] to specify what i want
    a = soup.find_all("div", "zuixin", limit=1)[0].a

    # use contents to get only the content inside without <a>/</a> tag
    # check if there's a new chapter
    if a.contents[0] != LastChapter:
        LastChapter = a.contents[0]
        Novel = urllib2.urlopen(BaseSite + a.get('href'))
        content = Novel.read().decode('gbk')
        soup = BeautifulSoup(content, "html.parser")
        soup.find_all("div", "ad_content", limit=1)[0].extract()
        contentbox = soup.find_all("div", "contentbox", limit=1)[0].div.contents
        s = LastChapter
        for text in contentbox:
            tmp = str(text).encode()
            if tmp != "<br/>":
                if tmp.find('flag'):
                    s += (tmp + '\n')

        # filiter
        s = str_full_to_half(s)
        for name in Filiter:
            s = s.replace(name, "")
        try:
            with open(LastChapter + ".txt", 'w+') as f:
                f.write(s)
                easygui.msgbox(NovelName + "更新啦！\n" + LastChapter, "就跟你說去看小說啦")
                """
                try:
                    os.system(LastChapter + ".txt")
                except:
                    print "無法開啟下載檔案"
                """
                return LastChapter
        except:
            easygui.msgbox("無法建造檔案", "QQ請找作者回報")
    else:
        print "nothing"

# Main Entry Point
try:
    flag = 0
    f = open("config.tt", "r+")
    fread = f.read()
    print fread
    a = fread.split("\"")
    quantity = (len(a) - 2) / 6
    print "一共" + str(quantity) + "本書要找"
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
            NewChapter = search(Filiter, NovelName, NovelSite, LastChapter, a)
            if NewChapter is not None:
                flag = 1
                fread = fread.replace(LastChapter, NewChapter)
    f.close()
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
                   "全职法师", "/b/29676", "第一千一百四十九章 1念万钧，群链"]  # we start with blanks for the values
    fieldValues = easygui.multenterbox(msg, title, fieldNames, fieldValues)
    # make sure that none of the fields was left blank
    while 1:
        if fieldValues is None: break
        errmsg = ""
        for i in range(len(fieldNames)):
            if fieldValues[i].strip() == "":
                errmsg += '"%s" 不能為空.\n' % fieldNames[i]
        if errmsg == "": break  # no problems found
        fieldValues = easygui.multenterbox(msg+"\n"+errmsg, title, fieldNames, fieldValues)
    with open("test.txt", "w") as f:
        f.write("\"Filiter:" + fieldValues[0] + "\"\n"
                "\"NovelName:" + fieldValues[1] + "\"\n"
                "\"NovelSite:" + fieldValues[2] + "\"\n"
                "\"LastChapter:" + fieldValues[3] + "\"")
    print "Reply was:", fieldValues
