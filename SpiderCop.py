import scrapy
import re
import json
import os
from pathlib import Path

class SpiderCop(scrapy.Spider):
	"""
	Spider for scraping data from list of all US police agencies into a json
	"""

	name = "SpiderCop"
	start_urls = ["https://en.wikipedia.org/wiki/List_of_United_States_state_and_local_law_enforcement_agencies"]
	valid_headers = ["city", "county", "university", "college", "sheriff", "constable", "municipal"]
	current_dir = os.path.dirname(__file__)


	def parse(self, response):
		"""Start parsing every state from root list"""
		# Create directory for output
		Path(self.current_dir + "/state_data").mkdir(exist_ok = True)

		# Use regex to find links to states in html, then request the state page using that url
		# Once page is retreived, parse_state_page is called
		for state_url in response.xpath(r'/html/body/div[3]/div[3]/div[5]/div[1]/div[2]/ul/li/a').getall():
			yield scrapy.Request("https://en.wikipedia.org" + re.findall(r'/wiki/List_of_law_enforcement_agencies_in_\w+\"', state_url)[0][:-1], callback = self.parse_state_page)

		# SINGLE STATE TEST
		# return scrapy.Request("https://en.wikipedia.org/wiki/List_of_law_enforcement_agencies_in_Florida", callback = self.parse_state_page)


	def parse_state_page(self, response):
		"""
		Compile agency data and put it in json file for state
		"""
		state_json = {}
		current_header = None
		prev_line_start = ""

		# Cut off extra content above table of contents and below references to make searching easier
		page_html = response.xpath("/html/body/div[3]/div[3]/div[5]/div[1]").get()
		start_index = re.search(r'id="toc"', page_html).start()
		end_index = re.search(r'id="References"', page_html).start()
		page_html = page_html[start_index:end_index].split("\n")

		for html_line in page_html:
			# If the category (header) is relevant and the current html line has data,
			if current_header and (html_line.startswith("<li>") or html_line.startswith("<ul>")):
				# Get the agency from html line, then trim name
				agency = re.search(r'>[A-Z].+?<', html_line)
				if agency:
					agency = {"name":agency[0][1:-1]}

					# Add agency to JSON as normal item or sublist: data is sublist IF current line is <ul> instead of <li> and previous item also has data
					if html_line.startswith("<ul>") and (prev_line_start == "<ul>" or prev_line_start == "<li>"):
						parent_list = state_json[current_header][-1]
						if "sublist" not in parent_list:
							parent_list["sublist"] = []
						parent_list["sublist"].append(agency)
					else:
						state_json[current_header].append(agency)
				
			elif html_line.startswith("<h2>"):
				# Get the header from html line, then trim name
				current_header = re.search(r'>[A-Z].+?<', html_line)
				if current_header:
					current_header = current_header[0][1:-1]
					flag = False
					# Check if header is valid
					for valid_header in self.valid_headers:
						if valid_header in current_header.lower():
							flag = True
							break
							
					if flag:
						state_json[current_header] = []
					else:
						current_header = None
			# Previous line is needed to know if data is part of a sublist or not
			prev_line_start = html_line[0:4]

		# Write JSON data to file
		state_name = response.url.rsplit("in_", 1)[1].replace("_", " ")
		file_name = self.current_dir + "/state_data/" + state_name + ".json"
		if os.path.exists(file_name):
			os.remove(file_name)
		with open(file_name, "w") as state_json_file:
			json.dump(state_json, state_json_file)
 