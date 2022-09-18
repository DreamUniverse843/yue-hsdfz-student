#============
#依赖库区
#============
from cgi import test
from imghdr import tests
import re
import requests
from colorama import init,Fore,Back,Style
from bs4 import BeautifulSoup
import pandas
import html5lib
#============

oaklet = requests.session() # 会话持久化自动保留 cookies

def Login():
    global username,password
    username=input("请输入用户名：")
    password=input("请输入密码：")
    res = oaklet.post("https://yue.hsdfz.com.cn/oaklet/j_spring_security_check?j_username="+ username +"&j_password="+ password +"&submit=%E7%99%BB%E3%80%80%E3%80%80%E5%BD%95")
    if("用户名或密码错误！" in res.text):
        print(Fore.RED+"用户名或密码错误，请检查用户名和密码是否正确。")
        Login()
    else:
        print(Fore.CYAN+"登录成功。")
        MainMenu()
    #print(Fore.MAGENTA+"是否需要储存用户信息?")
    #isUserInfoStorage=input(Fore.RED + "1 - 是，2 - 否\n")
    #if isUserInfoStorage=="2":
    #    MainMenu()
    #else:
    #    open("ProfileCache.txt","w",encoding='utf-8').write(username+"%%"+password)
    #    print("用户信息已保存。")
        

def getSpecificScore(rootURL,isTotal):
    testSpecificResult = BeautifulSoup(oaklet.get(rootURL).content,"lxml")
    #print(str(testSpecificResult))
    #print(testSpecificResult.find_all("table"))
    if isTotal == 0:
        paperID = re.findall(r"paperdataid=(.+)&amp;", str(testSpecificResult))[0]
        url = "https://yue.hsdfz.com.cn/oaklet/student/getuserexampaperdata.html?paperdataid="+ paperID + "&amp;utreeid="
        paperResult = pandas.DataFrame()
        paperResult = paperResult.append(pandas.read_html(str((BeautifulSoup(oaklet.get(url).content,"lxml").find_all("table")))))
        print(paperResult)
    else:
        testTotalResult = pandas.DataFrame()
        testTotalResult = testTotalResult.append(pandas.read_html(str(testSpecificResult.find_all("table"))))
        print(testTotalResult)



def queryTestInfo(rootURL):
    testGeneralInfo = BeautifulSoup(oaklet.get(rootURL).content,"lxml")
    #print(testGeneralInfo)
    if testGeneralInfo.find_all("li") == []:
        print(Fore.RED + "未获取到考试数据，考试 ID 可能无效。"+Fore.WHITE)
        MainMenu()
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
    global queryTestID
    print(Fore.MAGENTA+"0.退出\n1.查考试清单\n2.直查考试id")
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
            queryTestID = input("请输入需要查询的考试 id:")
            url = "https://yue.hsdfz.com.cn/oaklet/student/listvalidsubjecthtmldata.html?pid=" + str(queryTestID)
            queryTestInfo(url)
        else:
            print("\nBye\n")
            exit()

Start=Login()
