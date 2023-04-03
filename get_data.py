import os
import json
import argparse
import random

TEMP_DIR = 'temp/'

SHOW_START_TAG = '<td data-label="Show" class="col-0">'
END_TAG = '</tr>'
LINK_MARKER = '<a href='

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

def get_args():
	arg_parser = argparse.ArgumentParser(description='get_data.py: get Playbill Broadway Grosses data')
	arg_parser.add_argument('inputLink', type=str)
	return arg_parser.parse_args()

def get_webpage(link):
	os.system('mkdir ' + TEMP_DIR)
	rand_num = random.randint(0, 1000);
	tempfile = TEMP_DIR + 'tempfile' + str(rand_num) + '.txt'
	os.system('curl -s ' + link + ' --output ' + tempfile)

	lines = []
	for line in open(tempfile, 'r'):
		lines.append(line.strip())

	os.system('rm ' + tempfile)
	os.system('rm -r ' + TEMP_DIR)
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

def process_show_gross_page(link):
	lines = get_webpage(link)

	index = 0
	show_gross_page = dict()
	while index < len(lines):
		grosses = dict()
		week_end_date = ""
		while lines[index] != SHOW_GROSS_TAG:
			index += 1
			if index >= len(lines):
				return show_gross_page
		index += 1

		# End Date
		week_end_date = process_span_line(lines[index])
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

		show_gross_page[week_end_date] = grosses


def process_show_grosses(base_link):
	# Shows go from a link like: https://www.playbill.com/production/gross?production=00000150-aea6-d936-a7fd-eef6ecdd0001
	# to a link like: https://www.playbill.com/production/gross/p1?production=00000150-aea6-d936-a7fd-eef6ecdd0001

	# At a show's max length, increating the page (pX) will just keep it on the last one
	show_gross_pages = dict()

	page = 1

	page_first_half = base_link.split('?')[0] + '/p'
	page_second_half = '?' + base_link.split('?')[1]

	while True:
		show_gross_page = process_show_gross_page(page_first_half + str(page) + page_second_half)
		for date in show_gross_page:
			if date in show_gross_pages:
				return show_gross_pages
		show_gross_pages.update(show_gross_page)
		page += 1

def print_dict(jsondict):
	print(json.dumps(jsondict, sort_keys = True, indent = 4))

if __name__ == '__main__':
	args = get_args()

	print_dict(process_show_grosses(args.inputLink))
