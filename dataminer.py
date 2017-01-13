#!/usr/bin/env python
# -*- coding: utf-8 -*-

from browsermobproxy import Server
from selenium import webdriver
from xvfbwrapper import Xvfb
from datetime import datetime
import json
import argparse
import urlparse
import sys
import os
import parser


class performance(object):
	#create performance data

	def __init__(self, mob_path):
		#initialize
		print '{}: Initializing...'.format(datetime.now())
		self.browser_mob = mob_path
		self.server = self.driver = self.proxy = None

	@staticmethod
	def __store_into_file(title, result):
		#store data collected into file
		har_file = open(title + '.json', 'w')
		har_file.write(result.encode('utf-8'))
	   	har_file.close()

	def __parse(self, result):
		return parser.parse_errors(json.loads(result))

	def __start_server(self):
		#prepare and start server
		self.server = Server(self.browser_mob)
		self.server.start()
		self.proxy = self.server.create_proxy()

	def __start_driver(self):
		#prepare and start driver
		#chromedriver
		print "Browser: Chrome"
		chromedriver = os.getenv("CHROMEDRIVER_PATH", "/chromedriver")
		os.environ["webdriver.chrome.driver"] = chromedriver
		url = urlparse.urlparse (self.proxy.proxy).path
		chrome_options = webdriver.ChromeOptions()
		chrome_options.add_argument("--proxy-server={0}".format(url))
		chrome_options.add_argument("--no-sandbox")
		chrome_options.add_argument('--dns-prefetch-disable') # TODO: Commit to base project
		self.driver = webdriver.Chrome(chromedriver,chrome_options = chrome_options)
		
		# Firefox ----->
		# Optional firefox driver in the future
		# print "Browser: Firefox"
		# profile = webdriver.FirefoxProfile()
		# profile.set_proxy(self.proxy.selenium_proxy())
		# self.driver = webdriver.Firefox(firefox_profile=profile)
			

	def start_all(self):
		#start server and driver
		self.__start_server()
		self.__start_driver()
		return datetime.now()

	def create_har(self, url):
		#start request and parse response
		print '{}: Starting capture'.format(datetime.now())
		self.proxy.new_har(url, options={'captureHeaders': True})
		self.driver.get(url)
		result = json.dumps(self.proxy.har, ensure_ascii=False)
		print '{}: Parsing...'.format(datetime.now())
		
		return self.__parse(result)
		
		# print '{}: Saving to disk'.format(datetime.now())
		# self.__store_into_file('har', result)
		# print '{}: Finished har, starting performance'.format(datetime.now())

		# performance = json.dumps(self.driver.execute_script("return window.performance"), ensure_ascii=False)
		# self.__store_into_file('perf', performance)
	
	def create_noads_har(self, url):
		noadsUrl = '{}?spotim_rc_override_tag=none'.format(url)
		print '{}: Starting noads har capture'.format(datetime.now())
		self.proxy.new_har(noadsUrl, options={'captureHeaders': True})
		self.driver.get(noadsUrl)
		result = json.dumps(self.proxy.har, ensure_ascii=False)
		print '{}: Parsing...'.format(datetime.now())
		
		return self.__parse(result)

	def comparison(self, urlErrors, noadsUrlErrors):
		# TODO: Improve - this should be called form main() after create_har() returns 2 vars
		difference = (urlErrors-noadsUrlErrors)
		
		return 'Url: {} errors, noads: {} errors, difference: {}'.format(urlErrors, noadsUrlErrors, difference)
		
	def stop_all(self):
		#stop server and driver
		endTimeRecord = datetime.now()
		print '{}: Done'.format(endTimeRecord)
		self.server.stop()
		self.driver.quit()

		return endTimeRecord

	def fetch_urls(self, urlsFileName):
		#read urls from file
		urls = []
		with open(urlsFileName, 'r') as urlsfile:
			for line in urlsfile:
				urls.append(line)
		
		if len(urls) == 0:
			print 'Urls file empty'
			exit(0)
		return urls
				

if __name__ == '__main__':

	urlsFileName = 'urls.txt'
	# for headless execution
	with Xvfb() as xvfb:
		# parser = argparse.ArgumentParser(description='Performance Testing using Browsermob-Proxy and Python')
		# parser.add_argument('-u','--url',help='URL to test',required=True)
		# parser.add_argument('-b','--browser',help='Select Chrome or Firefox',required=True)
		# parser.add_argument('-p','--path',help='Select path for output files',required=False)
		# args = vars(parser.parse_args())
		path = os.getenv('BROWSERMOB_PROXY_PATH', '/browsermob-proxy-2.1.2/bin/browsermob-proxy')
		RUN = performance(path)
		#Currently takes only first line of file

		url = 				RUN.fetch_urls(urlsFileName)[0]
		startTime = 		RUN.start_all()
		urlErrors = 		RUN.create_har(url)
		noadsUrlErrors = 	RUN.create_noads_har(url)
		output = 			RUN.comparison(urlErrors, noadsUrlErrors) #?


		endTime = RUN.stop_all()

		print 'Completed in {} seconds'.format((endTime-startTime).seconds)
