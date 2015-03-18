# coding: UTF-8
# -1 彩蛋功能：输入昵称会显示照片
# -2 活动报名
# -3 最近活动
# -3.5 活动收款
# -3.6 精彩活动集
# -3.7 全部历史活动 #可添加2014.1类似搜索
# -3.8 个人游记集合
# -4 团购信息
# -5 团购报名
# -6 帮助
# -7 关于驴途户外
# -8 微社区

# -9 对微信公众平台可能分享的内容分类，便于建立数据库，如活动类，攻略类，科普类，团购类，等等
#
#回复括号内的关键字可查询相关内容：
#【最近活动】 未来计划组织的活动
#【活动回顾YYYYMM】 如【活动回顾201405】，可查询2014年5月的活动回顾
#【知识库】 最近发布的10条户外知识
#【知识XXX】 如【知识岩降】可查询岩降相关的户外知识
#【团购】 当前正在进行的团购活动
#【关于驴途】
#【留言建议】//待添加

import os
import sae
import web
import hashlib
import lxml
from lxml import etree
import time
import logging
from datetime import date

import sae.const

urls = (
    '/', 'weixin',
    '/db/insert', 'dbinset',
    '/home', 'home',
    '/index', 'index'
)

app_root = os.path.dirname(__file__)
templates_root = os.path.join(app_root, 'www')
render = web.template.render(templates_root)

logger = logging.getLogger("LVTUHUWAI")
console = logging.StreamHandler()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(name)s:%(asctime)s:%(levelname)s:  %(message)s")
console.setFormatter(formatter)
logger.addHandler(console)

db = web.database(dbn='mysql', host=sae.const.MYSQL_HOST, port=int(sae.const.MYSQL_PORT), user=sae.const.MYSQL_USER, pw=sae.const.MYSQL_PASS, db=sae.const.MYSQL_DB)

REPLY_TEXT = """<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%s</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[%s]]></Content>
</xml>"""

REPLY_IMAGETEXT = """<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%s</CreateTime>
<MsgType><![CDATA[news]]></MsgType>
<ArticleCount>%s</ArticleCount>
<Articles>
%s
</Articles>
</xml>"""

REPLY_IMAGETEXT_ARTICLE = """<item>
<Title><![CDATA[%s]]></Title> 
<Description><![CDATA[%s]]></Description>
<PicUrl><![CDATA[%s]]></PicUrl>
<Url><![CDATA[%s]]></Url>
</item>"""

REPLY_TEST = """<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%s</CreateTime>
<MsgType><![CDATA[news]]></MsgType>
<ArticleCount>1</ArticleCount>
<Articles>
<item>
<Title><![CDATA[活动报名——微店]]></Title> 
<Description><![CDATA[Hello World 这只是一个测试]]></Description>
<PicUrl><![CDATA[http://mmbiz.qpic.cn/mmbiz/qnkGqV3MOfhHYVNRPtk7Of9D9k961tJ2RS6uuK8o1IODYrP1AKyPxBFgtqyP4iaEOjw7aOVeK7rdMkKXscicgn3w/0]]></PicUrl>
<Url><![CDATA[http://t.cn/htlxt]]></Url>
</item>
</Articles>
</xml> 
"""

TEMPLATE_FORM_CHECKBOX = '''
<input type="checkbox" name="tags" id="%s" value="%s">
<label for="%s">%s</label>
'''

TEMPLATE_FORM_CHECKBOX_CHECKED = '''
<input type="checkbox" name="tags" id="%s" value="%s" checked>
<label for="%s">%s</label>
'''

TAGS_KEY = ["dengshan", "luying", "shuxingxing", "fubai", "qiaojiang", "huaxue", "yanjiang", "panyan", "shanghua", "caoyan", "shamo", "meishi", "meijing", "qinzi", "zhuangbei", "tubu"]
TAGS_VALUE = [u"登山", u"露营", u"数星星", u"腐败", u"速降", u"滑雪", u"岩降", u"攀岩", u"赏花", u"草原", u"沙漠", u"美食", u"美景", u"亲子", u"装备", u"徒步"]

class weixin:
    def GET(self):
        data = web.input()
        try:
            signature = data.signature
        except:
            return "Dear, are you lost?"
        timestamp = data.timestamp
        nonce = data.nonce
        echostr = data.echostr
        token = "123lvtuhuwai321"
        
        list = [token, timestamp, nonce]
        list.sort()
        
        sha1 = hashlib.sha1()
        map(sha1.update, list)
        hashcode = sha1.hexdigest()
        
        if hashcode == signature:
            return echostr
        else:
            return "Dear, are you lost?"
        

    def POST(self):
        str_xml = web.data()
        xml = etree.fromstring(str_xml)
        try:
            content = xml.find("Content").text
        except:
            content = ""
        msgType = xml.find("MsgType").text
        fromUser = xml.find("FromUserName").text
        toUser = xml.find("ToUserName").text
        try:
            event = xml.find("Event").text
        except:
            event = ""
        if msgType == "text":
            if content in [u"帮助", "help", "HELP", "Help"] or u"帮助" in content:
                return REPLY_TEXT % (fromUser, toUser, str(int(time.time())), u"回复关键字可查询相关内容：\n\n「最近活动」未来计划组织的活动\n「回顾YYYYMM」如'回顾201405'，可查询2014年5月的活动回顾\n「话题」最近发布的10篇户外话题\n「知识库」最近发布的10篇户外知识\n「知识XXX」如'知识岩降'可查询岩降相关的户外知识\n「团购」当前正在进行的团购活动\n「关于驴途」驴途户外介绍\n")
            elif content == u"最近活动":
                #DESC 倒序 ASC 正序
                results = db.select('articles', where="time>='"+str(date.today())+u"' and type='活动'", limit=10, order="time ASC")
                if len(results)==0:
                    return REPLY_TEXT % (fromUser, toUser, str(int(time.time())), u"最近无活动")
                articles = ""
                for result in results:
                    title = result["title"]
                    description = result["description"]
                    pic_url = result["pic_url"]
                    url = result["url"]
                    articles += REPLY_IMAGETEXT_ARTICLE % (title, description, pic_url, url)

                return REPLY_IMAGETEXT % (fromUser, toUser, str(int(time.time())), str(len(results)), articles)
            elif content == u"报名":
                return REPLY_TEST % (fromUser, toUser, str(int(time.time())))
            elif content.startswith(u"回顾") and len(content)==8:
                year = content[2:6]
                month = content[6:8]
                from_date = year+"-"+month+"-01"
                to_date = year+"-"+str(int(month)+1)+"-01"
                if(int(month)+1 == 13):
                    to_date = str(int(year)+1)+"-01-01"
                results = db.select('articles', where="time>='"+from_date+"' and "+"time<'" + to_date + "'" + u" and type='活动'", limit=10, order="time ASC")
                if len(results)==0:
                    return REPLY_TEXT % (fromUser, toUser, str(int(time.time())), year + u"年" + month + u"月无活动记录")
                articles = ""
                for result in results:
                    title = result["title"]
                    description = result["description"]
                    pic_url = result["pic_url"]
                    url = result["url"]
                    articles += REPLY_IMAGETEXT_ARTICLE % (title, description, pic_url, url)

                return REPLY_IMAGETEXT % (fromUser, toUser, str(int(time.time())), str(len(results)), articles)
            elif content == u"话题":
                results = db.select('articles', where=u"type='话题'", limit=10, order="time DESC")
                articles = ""
                for result in results:
                    title = result["title"]
                    description = result["description"]
                    pic_url = result["pic_url"]
                    url = result["url"]
                    articles += REPLY_IMAGETEXT_ARTICLE % (title, description, pic_url, url)

                return REPLY_IMAGETEXT % (fromUser, toUser, str(int(time.time())), str(len(results)), articles)
            elif content == u"知识库":
                results = db.select('articles', where=u"type='知识'", limit=10, order="time DESC")
                articles = ""
                for result in results:
                    title = result["title"]
                    description = result["description"]
                    pic_url = result["pic_url"]
                    url = result["url"]
                    articles += REPLY_IMAGETEXT_ARTICLE % (title, description, pic_url, url)

                return REPLY_IMAGETEXT % (fromUser, toUser, str(int(time.time())), str(len(results)), articles)
            elif content == u"团购":
                results = db.select('articles', where="time>='"+str(date.today())+u"' and type='团购'", limit=10, order="time ASC")
                if len(results)==0:
                    return REPLY_TEXT % (fromUser, toUser, str(int(time.time())), u"最近无团购")
                articles = ""
                for result in results:
                    title = result["title"]
                    description = result["description"]
                    pic_url = result["pic_url"]
                    url = result["url"]
                    articles += REPLY_IMAGETEXT_ARTICLE % (title, description, pic_url, url)

                return REPLY_IMAGETEXT % (fromUser, toUser, str(int(time.time())), str(len(results)), articles)
            elif content == u"关于驴途":
                return REPLY_TEXT % (fromUser, toUser, str(int(time.time())), u"驴途户外QQ群：10418828")
            elif content.startswith(u"知识") and not content.startswith(u"知识库"):
                key = content[2: len(content)]
                results = db.select('articles', where=u"type='知识' AND tags LIKE '" + key +"'", limit=10, order="time ASC")
                if len(results)==0:
                    return REPLY_TEXT % (fromUser, toUser, str(int(time.time())), u"无与'" + key + u"'相关的户外知识")
                articles = ""
                for result in results:
                    title = result["title"]
                    description = result["description"]
                    pic_url = result["pic_url"]
                    url = result["url"]
                    articles += REPLY_IMAGETEXT_ARTICLE % (title, description, pic_url, url)

                return REPLY_IMAGETEXT % (fromUser, toUser, str(int(time.time())), str(len(results)), articles)
            else:
                return REPLY_TEXT % (fromUser, toUser, str(int(time.time())), u"驴途户外感谢与你一起度过的美好时光。回复“帮助”，了解更多功能。")
        elif msgType == "event":
            if event == "subscribe":
                return REPLY_TEXT % (fromUser, toUser, str(int(time.time())), 
                    u"驴途户外——磨房天津站，三岁啦~\n\n无论你是因为驴途而户外，还是因为户外而选择了驴途，这三年的从无到有、从小到大、从山川河流到草原雪山，我们走过的和未走过的，组成了你我眼中的世界。\n2014年，你有没有心中向往的自由之地，想去那里走走看看，可以写下来，你的向往就是驴途未来要去到的远方~\n下一个三年，驴途还将伴你闯天涯，伴你走遍大江南北~\n\n回复“帮助”，了解更多功能。")

class dbinset:
    def GET(self):
        tags = ""
        for i in TAGS_KEY:
            if i == "dengshan":
                tags += TEMPLATE_FORM_CHECKBOX_CHECKED % (i, i, i, TAGS_VALUE[TAGS_KEY.index(i)])
            else:
                tags += TEMPLATE_FORM_CHECKBOX % (i, i, i, TAGS_VALUE[TAGS_KEY.index(i)])
        return render.index(tags)

    def POST(self):
        data = web.input(tags=[])
        type = data.type
        title = data.title
        description = data.description
        time = data.time
        pic_url = data.pic_url
        url = data.url
        tags = data.tags
        tags_value = []
        for tag in tags:
            tags_value.append(TAGS_VALUE[TAGS_KEY.index(tag)])
        try:
            db.insert("articles", type=type, title=title, description=description, time=time, pic_url=pic_url, url=url, tags=",".join(tags_value))
        except:
            return "Database Insert Error"
        raise web.seeother('/home')

class home:
    def GET(self):
        return render.home()

web.config.debug = False
app = web.application(urls, globals()).wsgifunc()
application = sae.create_wsgi_app(app)