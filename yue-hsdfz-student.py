#============
# 依赖库区
#============
import re
import os
import requests
from colorama import init,Fore
from bs4 import BeautifulSoup
import pandas
import maskpass
import warnings
import click
#============

oaklet = requests.session() # 会话持久化自动保留 cookies

warnings.filterwarnings('ignore') # 过滤依赖库抛出的 Warning

# 查分表格式化输出
pandas.set_option('display.unicode.ambiguous_as_wide', True)
pandas.set_option('display.unicode.east_asian_width', True)
pandas.set_option('display.width', 200)
pandas.set_option('display.max_colwidth', 200)

# 把 HTTP GET 封装为一个函数，当 cookies 过期时自动重新登录并恢复数据
def Rget(URL):
    Response = oaklet.get(URL)
    if("登　　录" in Response.text):
        print("会话可能已经过期，正在重新登录。")
        res = oaklet.post("https://yue.hsdfz.com.cn/oaklet/j_spring_security_check?j_username="+ username +"&j_password="+ password +"&submit=%E7%99%BB%E3%80%80%E3%80%80%E5%BD%95")
        if("用户名或密码错误！" in res.text):
            print(Fore.RED+"自动重新登录失败，请重新输入用户信息。"+ Fore.WHITE)
            Login()
        else:
            print("自动重新登录成功。\n")
            return oaklet.get(URL); # 如果发生了登录需要再获取一次
    else:
        return Response;
    

# 取答题卡图像
def getCardImage():
    getCardImageURL=''
    getCardImageType=int(input("0:返回上一级\n1:正面原始卡\n2:正面批注卡\n3:背面原始卡\n4:背面批注卡\n请指定需要显示的卡图像:"))
    if(getCardImageType==0):
        return;
    else:
        if(getCardImageType==1):
            url = "https://yue.hsdfz.com.cn/oaklet/student/paperdataview_frontimage.html?id=" + paperID
            ImgLabel = BeautifulSoup(Rget(url).content,"lxml").find_all('img')
            for imgURL in ImgLabel:
               getCardImageURL=imgURL.get('src')
        elif(getCardImageType==2):
            Rget("https://yue.hsdfz.com.cn/oaklet/student/recreatemarkedpaperdata.html?id=" + paperID + "&side=front") # 取批注卡时先刷新批注
            print("请求刷新批注信息中，请稍等。")
            getCardImageURL = "https://yue.hsdfz.com.cn/oaklet/student/getmarkedpaperdata.html?id=" + paperID + "&side=front"
        elif(getCardImageType==3):
            url = "https://yue.hsdfz.com.cn/oaklet/student/paperdataview_backimage.html?id=" + paperID
            ImgLabel = BeautifulSoup(Rget(url).content,"lxml").find_all('img')
            for imgURL in ImgLabel:
                getCardImageURL=imgURL.get('src')
        elif(getCardImageType==4):
            Rget("https://yue.hsdfz.com.cn/oaklet/student/recreatemarkedpaperdata.html?id=" + paperID + "&side=back") # 取批注卡时先刷新批注
            print("请求刷新批注信息中，请稍等。")
            getCardImageURL = "https://yue.hsdfz.com.cn/oaklet/student/getmarkedpaperdata.html?id=" + paperID + "&side=back"
        with open('cache.jpg',"wb") as Image:
            Image.write(Rget(getCardImageURL).content)
        os.startfile('cache.jpg')
        getCardImage()

# 每次查询后清屏避免终端字符堆积
def ClearScreen():
    click.clear()

# 登录
def Login():
    init() # 彩色字符显示初始化
    print(Fore.WHITE + "==================================\n\n hsdfz oaklet student cilent\n https://github.com/DreamUniverse843/yue-hsdfz-student\n Licensed under GPLv3. (Stable 1.0.6)\n\n==================================")
    global username,password
    username=input("请输入用户名：")
    password=maskpass.askpass("请输入密码：")
    print("\n登录中。如程序长时间卡在此消息处，可能学校服务器响应超时。\n")
    res = oaklet.post("https://yue.hsdfz.com.cn/oaklet/j_spring_security_check?j_username="+ username +"&j_password="+ password +"&submit=%E7%99%BB%E3%80%80%E3%80%80%E5%BD%95")
    if("用户名或密码错误！" in res.text):
        print(Fore.RED+"用户名或密码错误，请检查用户名和密码是否正确。"+ Fore.WHITE)
        exit()
    else:
        print(Fore.CYAN+"登录成功。\n")
        MainMenu()
        
# 取得分信息
def getSpecificScore(rootURL,isTotal):
    global paperID,examDataID,isPaperSorted
    isPaperSorted = False
    print(rootURL)
    sortRootURL = "https://yue.hsdfz.com.cn/oaklet/student/userexampaperhtmldata.html?pid="+ queryTestID +"&sid="+ QueryTestSubject +"&uid=" + username
    testSpecificResult = BeautifulSoup(Rget(rootURL).content,"lxml")
    testSortedResult = BeautifulSoup(Rget(sortRootURL).content,"lxml")
    try:
        examDataID = re.findall(r"examdataid=(.+)\"", str(testSortedResult))[0] # 取分题型信息
    except(IndexError):
        examDataID = "null"
        print("提示：此科目未分题型，无法使用分题型列表。")
    paperResult = paperErrors = paperObjectResult = paperSubjectResult = paperSortedResult = pandas.DataFrame()
    if isTotal == 0:
        try:
            paperID = re.findall(r"paperdataid=(.+)&amp;", str(testSpecificResult))[0]
            if(examDataID != "null"):
                paperSortedGet = Rget("https://yue.hsdfz.com.cn/oaklet/student/listuserscorebyqt.html?paperdataid=" + paperID + "&examdataid=" + examDataID)
                if("请等待" in paperSortedGet.text):
                    print("提示：此科目试卷未评阅完毕，无法使用分题型列表。")
                else:
                    isPaperSorted = True
                    paperSortedResult = paperSortedResult.append(pandas.read_html(str((BeautifulSoup(paperSortedGet.content,"lxml").find_all("table"))),match="序号"))
            url = "https://yue.hsdfz.com.cn/oaklet/student/getuserexampaperdata.html?paperdataid="+ paperID + "&amp;utreeid="
            paperResult = paperResult.append(pandas.read_html(str((BeautifulSoup(Rget(url).content,"lxml").find_all("table"))),match="考号"))
            paperErrors = paperErrors.append(pandas.read_html(str((BeautifulSoup(Rget(url).content,"lxml").find_all("table"))),match="题号")).drop(['知识点'],axis=1)
            paperObjectResult = paperObjectResult.append(pandas.read_html(str((BeautifulSoup(Rget("https://yue.hsdfz.com.cn/oaklet/student/listuseroqs.html?paperdataid=" + paperID).content,"lxml").find_all("table"))),match="序号"))
            paperSubjectResult = paperSubjectResult.append(pandas.read_html(str((BeautifulSoup(Rget("https://yue.hsdfz.com.cn/oaklet/student/listusersqs.html?paperdataid=" + paperID).content,"lxml").find_all("table"))),match="序号"))
            print("==========基本情况==========")
            print(paperResult.iloc[0])
            print("=========客观题情况=========")
            print(paperObjectResult)
            print("\n客观题当前得分合计(可能含未评阅试题): " + str(paperObjectResult['考生得分'].sum()) + "\n")
            print("=========主观题情况=========")
            print(paperSubjectResult)
            print("\n主观题当前得分合计(可能含未评阅试题): " + str(paperSubjectResult['考生得分'].sum()) + "\n")
            print("==========错题情况==========")
            print(paperErrors)
            if(isPaperSorted == True):
                print("=========分题型显示=========")
                print(paperSortedResult)
            res=input(Fore.RED+"是否需要显示评卷图?(y/N) "+Fore.WHITE)
            if(res=='y' or res=='Y'):
                getCardImage()
        except(IndexError):
            print(Fore.RED + "\n无该科目试卷信息，可能是 ID 无效，或考生未参与该科考试，或试卷未扫描。\n"+Fore.WHITE)
    else:
        try:
            paperResult = paperResult.append(pandas.read_html(str(testSpecificResult.find_all("table")),match="考号"))
            print("==========基本情况==========")
            print(paperResult.iloc[0])
        except (ValueError):
            print(Fore.RED + "\n没有多科数据，可能未合成总成绩表。\n")

# 取考试学科数据
def queryTestInfo(rootURL):
    global isForceQuery,QueryTestSubject
    testGeneralInfo = BeautifulSoup(Rget(rootURL).content,"lxml")
    #print(testGeneralInfo)
    if testGeneralInfo.find_all("li") == []:
        print(Fore.RED + "未获取到考试数据，考试 ID 可能无效。" + Fore.WHITE)
        if isForceQuery != "y":
            isForceQuery = input("是否要尝试强制查询?(y/N)")
            if isForceQuery != "y":
                MainMenu()
            else:
                print(Fore.RED + "请注意:您正在进行强制查询。\n" + Fore.WHITE)
                print(" 14  语文\n 22  政治\n 17  物理\n 15  数学\n 16  英语\n 18  化学\n 21  地理\n 20  历史\n 19  生物")
    print("\n当前查询的考试 ID:"+queryTestID)
    if testGeneralInfo.find_all("a") == []:
        print(Fore.RED + "目前该考试尚未出总成绩，直接查询相应学科可能成绩不准确!"+Fore.WHITE)
    else:
        print(Fore.CYAN + "该考试已出总成绩，可以获取总成绩信息。"+Fore.WHITE)
    for child in testGeneralInfo.find_all("li"):
        itemID = child.get('itemid')
        itemName = (re.sub(r'[\u3000\u0020\t]+', '', child.get_text()).replace("\n",""))
        if itemID is None:
            continue;
        else:
            print(" " + itemID + "  " + itemName)
    QueryTestSubject = input("请输入您要查询的学科 id,或留空以获取总成绩,输入 exit 退出当前考试查询:")
    ClearScreen()
    if QueryTestSubject == "":
        url = "https://yue.hsdfz.com.cn/oaklet/student/getexamgrademultitotalofuser.html?projectid="+ queryTestID + "&uid="+ username + "&group=all"
        getSpecificScore(url,1)
    elif QueryTestSubject == "exit":
        MainMenu()
    else:
        url = "https://yue.hsdfz.com.cn/oaklet/student/userexampaperhtmldata.html?pid="+ queryTestID +"&sid="+ QueryTestSubject +"&uid=" + username
        getSpecificScore(url,0) 
    queryTestInfo(rootURL)

# 主菜单
def MainMenu():
    global queryTestID,isForceQuery
    isForceQuery = ""
    print(Fore.MAGENTA+"0.退出\n1.查考试清单\n2.直查考试id\n3.退出登录"+Fore.WHITE)
    Mission = input(Fore.RED + "请选择要执行的任务:" + Fore.WHITE)
    if Mission=="2":
        queryTestID = input("请输入需要查询的考试 id:")
        url = "https://yue.hsdfz.com.cn/oaklet/student/listvalidsubjecthtmldata.html?pid=" + str(queryTestID)
        queryTestInfo(url)
    else:
        if Mission=="1":
            url = "https://yue.hsdfz.com.cn/oaklet/student/listprojectwithlinkhtmldata.html?uid="+ str(username)
            testListElement = BeautifulSoup(Rget(url).content,'lxml')
            for child in testListElement.find_all("li"):
                #print(child)
                testID = child.get('id')
                testName = (re.sub(r'[\u3000\u0020\t]+', '', child.get_text()).replace("\n",""))
                print(" " + testID + "  " + testName)
            queryTestID = input(Fore.RED + "如果没有看到您要查询的考试，请尝试使用直查id模式。\n" + Fore.WHITE + "请输入需要查询的考试 id，或留空以返回主菜单:")
            if queryTestID == "":
                MainMenu()
            else:
                url = "https://yue.hsdfz.com.cn/oaklet/student/listvalidsubjecthtmldata.html?pid=" + str(queryTestID)
                queryTestInfo(url)
        elif Mission=="3":
            url = "https://yue.hsdfz.com.cn/oaklet/j_spring_security_logout"
            res = Rget(url)
            print("已成功退出登录。")
            Login()
        else:
            print("\nBye\n")
            exit()

# 启动点
Start=Login()
