#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..')
from base.spider import Spider
import re
import math

class Spider(Spider):
	def getName(self):
		return "体育直播"
	def init(self,extend=""):
		pass
	def isVideoFormat(self,url):
		pass
	def manualVideoCheck(self):
		pass
	def homeContent(self,filter):
		result = {}
		cateManual = {
			"全部": ""
		}
		classes = []
		for k in cateManual:
			classes.append({
				'type_name': k,
				'type_id': cateManual[k]
			})

		result['class'] = classes
		if (filter):
			result['filters'] = self.config['filter']
		return result
	def homeVideoContent(self):
		result = {}
		return result

	def categoryContent(self,tid,pg,filter,extend):
		result = {}
		url = 'http://www.fifa2022.tv/'
		rsp = self.fetch(url)
		html = self.html(rsp.text)
		aList = html.xpath("//tr[@class='against']")
		videos = []
		img = 'https://s1.ax1x.com/2022/10/07/x3NPUO.png'
		for a in aList:
			urlList = a.xpath("./td[@class='live_link']/a")
			time = a.xpath("./td[@class='tixing']/@t")[0].split(' ')[1]
			stat = a.xpath("./td/div[contains(@class, 'status')]/text()")
			if stat != []:
				stat = stat[0]
			else:
				stat = '未开始'
			if '比分' not in urlList[0].xpath("./text()")[0] and stat != '结束':
				remark = a.xpath("./td[@class='matcha']/a/text()")[0] + '|' + time
				teams = a.xpath("./td[@class='teama']/a/strong/text()")
				if teams != []:
					name = teams[0].strip('\t').strip() + 'VS' + teams[1].strip('\t').strip()
				else:
					nameList = a.xpath("./td[5]/text()")[0].split(' ')
					names = []
					for nL in nameList:
						if nL != '' and nL.lower() != 'vs':
							names.append(nL)
					if len(names) < 3:
						name = names[0] + 'VS' + name[1]
					else:
						name = names[-2] + 'VS' + name[-1]
				aid = ''
				for url in urlList:
					title = url.xpath("./text()")[0]
					aurl = url.xpath("./@href")[0]
					#aurl = self.regStr(reg=r'/tv/(.*?).html', src=aurl)
					if '比分' not in title:
						aid = aid + title + '@@@' + aurl + '#'
				videos.append({
					"vod_id": name + '###' + remark.split('|')[0] + '###' + aid,
					"vod_name": name,
					"vod_pic": img,
					"vod_remarks": remark
				})
		numvL = len(videos)
		pgc = math.ceil(numvL/15)
		result['list'] = videos
		result['page'] = pg
		result['pagecount'] = pgc
		result['limit'] = numvL
		result['total'] = numvL
		return result

	def detailContent(self,array):
		aid = array[0]
		aids = aid.split('###')
		name = aids[0]
		typeName = aids[1]
		tus = aids[2].strip('#').split('#')
		pic = 'https://s1.ax1x.com/2022/10/07/x3NPUO.png'
		vod = {
			"vod_id": name,
			"vod_name": name,
			"vod_pic": pic,
			"type_name": typeName,
			"vod_year": "",
			"vod_area": "",
			"vod_remarks": '',
			"vod_actor": '',
			"vod_director":'',
			"vod_content": ''
		}
		purl = ''
		for tu in tus:
			title = tu.split('@@@')[0]
			uid = tu.split('@@@')[1]
			purl = purl + '{0}${1}'.format(title,uid) + '#'
		vod['vod_play_from'] = '体育直播'
		vod['vod_play_url'] = purl
		result = {
			'list': [
				vod
			]
		}
		return result

	def searchContent(self,key,quick):
		result = {}
		return result

	def playerContent(self,flag,id,vipFlags):
		result = {}
		url = id.strip('#')
		rsp = self.fetch(url)
		root = self.html(rsp.text)
		phpurl = root.xpath("//div[@class='media']/iframe/@src")[0]
		headers = {
			"Referer": url,
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
		}
		rsp = self.fetch(phpurl,headers=headers,cookies=rsp.cookies)
		if 'm3u8' in rsp.text:
			if 'm3u8.html?id=' in rsp.text:
				purl = re.search(r'm3u8\.html\?id=(.*?m3u8.*?)\"', rsp.text.replace("\n",'').replace("\r",'')).group(1)
			else:
				purl = re.search(r"url: \'(.*?)\'", rsp.text.replace("\n",'').replace("\r",'')).group(1)
			if not purl.startswith('http'):
				purl = re.search(r"(.*)/", phpurl).group(1) + purl
		else:
			aurl = re.search(r"(.*)/", phpurl).group(1) + re.search(r'src=\"..(.*?)\"', rsp.text.replace("\n",'').replace("\r",'')).group(1)
			aheaders = {
				"Referer": url,
				"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
			}
			r = self.fetch(aurl, headers=aheaders, cookies=rsp.cookies)
			purl = re.search(r"url: \'(.*?)\'", r.text)
			if purl == None:
				purl = re.search(r'm3u8\.html\?id=(.*?)\"', r.text.replace("\n",'').replace("\r",''))
			purl = purl.group(1)
		result["parse"] = 0
		result["playUrl"] = ''
		result["url"] = purl
		result["header"] = ''
		return result

	config = {
		"player": {},
		"filter": {}
	}
	header = {}

	def localProxy(self,param):
		action = {
			'url':'',
			'header':'',
			'param':'',
			'type':'string',
			'after':''
		}
		return [200, "video/MP2T", action, ""]
