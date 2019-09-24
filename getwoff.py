#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author: ArcherTrister
# python3 环境
from fontTools.ttLib import TTFont
from fake_useragent import UserAgent
import requests
import random
import mysqlutils as db
import re
import os

ua = UserAgent()

#代理浏览器header
user_agent = [
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
    "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
    "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (iPod; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (iPad; U; CPU OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (Linux; U; Android 2.3.7; en-us; Nexus One Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U; en-GB) Presto/2.8.149 Version/11.10",
    "Mozilla/5.0 (Linux; U; Android 3.0; en-us; Xoom Build/HRI39) AppleWebKit/534.13 (KHTML, like Gecko) Version/4.0 Safari/534.13",
    "Mozilla/5.0 (BlackBerry; U; BlackBerry 9800; en) AppleWebKit/534.1+ (KHTML, like Gecko) Version/6.0.0.337 Mobile Safari/534.1+",
    "Mozilla/5.0 (hp-tablet; Linux; hpwOS/3.0.0; U; en-US) AppleWebKit/534.6 (KHTML, like Gecko) wOSBrowser/233.70 Safari/534.6 TouchPad/1.0",
    "Mozilla/5.0 (SymbianOS/9.4; Series60/5.0 NokiaN97-1/20.0.019; Profile/MIDP-2.1 Configuration/CLDC-1.1) AppleWebKit/525 (KHTML, like Gecko) BrowserNG/7.1.18124",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0; HTC; Titan)",
    "UCWEB7.0.2.37/28/999",
    "NOKIA5700/ UCWEB7.0.2.37/28/999",
    "Openwave/ UCWEB7.0.2.37/28/999",
    "Mozilla/4.0 (compatible; MSIE 6.0; ) Opera/UCWEB7.0.2.37/28/999",
]

#获取shopNum、tagName、address对应的woff文件URL
def get_woff_file(url):
    headers = {'User-Agent': random.choice(user_agent),  # 随机选取头部代理,防止被屏蔽
               'Connection': "keep-alive",
               'Host': "s3plus.meituan.net",
               'referer': 'http://www.dianping.com/',
               'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
               }
    #print("ING..........")
    r = requests.get(url, headers=headers)
    r.encoding = 'utf-8'
    #print(r.text)
    shopNumWoff = re.findall('@font-face{font-family: "PingFangSC-Regular-shopNum(.*?).woff', r.text, re.S)   
    tagNameWoff = re.findall('@font-face{font-family: "PingFangSC-Regular-tagName(.*?).woff', r.text, re.S)
    addressWoff = re.findall('@font-face{font-family: "PingFangSC-Regular-address(.*?).woff', r.text, re.S)
    r.close()
    savewoff(shopNumWoff,'shopNum.woff')
    savewoff(tagNameWoff,'tagName.woff')
    savewoff(addressWoff,'address.woff')
    update_dic()

#更新当前字库
def update_dic():
    #update_sqls = "update shopnum_dic a ,wofflatest b set a.word=b.word where a.position=b.position;update tagname_dic a ,wofflatest b set a.word=b.word where a.position=b.position;update address_dic a ,wofflatest b set a.word=b.word where a.position=b.position;"
    #insert_sqls = "insert into woff_dic select * from shopnum_dic where word in ('0','1','2','3','4','5','6','7','8','9');insert into woff_dic select * from tagname_dic where word not in ('0','1','2','3','4','5','6','7','8','9');insert into woff_dic select * from address_dic where word not in ('0','1','2','3','4','5','6','7','8','9');"
    #print(update_sqls)
    db.execute("update shopnum_dic a, wofflatest b set a.word=b.word where a.position=b.position;")
    db.execute("update tagname_dic a, wofflatest b set a.word=b.word where a.position=b.position;")
    db.execute("update address_dic a, wofflatest b set a.word=b.word where a.position=b.position;")
    db.execute("insert into woff_dic select * from shopnum_dic where word in ('0','1','2','3','4','5','6','7','8','9');")
    db.execute("insert into woff_dic select * from tagname_dic where word not in ('0','1','2','3','4','5','6','7','8','9');")
    db.execute("insert into woff_dic select * from address_dic where word not in ('0','1','2','3','4','5','6','7','8','9');")
    
#将获取的woff文件保存到本地便于解析存放点阵信息到数据库
def savewoff(woff,filename):
    headers = {'User-Agent': random.choice(user_agent),  # 随机选取头部代理,防止被屏蔽
               'Connection': "keep-alive",
               'Host': "s3plus.meituan.net",
               'referer': 'http://www.dianping.com/',
               'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
               }
    result = ''
    for tmp in woff:
        result = result + tmp
    woff2 = re.findall('url\(\"//(.*?);', result, re.S)
    resultb = ''
    for a in woff2:
        resultb = resultb + str(a).replace('eot', 'woff').replace(')', '').replace('"', '')
    #print(resultb)
    url = "https://" + resultb
    response_woff = requests.get(url, headers=headers).content
    with open(filename, 'wb') as f:
        f.write(response_woff)
    save_word(filename)

#解析woff字体文件进行解析
def save_word(filename):
    tablename=filename.replace('.woff','')+"_dic"
    font = TTFont(filename)
    glyf = font.get('glyf')
    result = font['cmap']
    sql_delete="truncate table %s"%(tablename)
    db.execute(sql_delete)
    cmap_dict = result.getBestCmap()
    insert_data = []
    for key, value in cmap_dict.items():
        k_tmp = str(hex(eval(str(key))))
        b = k_tmp.replace("0x", '')
        glyf = font.get('glyf')
        c = glyf[value]
        temp = (str(value), str(key), str(b), str(c.coordinates))
        insert_data.append(temp)
    
    #print(insert_data)
    sql_insert = "insert into {0} (name, ten_key, sixteen_key, position) values (%s, %s, %s, %s)".format(tablename)
    db.insertmany(sql_insert, insert_data)

#request 请求头部、由于此脚本请求不同的网页header信息不一致所以未设置全局变量
#解析woff字体库的数字类型
def test():
    headers = {'User-Agent': random.choice(user_agent),  # 随机选取头部代理,防止被屏蔽
               'Connection': "keep-alive",
               'Host': "www.dianping.com",
               'referer': 'http://www.dianping.com/',
               'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
              }
    #随机选取一家店铺获取WOFF文件
    sql="select shophref from dzcomment_shop ORDER BY RAND() LIMIT 1;"
    result=db.queryone(sql)
    if len(result)>0:
        url="http://"+result[0]
        try:
            r = requests.get(url, headers=headers)
            r.encoding = 'utf-8'
            #print(r.text)
            #print(url)
            woff_url = re.findall('//s3plus.meituan.net/v1/(.*?)"', r.text, re.S)
            r.close()
            #print(woff_url)
            if(len(woff_url)>0):
                result_url="https://s3plus.meituan.net/v1/"+woff_url[0]
                get_woff_file(result_url)
                return 1
            else:
                return "URL IS NULL"
        except Exception as e:
            print(e)
            return 0
    else:
        return 0

def get_html(page):
    RefererUrl = "http://www.dianping.com/kunming/ch10/g508p"+str(page-1)
    if page <= 1:
        RefererUrl = "http://www.dianping.com/"

    headers = {'User-Agent': random.choice(user_agent),  # 随机选取头部代理,防止被屏蔽
               'Connection': "keep-alive",
               'Host': "www.dianping.com",
               'Referer': RefererUrl,
               'Cookie': 's_ViewType=10; _lxsdk_cuid=16d6143f11bc8-0c5453cf7dc3fd-a7f1a3e-1fa400-16d6143f11bc8; _lxsdk=16d6143f11bc8-0c5453cf7dc3fd-a7f1a3e-1fa400-16d6143f11bc8; _hc.v=81a12ccd-68e8-d0e4-2648-d754f65fd0a3.1569294906; _lxsdk_s=16d6143f11c-d44-261-260%7C%7C42',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
              }
    url = "http://www.dianping.com/kunming/ch10/g508p"+str(page)

    # 当前时间目录路径
    dirs = url.replace("http://www.dianping.com/", "").split('/')
    pathStr = os.path.abspath('.') + "/htmls/" + dirs[0] + "/" + dirs[1]
    decodePathStr = pathStr + "/decode"
    # 是否存在
    isExists = os.path.exists(pathStr)
    # 不存在则创建
    if not isExists:
        os.makedirs(pathStr)

    if not os.path.exists(decodePathStr):
        os.makedirs(decodePathStr)

    fileName = pathStr + "/" + dirs[2]+".html"
    decodeFileName = decodePathStr + "/" + dirs[2]+".html"

    #检测文件是否存在
    if not os.path.exists(fileName):
        try:
            r = requests.get(url, headers=headers)
            r.encoding = 'utf-8'
            html = r.text
            #<div id="not-found-tip">
            errorPage = re.findall('您要访问的页面不存在(.*?)"', html, re.S)
            if(len(errorPage) > 0):
                print("出现验证，爬取失败")
                return
            with open(fileName, "w", encoding='utf-8') as f:
                f.write(html)
            if Flag:
                woff_url = re.findall('//s3plus.meituan.net/v1/(.*?)"', html, re.S)
                r.close()
                #print(woff_url)
                if(len(woff_url)>0):
                    result_url="https://s3plus.meituan.net/v1/"+woff_url[0]
                    get_woff_file(result_url)
                    dic_data = db.queryall("select sixteen_key, word from woff_dic")
                    print(dic_data)
                    Flag = True
                    return 1
                else:
                    return "URL IS NULL"
        except Exception as e:
            print(e)
            return 0

if __name__ == '__main__':
    #test()
    #update_dic()
    Flag = False

    get_html(2)
    #get_woff_file("http://s3plus.meituan.net/v1/mss_0a06a471f9514fc79c981b5466f56b91/svgtextcss/899802d452ba2c1503c2afe861089615.css")