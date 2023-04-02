#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..') 
from base.spider import Spider
import json
import time
import base64
import re
from urllib import request, parse
import urllib
import urllib.request

class Spider(Spider):  # 元类 默认的元类 type
	def getName(self):
		return "胖虎免费svip影视"#地址发布页:https://www.webqq.ml/
	def init(self,extend=""):
		print("============{0}============".format(extend))
		pass
	def isVideoFormat(self,url):
		pass
	def manualVideoCheck(self):
		pass
	def homeContent(self,filter):
		result = {}
		cateManual = {
			"今日更新":"new",
			"电影": "1",
			"剧集":"2",
			"动漫":"4",
			"综艺":"3"
		}
		classes = []
		for k in cateManual:
			classes.append({
				'type_name':k,
				'type_id':cateManual[k]
			})
		result['class'] = classes
		if(filter):
			result['filters'] = self.config['filter']
		return result
	def homeVideoContent(self):
		rsp = self.fetch('https://www.panghuys.com/',headers=self.header)
		htmlTxt=rsp.text
		videos = self.get_list(html=htmlTxt,patternTxt=r'<a href="(?P<url>/v/.+?\.html)" title="(?P<title>.+?)" class=".*?"><div class=".*?"><div class=".*?">.*?</div><div class="module-item-pic"><img class=".*?" data-original="(?P<img>.+?)"')
		result = {
			'list':videos
		}
		return result
	def categoryContent(self,tid,pg,filter,extend):
		result = {}
		videos=[]
		if tid=='new' and int(pg)>1:
			return result
		url='https://www.panghuys.com/vodshow/{0}/page/{1}.html'.format(tid,pg)
		if tid=='new':
			url='https://www.panghuys.com/label/new.html'
		rsp = self.fetch(url,headers=self.header)
		htmlTxt=rsp.text
		videos = self.get_list(html=htmlTxt,patternTxt=r'<a\shref="(?P<url>/v/.{4,20}\.html)"\stitle="(?P<title>.+?)"\sclass=".+?"><div class=".+?"><div class=".+?">(.*?)</div><div class=".+?"><img\sclass=".+?"\sdata-original="(?P<img>.+?)"')
		pag=self.get_RegexGetText(Text=htmlTxt,RegexText=r'<a\shref="/vodshow/[0-9]/page/([0-9]+?).html"\sclass="page-link page-next"\stitle="尾页">',Index=1)
		if pag=="":
			pag=999
		numvL = len(videos)
		result['list'] = videos
		result['page'] = pg
		result['pagecount'] = pag
		result['limit'] = numvL
		result['total'] = numvL
		return result
	def detailContent(self,array):
		result = {}
		aid = array[0].split('###')
		url = aid[1]
		title = aid[0]
		logo = aid[2]
		if len(url)<4:
			return result
		url='https://www.panghuys.com'+url
		rsp = self.fetch(url,headers=self.header)
		htmlTxt=rsp.text
		playFrom = []
		videoList=[]
		vodItems = []
		line=self.get_RegexGetTextLine(Text=htmlTxt,RegexText=r'<div\sclass=".+?"\sdata-dropdown-value="(.+?)">',Index=1)
		circuit=self.get_lineList(Txt=htmlTxt,mark=r'class="module-play-list">',after='</div>')
		for v in circuit:
			ListRe=re.finditer('<a class="module-play-list-link" href="(?P<href>.+?)" title=".*?">(<span>){0,1}(?P<title>.+?)(</span>){0,1}</a>', v, re.M|re.S)
			vodItems = []
			for value in ListRe:
				vodItems.append(value.group('title')+"$"+value.group('href'))
			joinStr = "#".join(vodItems)
			videoList.append(joinStr)
		vod_play_from='$$$'.join([self.removeHtml(txt=t) for t in line])
		vod_play_url = "$$$".join(videoList)
		typeName=self.get_RegexGetText(Text=htmlTxt,RegexText=r'<a href="/vodshow/\d+?/class/.+?.html">(.+?)</a>',Index=1)
		year=self.get_RegexGetText(Text=htmlTxt,RegexText=r'<a title="(\d{4})" href="/vodshow/\d+?/year/\d{4}.html">',Index=1)
		dir=self.get_RegexGetText(Text=htmlTxt,RegexText=r'<a href="/phsch/director/.*?.html" target="_blank">(.*?)</a>',Index=1)
		act=self.get_RegexGetText(Text=htmlTxt,RegexText=r'主演：(.*?)更新：',Index=1)
		cont=self.get_RegexGetText(Text=htmlTxt,RegexText=r'<div class="module-info-introduction-content show-desc".*?>(.*?)</div>',Index=1)
		vod = {
			"vod_id":array[0],
			"vod_name":title,
			"vod_pic":logo,
			"type_name":self.removeHtml(txt=typeName),
			"vod_year":year,
			"vod_area":'',
			"vod_remarks":"",
			"vod_actor":self.removeHtml(txt=act),
			"vod_director":self.removeHtml(txt=dir),
			"vod_content":self.removeHtml(txt=cont)
		}
		vod['vod_play_from'] = vod_play_from
		vod['vod_play_url'] =vod_play_url
		result = {
			'list':[
				vod
			]
		}
		return result

	def searchContent(self,key,quick):
		Url='https://www.panghuys.com/phsch.html?wd={0}'.format(urllib.parse.quote(key))
		rsp = self.fetch(Url,headers=self.header)
		htmlTxt=rsp.text
		videos = self.get_list(html=htmlTxt,patternTxt=r'<a href="(?P<url>/v/.+?\.html)" class=".*?"><div class=".*?"><div class=".*?">.+?</div><div class=".*?"><img class=".*?" data-original="(?P<img>.+?)"\salt="(?P<title>.+?)"')
		result = {
			'list':videos
		}
		return result
	def playerContent(self,flag,id,vipFlags):
		result = {}
		parse=1
		Url='https://www.panghuys.com{0}'.format(id)
		rsp = self.fetch(Url,headers=self.header)
		htmlTxt = rsp.text
		m3u8Line=self.get_RegexGetTextLine(Text=htmlTxt,RegexText=r'url":"(h.+?)",',Index=1)
		if len(m3u8Line)>0:
			Url=m3u8Line[0].replace("/","")
		if Url.find('.m3u8')<1:
			parse=0
			Url='https://www.panghuys.com{0}'.format(id)
		result["parse"] = parse
		result["playUrl"] = ''
		result["url"] = Url
		result["header"] = ''
		return result
	def ifJx(self,urlTxt):
		Isjiexi=0
		RegexTxt=r'(youku.com|v.qq|bilibili|iqiyi.com|xigua.com)'
		if self.get_RegexGetText(Text=urlTxt,RegexText=RegexTxt,Index=1):
			Isjiexi=1
		return Isjiexi
	def get_RegexGetText(self,Text,RegexText,Index):
		returnTxt=""
		Regex=re.search(RegexText, Text, re.M|re.S)
		if Regex is not None:
			returnTxt=Regex.group(Index)
		return returnTxt	
	def get_list(self,html,patternTxt):
		ListRe=re.finditer(patternTxt, html, re.M|re.S)
		videos = []
		i=0
		for vod in ListRe:
			lastVideo = vod.group('url')
			title =vod.group('title')
			img =vod.group('img')
			if img.find('http')!=0:
				img='https://www.panghuys.com'+img
			if len(lastVideo) == 0:
				lastVideo = '_'
			videos.append({
				"vod_id":"{0}###{1}###{2}".format(title,lastVideo,img),
				"vod_name":title,
				"vod_pic":img,
				"vod_remarks":''
			})
		return videos
	def get_RegexGetTextLine(self,Text,RegexText,Index):
		returnTxt=[]
		pattern = re.compile(RegexText, re.M|re.S)
		ListRe=pattern.findall(Text)
		if len(ListRe)<1:
			return returnTxt
		for value in ListRe:
			returnTxt.append(value)	
		return returnTxt
	def get_lineList(self,Txt,mark,after):
		circuit=[]
		origin=Txt.find(mark)
		while origin>8:
			end=Txt.find(after,origin)
			circuit.append(Txt[origin:end])
			origin=Txt.find(mark,end)
		return circuit
	def removeHtml(self,txt):
		soup = re.compile(r'<[^>]+>',re.S)
		txt =soup.sub('', txt)
		return txt.replace("&nbsp;"," ")
	config = {
		"player": {},
		"filter": {}
		}
	header = {
		"Referer": 'https://www.panghuys.com/',
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
		'Host': 'www.panghuys.com'

	}

	def localProxy(self,param):
		return [200, "video/MP2T", action, ""]