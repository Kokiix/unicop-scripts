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
		data_type_num = 0
		prison_data = {"United States penitentiaries": []}

		for html_data in response.xpath("/html/body/div[3]/div[3]/div[5]/div[1]/table[1]/tbody/tr/td").getall():
			data = re.findall(r'>[A-Z].+?\n', html_data)
			if data:
				data = data[0]
				if "," in data:
					prison_data["United States penitentiaries"].append({"name": data[1:-5]})
					current_jail_num += 1
					data_type_num = 0
				else:
					current_jail = prison_data["United States penitentiaries"][current_jail_num]
					field_name = ""
					match data_type_num:
						case 0:
							field_name = "location"
						case 1:
							field_name = "gender"
						case 2:
							field_name = "security_class"
					current_jail[field_name] = data[1:-1]
					data_type_num += 1

		print(json.dumps(prison_data, indent=4))
		# file_name = os.path.dirname(__file__) + "federal_prisons.json"
		# if os.path.exists(file_name):
		# 	os.remove(file_name)
		# with open(file_name, "w") as f:
		# 	json.dump(AAAAAAAA, f)
 