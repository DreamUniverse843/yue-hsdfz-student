#============
#依赖库区
#============
from ast import For
from cgi import test
from imghdr import tests
import re
import os
import requests
from colorama import init,Fore,Back,Style
from bs4 import BeautifulSoup
import pandas
import maskpass
import warnings
import platform
#============

oaklet = requests.session() # 会话持久化自动保留 cookies

warnings.filterwarnings('ignore') # 过滤依赖库抛出的 Warning

# 查分表格式化输出
pandas.set_option('display.unicode.ambiguous_as_wide', True)
pandas.set_option('display.unicode.east_asian_width', True)
pandas.set_option('display.width', 180) 

# 每次查询后清屏避免终端字符堆积
def ClearScreen():
    if(platform.system == "Windows"):
        os.system("cls") # Windows 系统下调用 cls 清屏
    else:
        os.system("printf'\033c'") # Linux 系统下调用复位符清屏

def Login():
    print("==================================\n\n hsdfz oaklet student cilent\n https://github.com/DreamUniverse843/yue-hsdfz-student\n Licensed in GPLv3.\n\n==================================")
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
        

def getSpecificScore(rootURL,isTotal):
    testSpecificResult = BeautifulSoup(oaklet.get(rootURL).content,"lxml")
    #print(str(testSpecificResult))
    #print(testSpecificResult.find_all("table"))
    paperResult = paperErrors = pandas.DataFrame()
    if isTotal == 0:
        try:
            paperID = re.findall(r"paperdataid=(.+)&amp;", str(testSpecificResult))[0]
            url = "https://yue.hsdfz.com.cn/oaklet/student/getuserexampaperdata.html?paperdataid="+ paperID + "&amp;utreeid="
            paperResult = paperResult.append(pandas.read_html(str((BeautifulSoup(oaklet.get(url).content,"lxml").find_all("table"))),match="考号"))
            paperErrors = paperErrors.append(pandas.read_html(str((BeautifulSoup(oaklet.get(url).content,"lxml").find_all("table"))),match="题号"))
            print("==========基本情况==========")
            print(paperResult.iloc[0])
            print("==========错题情况==========")
            print(paperErrors)
        except(IndexError):
            print(Fore.RED + "\n无该科目试卷信息，可能是 ID 无效，或考生未参与该科考试，或试卷未扫描。\n"+Fore.WHITE)
    else:
        try:
            paperResult = paperResult.append(pandas.read_html(str(testSpecificResult.find_all("table")),match="考号"))
            print("==========基本情况==========")
            print(paperResult.iloc[0])
        except (ValueError):
            print(Fore.RED + "\n没有多科数据，可能未合成总成绩表。\n")

    


def queryTestInfo(rootURL):
    global isForceQuery
    testGeneralInfo = BeautifulSoup(oaklet.get(rootURL).content,"lxml")
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
    #print(testGeneralInfo.find_all("a"))
    if testGeneralInfo.find_all("a") == []:
        print(Fore.RED + "目前该考试尚未出总成绩，直接查询相应学科可能成绩不准确!"+Fore.WHITE)
    else:
        print(Fore.CYAN + "该考试已出总成绩，可以获取总成绩信息。"+Fore.WHITE)
    for child in testGeneralInfo.find_all("li"):
        itemID = child.get('itemid')
        itemName = child.get_text()
        #print(itemID)
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
    #print(url)
    
    queryTestInfo(rootURL)

def MainMenu():
    global queryTestID,isForceQuery
    isForceQuery = ""
    print(Fore.MAGENTA+"0.退出\n1.查考试清单\n2.直查考试id\n3.退出登录")
    Mission = input(Fore.RED + "请选择要执行的任务:" + Fore.WHITE)
    if Mission=="2":
        queryTestID = input("请输入需要查询的考试 id:")
        url = "https://yue.hsdfz.com.cn/oaklet/student/listvalidsubjecthtmldata.html?pid=" + str(queryTestID)
        queryTestInfo(url)
    else:
        if Mission=="1":
            url = "https://yue.hsdfz.com.cn/oaklet/student/listprojectwithlinkhtmldata.html?uid="+ str(username)
            testListElement = BeautifulSoup(oaklet.get(url).content,'lxml')
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
            res = oaklet.get(url)
            print("已成功退出登录。")
            Login()
        else:
            print("\nBye\n")
            exit()

Start=Login()
