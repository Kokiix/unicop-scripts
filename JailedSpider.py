import scrapy
import re
import json
import os

class JailedSpider(scrapy.Spider):
	"""
	Spider for scraping data from list of all US federal prisons into a json

	Run with:

	$ pip install scrapy
	$ scrapy runspider JailedSpider.py -s LOG_ENABLED=False
	"""

	name = "JailedSpider"
	start_urls = ["https://en.wikipedia.org/wiki/List_of_United_States_federal_prisons"]


	def parse(self, response):
		current_jail_num = -1
		current_prison_category = ""
		data_type_num = 0
		prison_data = {}

		page_html = response.xpath("/html/body/div[3]/div[3]/div[5]/div[1]").get()
		start_index = re.search(r'id="toc"', page_html).start()
		end_index = re.search(r'id="Former_federal_facilities"', page_html).start()
		page_html = page_html[start_index:end_index].split("\n")

		# for html_data in response.xpath("/html/body/div[3]/div[3]/div[5]/div[1]/table[1]/tbody/tr/td").getall():
		for html_line in page_html:
			if html_line.startswith("<h2>"):
				prison_cat = re.search(r'>[A-Z].+?<', html_line)
				if prison_cat != None:
					current_prison_category = prison_cat[0][1:-1]
					current_jail_num = -1
					prison_data[current_prison_category] = []
			elif html_line.startswith("<td>"):
				data = re.search(r'>[A-Z].+?(?:<|$)', html_line, flags = re.M)
				if data:
					data = data[0]
					if "," in data:
						prison_data[current_prison_category].append({"name": data[1:-1]})
						current_jail_num += 1
						data_type_num = 0
					else:
						current_jail = prison_data[current_prison_category][current_jail_num]
						field_name = ""
						match data_type_num:
							case 0:
								field_name = "location"
							case 1:
								field_name = "gender"
							case 2:
								field_name = "security_class"
						current_jail[field_name] = data[1:]
						data_type_num += 1

		file_name = os.path.dirname(__file__) + "/federal_prisons.json"
		if os.path.exists(file_name):
			os.remove(file_name)
		with open(file_name, "w") as f:
			json.dump(prison_data, f)
 