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

ua = UserAgent()

#获取shopNum、tagName、address对应的woff文件URL
def get_woff_file(url):
    headers = {'User-Agent': ua.random,  # 随机选取头部代理,防止被屏蔽
               'Connection': "keep-alive",
               'Host': "s3plus.meituan.net",
               'referer': 'http://www.dianping.com/',
               'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
               }
    #print("ING..........")
    r = requests.get(url, headers=headers)
    r.encoding = 'utf-8'
    shopNumWoff = re.findall('@font-face{font-family: "PingFangSC-Regular-shopNum(.*?).woff', r.text, re.S)   
    tagNameWoff = re.findall('@font-face{font-family: "PingFangSC-Regular-tagName(.*?).woff', r.text, re.S)
    addressWoff = re.findall('@font-face{font-family: "PingFangSC-Regular-address(.*?).woff', r.text, re.S)
    savewoff(shopNumWoff,'shopNum.woff')
    savewoff(tagNameWoff,'tagName.woff')
    savewoff(addresswoff,'address.woff')
    update_dic()

#更新当前字库
#update shopnum_dic a ,wofflatest b set a.word=b.word  where a.position=b.position;
#update tagname_dic a ,wofflatest b set a.word=b.word  where a.position=b.position;
#update address_dic a ,wofflatest b set a.word=b.word  where a.position=b.position;
#insert into woff_dic select * from shopnum_dic  where word in ('0','1','2','3','4','5','6','7','8','9');
#insert into woff_dic select * from tagname_dic where word not in ('0','1','2','3','4','5','6','7','8','9');
#insert into woff_dic select * from address_dic where word not in ('0','1','2','3','4','5','6','7','8','9');
def update_dic():
    update_sqls = '''
                    update shopnum_dic a ,wofflatest b set a.word=b.word  where a.position=b.position;
                    update tagname_dic a ,wofflatest b set a.word=b.word  where a.position=b.position;
                    update address_dic a ,wofflatest b set a.word=b.word  where a.position=b.position;
                '''
    insert_sqls = '''
                    insert into woff_dic select * from shopnum_dic  where word in ('0','1','2','3','4','5','6','7','8','9');
                    insert into woff_dic select * from tagname_dic where word not in ('0','1','2','3','4','5','6','7','8','9');
                    insert into woff_dic select * from address_dic where word not in ('0','1','2','3','4','5','6','7','8','9');
                '''
    print(update_sqls)
    #db.execute(update_sqls)
    #db.execute(insert_sqls)
    
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
        temp = (tablename, value, key, b, c.coordinates)
        insert_data.append(temp)
    
    sql_insert = "insert into %s (name,ten_key,sixteen_key,position) values (\'%s\',%s,\'%s\',\'%s\')"
    db.insertmany(sql_insert, insert_data)

#request 请求头部、由于此脚本请求不同的网页header信息不一致所以未设置全局变量
#解析woff字体库的数字类型
def test():
    headers = {'User-Agent': ua.random,  # 随机选取头部代理,防止被屏蔽
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

if __name__ == '__main__':
    #test()
    update_dic()
    #get_woff_file("http://s3plus.meituan.net/v1/mss_0a06a471f9514fc79c981b5466f56b91/svgtextcss/899802d452ba2c1503c2afe861089615.css")