import os
import json
import argparse
import random
from matplotlib import pyplot as plt
import requests

TEMP_DIR = 'temp/'

SHOW_START_TAG = '<td data-label="Show" class="col-0">'
END_TAG = '</tr>'
LINK_MARKER = '<a href='
LINK_ENDER = '</a>'

SHOW_GROSS_TAG = '<td data-label="Week Ending" class="col-0">'

# Keys
LINK_KEY = 'link'
THEATER_KEY = 'theater'
GROSS_KEY = 'gross'
DIFF_KEY = 'diff'
AVG_TICKET_KEY = 'avg_ticket'
TOP_TICKET_KEY = 'top_ticket'
SEATS_SOLD_KEY = 'seats_sold'
SEATS_IN_THEATER_KEY = 'seats_in_theater'
PERFORMANCES_KEY = 'num_performances'
PREVIEWS_KEY = 'num_previews'
CAPACITY_KEY = 'percent_capacity'
DIFF_CAP_KEY = 'diff_capacity'
WEEK_NUM_KEY = 'week_num'
RECENTNESS_KEY = 'recent'

MONTH_MAP = {'Jan': '01',
			 'Feb': '02',
			 'Mar': '03',
			 'Apr': '04',
			 'May': '05',
			 'Jun': '06',
			 'Jul': '07',
			 'Aug': '08',
			 'Sep': '09',
			 'Oct': '10',
			 'Nov': '11',
			 'Dec': '12'}

def get_args():
	arg_parser = argparse.ArgumentParser(description='get_data.py: get Playbill Broadway Grosses data')
	# arg_parser.add_argument('inputLink', type=str)
	return arg_parser.parse_args()

def make_tempfile():
	os.system('mkdir -p ' + TEMP_DIR)
	rand_num = random.randint(0, 1000)
	tempfile = TEMP_DIR + 'tempfile' + str(rand_num) + '.txt'
	return tempfile

def remove_tempfile(tempfile):
	os.system('rm ' + tempfile)
	os.system('rm -r ' + TEMP_DIR)

def get_webpage(link):
	tempfile = make_tempfile()
	
	os.system('curl -s ' + link + ' --output ' + tempfile)

	lines = []
	for line in open(tempfile, 'r'):
		lines.append(line.strip())

	remove_tempfile(tempfile)

	return lines

def get_hard_to_get_webpage(link):
	url_result = requests.get(link)

	lines = []
	for line in str(url_result.content).split('\\n'):
		line = line.replace('\\t', '\t').replace('\\"', '"')
		lines.append(line.strip())

	return lines

def process_span_line(line):
	return line.split('>')[1].split('<')[0]

def process_grosses(lines):
	index = 0
	show_grosses = dict()
	while index < len(lines):
		show = dict()
		showname = ""
		while lines[index] != SHOW_START_TAG:
			index += 1
			if index >= len(lines):
				return show_grosses
		index += 1

		# Link
		show[LINK_KEY] = lines[index].split('"')[1]
		index += 1

		# Showname
		showname = process_span_line(lines[index]).replace('&amp; ', "&").replace('&#039;', "'")
		index += 2

		# Theater
		show[THEATER_KEY] = process_span_line(lines[index])
		index += 3

		# Weekly Gross
		show[GROSS_KEY] = process_span_line(lines[index])
		index += 4

		# Weekly Gross Difference
		show[DIFF_KEY] = process_span_line(lines[index])
		index += 3

		# Average Ticket Cost
		show[AVG_TICKET_KEY] = process_span_line(lines[index])
		index += 1
		show[TOP_TICKET_KEY] = process_span_line(lines[index])
		index += 3

		# Seats Sold
		show[SEATS_SOLD_KEY] = process_span_line(lines[index])
		index += 1
		show[SEATS_IN_THEATER_KEY] = process_span_line(lines[index])
		index += 3

		# Performances and Previews
		show[PERFORMANCES_KEY] = process_span_line(lines[index])
		index += 1
		show[PREVIEWS_KEY] = process_span_line(lines[index])
		index += 3

		# Capacity Percentage
		show[CAPACITY_KEY] = process_span_line(lines[index])
		index += 3

		# Difference in Capacity Percentage
		show[DIFF_CAP_KEY] = process_span_line(lines[index])
		index += 1

		show_grosses[showname] = show
	return show_grosses

def process_show_gross_page(link, recent_val):
	lines = get_hard_to_get_webpage(link)

	index = 0
	show_gross_page = dict()
	while index < len(lines):
		grosses = dict()
		week_end_date = ""
		while lines[index] != SHOW_GROSS_TAG:
			index += 1
			if index >= len(lines):
				return show_gross_page, recent_val
		index += 1

		# End Date
		week_end_date_unprocessed = process_span_line(lines[index])
		month_and_day = week_end_date_unprocessed.split(',')[0]
		month = MONTH_MAP[month_and_day.split(' ')[0]]
		day = month_and_day.split(' ')[1]
		if len(day) < 2:
			day = '0' + day
		week_end_date = week_end_date_unprocessed.split(',')[1].strip() + '-' + month + '-' + day
		index += 3

		# Week Number
		grosses[WEEK_NUM_KEY] = process_span_line(lines[index])
		index += 3

		# Weekly Gross
		grosses[GROSS_KEY] = process_span_line(lines[index])
		index += 4

		# Weekly Gross Difference
		grosses[DIFF_KEY] = process_span_line(lines[index])
		index += 3

		# Average Ticket Cost
		grosses[AVG_TICKET_KEY] = process_span_line(lines[index])
		index += 1
		grosses[TOP_TICKET_KEY] = process_span_line(lines[index])
		index += 3

		# Seats Sold
		grosses[SEATS_SOLD_KEY] = process_span_line(lines[index])
		index += 1
		grosses[SEATS_IN_THEATER_KEY] = process_span_line(lines[index])
		index += 3

		# Performances and Previews
		grosses[PERFORMANCES_KEY] = process_span_line(lines[index])
		index += 1
		grosses[PREVIEWS_KEY] = process_span_line(lines[index])
		index += 3

		# Capacity Percentage
		grosses[CAPACITY_KEY] = process_span_line(lines[index])
		index += 3

		# Difference in Capacity Percentage
		grosses[DIFF_CAP_KEY] = process_span_line(lines[index])
		index += 1

		grosses[RECENTNESS_KEY] = recent_val
		recent_val += 1

		show_gross_page[week_end_date] = grosses


def process_show_grosses(base_link):
	# Shows go from a link like: https://www.playbill.com/production/gross?production=00000150-aea6-d936-a7fd-eef6ecdd0001
	# to a link like: https://www.playbill.com/production/gross/p1?production=00000150-aea6-d936-a7fd-eef6ecdd0001

	# At a show's max length, increating the page (pX) will just keep it on the last one
	show_gross_pages = dict()

	page = 1

	page_first_half = base_link.split('?')[0] + '/p'
	page_second_half = '?' + base_link.split('?')[1]

	recent_val = 1

	while True:
		show_gross_page, recent_val = process_show_gross_page(page_first_half + str(page) + page_second_half, recent_val)
		for date in show_gross_page:
			if date in show_gross_pages:
				return show_gross_pages
		show_gross_pages.update(show_gross_page)
		page += 1

def print_dict(jsondict):
	print(json.dumps(jsondict, sort_keys = True, indent = 4))


def extract_long_running_show_data():
	with open('Longest_Running_Broadway_Shows.tsv') as shows_list:
		for show_line in shows_list:
			show_list = show_line.split('\t')
			show_name = show_list[0]
			show_link = show_list[1]
			if len(show_link) <= 1:
				continue
			show_grosses = process_show_grosses(show_link)
			for grosses_week in sorted(show_grosses.keys()):
				year = grosses_week.split('-')[0].strip()
				week_num = show_grosses[grosses_week][WEEK_NUM_KEY]
				gross = show_grosses[grosses_week][GROSS_KEY]
				num_shows = int(show_grosses[grosses_week][PREVIEWS_KEY]) + int(show_grosses[grosses_week][PERFORMANCES_KEY]
				print(grosses_week + "\t" + show_name + "\t" + week_num + "\t" + year + "\t" + gross.strip('$').replace(',', '') + "\t" + str(num_shows))

if __name__ == '__main__':
	args = get_args()

	# sweeney_todd = 'https://www.playbill.com/production/gross?production=651e8a52-1de9-42b8-b3f9-88a56c5c0baa'
	# wicked = 'https://www.playbill.com/production/gross?production=00000150-aea6-d936-a7fd-eef6ecdd0001'
	# hadestown = 'https://www.playbill.com/production/gross?production=00000167-5ad2-d052-a567-dfdb48060000'
	# phantom = 'https://www.playbill.com/production/gross?production=00000150-aea4-d936-a7fd-eef4dee60001'

	extract_long_running_show_data()
	# hadestown_grosses = process_show_grosses(hadestown)
	# print(hadestown_grosses)
	# plot_grosses(hadestown_grosses)
