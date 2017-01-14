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
import mail
from time import sleep
import logging
import yaml


#TODO: Export performance metrics!
#TODO: Search audio extensions in Networking data
#TODO: Create requirements.txt and point dockerfile to use
#TODO: Create a base image

logging.basicConfig(filename='dataminer.log',level=logging.INFO)


class performance(object):
	#create performance data

	def __init__(self, mob_path):
		#initialize
		logging.info('**********************')
		logging.info('{}: Initializing...'.format(datetime.now())) 
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
		chromedriver = os.getenv("CHROMEDRIVER_PATH", "/chromedriver")
		os.environ["webdriver.chrome.driver"] = chromedriver
		url = urlparse.urlparse (self.proxy.proxy).path
		chrome_options = webdriver.ChromeOptions()
		chrome_options.add_argument("--proxy-server={0}".format(url))
		chrome_options.add_argument("--no-sandbox")
		chrome_options.add_argument('--dns-prefetch-disable') # TODO: Commit to base project # set env LANG=en_US.UTF-8 ./chromedriver ?
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
		logging.info('{}: Starting capture'.format(datetime.now())) 
		self.proxy.new_har(url, options={'captureHeaders': True})
		self.driver.get(url)
		result = json.dumps(self.proxy.har, ensure_ascii=False)
		logging.info('{}: Parsing...'.format(datetime.now())) 
		
		return self.__parse(result)
		
		# print '{}: Saving to disk'.format(datetime.now())
		# self.__store_into_file('har', result)
		# print '{}: Finished har, starting performance'.format(datetime.now())

		# performance = json.dumps(self.driver.execute_script("return window.performance"), ensure_ascii=False)
		# self.__store_into_file('perf', performance)
	

	def create_noads_har(self, url):
		noadsUrl = '{}?spotim_rc_override_tag=none'.format(url)
		logging.info('{}: Starting noads har capture'.format(datetime.now())) 
		self.proxy.new_har(noadsUrl, options={'captureHeaders': True})
		self.driver.get(noadsUrl)
		result = json.dumps(self.proxy.har, ensure_ascii=False)
		logging.info('{}: Parsing...'.format(datetime.now())) 
		
		return self.__parse(result)


	def output_msg(self, urlErrors, noadsUrlErrors, url):
		#TODO: Checkout email message foramt: http://stackoverflow.com/questions/882712/sending-html-email-using-python
		difference = (urlErrors-noadsUrlErrors)
		return [
				'Summary of analysis:',
				'Time: {}'.format(datetime.now()),
				'URL: {}'.format(url),
				'Found {} errors'.format(urlErrors), 
				'No ads mode: {} errors'.format(noadsUrlErrors), 
				'Difference: {}'.format(difference),
				'Spot relevant err percentage: {}%'.format((float(difference)/urlErrors)*100),
				'\n',
				'You are recieving this email since the difference error threshold has passed.'
				]
		

	def stop_all(self):
		#stop server and driver
		endTimeRecord = datetime.now()
		logging.info('{}: Done'.format(endTimeRecord)) 
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
			logging.info('Urls file empty') 
			exit(0)
		return urls
				

def fetch_conf():
	with open('conf.yml') as conf:
		dataMap = yaml.safe_load(conf)
	
	return dataMap


if __name__ == '__main__':
	conf = fetch_conf()['dataminer']
	# for headless execution
	with Xvfb() as xvfb:
		path = os.getenv('BROWSERMOB_PROXY_PATH', '/browsermob-proxy-2.1.2/bin/browsermob-proxy')
		RUN = performance(path)

		# Currently takes only first line of file ->
		startTime = 		RUN.start_all()
		urlErrors = 		RUN.create_har(conf['url'])
		noadsUrlErrors = 	RUN.create_noads_har(conf['url'])
		output = 			RUN.output_msg(urlErrors, noadsUrlErrors, conf['url']) 

		# Threshold test
		if (urlErrors-noadsUrlErrors) > conf['error_threshold'] and conf['email']:
			mail.send_mail(output)
			logging.info('{}: Emailing..'.format(datetime.now()))
		else:
			logging.info('Not emailing (urlErrors-noadsUrlErrors is {})'.format(urlErrors-noadsUrlErrors))		
			
		endTime = RUN.stop_all()
		logging.info('Completed in {} seconds'.format((endTime-startTime).seconds)) 

	logging.info('Sleeping {}'.format(conf['cycle_time']))
	sleep(conf['cycle_time'])
