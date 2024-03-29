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

THEATERS = {"Al Hirschfeld Theatre": 'https://www.playbill.com/venue/al-hirschfeld-theatre-vault-0000000268',
			"Ambassador Theatre": 'https://www.playbill.com/venue/ambassador-theatre-vault-0000000033',
			"American Airlines Theatre": 'https://www.playbill.com/venue/american-airlines-theatre-vault-0000000327',
			"August Wilson Theatre": 'https://www.playbill.com/venue/august-wilson-theatre-vault-0000000162',
			"Belasco Theatre": 'https://www.playbill.com/venue/belasco-theatre-vault-0000000334',
			"Bernard B. Jacobs Theatre": 'https://www.playbill.com/venue/bernard-b-jacobs-theatre-vault-0000000323',
			"Booth Theatre": 'https://www.playbill.com/venue/booth-theatre-vault-0000000054',
			"Broadhurst Theatre": 'https://www.playbill.com/venue/broadhurst-theatre-vault-0000000061',
			"Broadway Theatre": 'https://www.playbill.com/venue/broadway-theatre-vault-0000000390',
			"Circle in the Square Theatre": 'https://www.playbill.com/venue/circle-in-the-square-theatre-vault-0000000092',
			"Ethel Barrymore Theatre": 'https://www.playbill.com/venue/ethel-barrymore-theatre-vault-0000000135',
			"Eugene O'Neill Theatre": 'https://www.playbill.com/venue/eugene-oneill-theatre-vault-0000000141',
			"Gerald Shoenfeld Theatre": 'https://www.playbill.com/venue/gerald-schoenfeld-theatre-vault-0000000293',
			"Gershwin Theatre": 'https://www.playbill.com/venue/george-gershwin-theatre-vault-0000000339',
			"Hayes Theaer": 'https://www.playbill.com/venue/helen-hayes-theater-vault-0000000235',
			"Hudson Theatre": 'https://www.playbill.com/venue/hudson-theatre-vault-0000000198',
			"Imperial Theatre": 'https://www.playbill.com/venue/imperial-theatre-vault-0000000201',
			"James Earl Jones Theatre": 'https://www.playbill.com/venue/james-earl-jones-theatre-2022-new-york-ny',
			"John Golden Theatre": 'https://www.playbill.com/venue/john-golden-theatre-vault-0000000270',
			"Lena Horne Theatre": 'https://www.playbill.com/venue/lena-horne-theatre-2022-new-york-ny',
			"Longacre Theatre": 'https://www.playbill.com/venue/longacre-theatre-vault-0000000242',
			"Lunt-Fontanne Theatre": 'https://www.playbill.com/venue/lunt-fontanne-theatre-vault-0000000158',
			"Lyceum Theatre": 'https://www.playbill.com/venue/lyceum-theatre-vault-0000000243',
			"Lyric Theatre": 'https://www.playbill.com/venue/lyric-theatre-vault-0000000590',
			"Majestic Theatre": 'https://www.playbill.com/venue/majestic-theatre-vault-0000000261',
			"Marquis Theatre": 'https://www.playbill.com/venue/marquis-theatre-vault-0000000267',
			"Minskoff Theatre": 'https://www.playbill.com/venue/minskoff-theatre-vault-0000000068',
			"Music Box Theatre": 'https://www.playbill.com/venue/music-box-theatre-vault-0000000070',
			"Nederlander Theater": 'https://www.playbill.com/venue/nederlander-theatre-vault-0000000071',
			"Neil Simon Theatre": 'https://www.playbill.com/venue/neil-simon-theatre-vault-0000000031',
			"New Amsterdam Theatre": 'https://www.playbill.com/venue/new-amsterdam-theatre-vault-0000000276',
			"Palace Theatre": 'https://www.playbill.com/venue/palace-theatre-vault-0000000288',
			"Richard Rodgers Theatre": 'https://www.playbill.com/venue/richard-rodgers-theatre-vault-0000000085',
			"Samuel J. Friedman Theatre": 'https://www.playbill.com/venue/samuel-j-friedman-theatre-vault-0000000052',
			"Shubert Theatre": 'https://www.playbill.com/venue/shubert-theatre-vault-0000000329',
			"Stephen Sondheim Theatre": 'https://www.playbill.com/venue/stephen-sondheim-theatre-vault-0000000184',
			"St. James Theatre": 'https://www.playbill.com/venue/st-james-theatre-vault-0000000133',
			"Studio 54": 'https://www.playbill.com/venue/studio-54-vault-0000000147',
			"Vivian Beaumont Theater": 'https://www.playbill.com/venue/vivian-beaumont-theater-vault-0000000344',
			"Walter Kerr Theatre": 'https://www.playbill.com/venue/walter-kerr-theatre-vault-0000000320',
			"Winter Garden Theatre": 'https://www.playbill.com/venue/winter-garden-theatre-vault-0000000353'}

# Theater Previous Shows Keys
PREVIOUS_SHOWS_TAG = '<h3 itemprop="headline" class="bsp-component-title">Previous Shows in This Building</h3>'
PREVIOUS_SHOW_TAG = '<div class="bsp-carousel-slide">'
SHOW_TITLE = 'title='
DATE_TAG = 'data-cms-ai="0">'

# Facts Keys/Tags
BOOK_TAG = '<span>book:</span>'
BOOK_KEY = 'book'
MUSIC_TAG = '<span>music:</span>'
MUSIC_KEY = 'music'
LYRICS_TAG = '<span>lyrics:</span>'
LYRICS_KEY = 'lyrics'
RUNTIME_TAG = '<li><span>Running Time:</span>'
RUNTIME_END_TAG = '</li>'
RUNTIME_KEY = 'runtime'
ADDRESS_KEY = 'address'
DESCRIPTION_KEY = 'description'
KEYWORDS_KEY = 'keywords'
CAST_MEMBERS_KEY = 'cast_members'
FIRST_PREVIEW_KEY = 'first_preview'
OPENING_DATE_TAG = '<div class="bsp-list-promo-title">Opening Date</div>'
OPENING_DATE_KEY = 'opening_date'
CLOSING_DATE_TAG = '<div class="bsp-list-promo-title">Closing Date</div>'
CLOSING_DATE_KEY = 'closing_date'
PREVIEWS_TAG = '<div class="bsp-list-promo-title">Previews</div>'
PREVIEWS_KEY = 'previews'
PERFORMANCES_TAG = '<div class="bsp-list-promo-title">Performances</div>'
AWARDS_KEY = 'awards'
GROSS_LINK_KEY = 'gross_link'
TOTAL_CURRENT_GROSS_TAG = '<b>Total Current Gross:</b>'
TOTAL_CURRENT_GROSS_KEY = 'total_current_gross'
HIGHEST_WEEKLY_GROSS_TAG = '<b>Highest Weekly Gross:</b>'
HIGHEST_WEEKLY_GROSS_KEY = 'highest_weekly_gross'
AVERAGE_TICKET_PRICE_TAG = '<b>Average Ticket Price:</b>'
AVERAGE_TICKET_PRICE_KEY = 'average_ticket_price'
AVERAGE_PERCENT_CAPACITY_TAG = '<b>Average % Capacity:</b>'
AVERAGE_PERCENT_CAPACITY_KEY = 'average_percent_capacity'

# Cast Keys and Tags
CAST_START_TAG = '<div class="bsp-component cast-list" id="cc">'
CAST_MEMBER_START_TAG = '<li>'
CAST_MEMBER_REPLACEMENT_START_TAG = '<span class="cast-list-subheading hide">Replacement</span>'
CAST_MEMBER_DATE_TAG = '<div class="bsp-component-group">'
CAST_MEMBER_ADDITIONAL_DATES_TAG = '<ul class="bsp-unstyled-list">'
CAST_MEMBER_END_TAG = '</ul>'
CAST_MEMBER_DEPARTED_TAG = 'Departed on'
CAST_MEMBER_ARRIVED_TAG = 'Arrived on'
CAST_MEMBER_NOT_DATE_TAG = '<ul class="bsp-unstyled-list cast-list-sublist hide">'

REPLACEMENT_KEY = 'replacement'
DATES_KEY = 'dates'
NAME_KEY = 'name'
ROLE_KEY = 'role'
CAST_LINK_KEY = 'link'
TAG_KEY = 'tag'

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
	lines = get_webpage(link)

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

def process_previous_shows_at_theater(link):
	previous_show_pages = dict()
	
	lines = get_webpage(link)

	index = 0

	while index < len(lines) and lines[index] != PREVIOUS_SHOWS_TAG:
		index += 1

	while index < len(lines):
		grosses = dict()
		week_end_date = ""

		while lines[index] != PREVIOUS_SHOW_TAG:
			index += 1

			if index >= len(lines):
				return previous_show_pages
		
		index += 8
		
		url = lines[index].replace(LINK_MARKER, '').replace('"', '')
		index += 1
		title = lines[index].replace(SHOW_TITLE, '').replace('"', '').replace('&#039;', "'").replace('&amp;', '&')
		index += 18
		date = lines[index].replace(DATE_TAG, '')

		previous_show_pages[(title, date)] = url

		index += 1
	return previous_show_pages

def get_set_of_people(line):
	set_of_people = dict()
	people = line.split(', ')
	for person in people:
		name = process_span_line(person)
		name_url = person.replace(LINK_MARKER, '').split(' ')[0].strip('"')
		set_of_people[name] = name_url
	return set_of_people

def format_date(month, day, year):
	month = process_span_line(month)
	day = process_span_line(day)
	year = process_span_line(year)

	if len(day) > 0 and len(year) > 0:
		return month + " " + day + ", " + year
	return month

def process_cast_member(cast_lines, previous_role, auto_replacement):
	cast_member = dict()

	cast_member[REPLACEMENT_KEY] = False
	
	if auto_replacement:
		cast_member[REPLACEMENT_KEY] = True
	
	dates = []
	for index in range(0, len(cast_lines)):
		if cast_lines[index] == CAST_MEMBER_REPLACEMENT_START_TAG:
			cast_member[REPLACEMENT_KEY] = True
			cast_member[ROLE_KEY] = previous_role
		if cast_lines[index].startswith(LINK_MARKER) and cast_lines[index].endswith(LINK_ENDER):
			cast_member[NAME_KEY] = process_span_line(cast_lines[index])
			cast_member[CAST_LINK_KEY] = cast_lines[index].replace(LINK_MARKER, '').split(' ')[0].strip('\\"')
			index += 3

			roles = []
			if cast_lines[index] == '</li>':
				cast_member[REPLACEMENT_KEY] = True
			
			while cast_lines[index] != '</li>':
				roles.append(cast_lines[index].replace('<br>', ''))
				index += 1	
			if len(roles) > 0:
				cast_member[ROLE_KEY] = roles
				previous_role = cast_member[ROLE_KEY]

		if cast_lines[index] == CAST_MEMBER_DATE_TAG:
			index += 1
			if CAST_MEMBER_ARRIVED_TAG in cast_lines[index]:
				index += 1
				dates.append(cast_lines[index] + " - Present")
			elif CAST_MEMBER_DEPARTED_TAG in cast_lines[index]:
				index += 1
				dates.append("Opening - " + cast_lines[index])
			elif cast_lines[index] != CAST_MEMBER_NOT_DATE_TAG:
				dates.append(cast_lines[index])
		if cast_lines[index] == CAST_MEMBER_ADDITIONAL_DATES_TAG:
			index += 1
			while index < len(cast_lines) and cast_lines[index] != "</div":
				if CAST_MEMBER_ARRIVED_TAG in cast_lines[index]:
					index += 1
					dates.append(cast_lines[index] + " - Present")
				elif CAST_MEMBER_DEPARTED_TAG in cast_lines[index]:
					index += 1
					dates.append("Opening - " + cast_lines[index])
				elif cast_lines[index] != CAST_MEMBER_NOT_DATE_TAG:
					dates.append(cast_lines[index])
				index += 1

	dates = [date.replace('</li>', '').replace('<li>', '') for date in dates]

	if len(dates) == 0:
		dates.append("Opening - Present")

	cast_member[DATES_KEY] = dates

	return cast_member, previous_role

	

def get_cast_information(link):
	cast_information = dict()
	
	lines = get_hard_to_get_webpage(link)

	index = 0

	while index < len(lines) and lines[index] != CAST_START_TAG:
		index += 1

	index += 2

	role_type = process_span_line(lines[index])

	previous_role = None

	cast_members_unique = set()
	cast_members = list()

	auto_replacement = False

	tag = ""

	while index < len(lines):
		cast_lines = []
		while index < len(lines) and lines[index] != CAST_MEMBER_START_TAG and lines[index] != CAST_MEMBER_REPLACEMENT_START_TAG:
			if "Other Music Replacements" in lines[index]:
				auto_replacement = True
				tag = "Other Music Replacements"
			elif "Other Cast Replacements" in lines[index]:
				auto_replacement = True
				tag = "Other Cast Replacements"
			elif "Other Production Team Replacements" in lines[index]:
				auto_replacement = True
				tag = "Other Production Team Replacements"
			elif "Production Team" in lines[index]:
				auto_replacement = False
				tag = "Production Team"
			elif "Standbys, Understudies, and Swings" in lines[index]:
				auto_replacement = False
				tag = "Standbys, Understudies, and Swings"
			elif "Music" in lines[index]:
				auto_replacement = False
				tag = "Music"
			elif "Cast" in lines[index]:
				auto_replacement = False
				tag = "Cast"
			index += 1
		
		while index < len(lines) and lines[index] != CAST_MEMBER_END_TAG:
			cast_lines.append(lines[index])
			index += 1
		cast_member, previous_role = process_cast_member(cast_lines, previous_role, auto_replacement)

		if REPLACEMENT_KEY in cast_member and DATES_KEY in cast_member and NAME_KEY in cast_member and ROLE_KEY in cast_member and CAST_LINK_KEY in cast_member:
			cast_members_unique.add((cast_member[REPLACEMENT_KEY], ";".join(cast_member[DATES_KEY]), cast_member[NAME_KEY], ";".join(cast_member[ROLE_KEY]), cast_member[CAST_LINK_KEY], tag))

		index += 1

	for cast_member in cast_members_unique:
		cast_members.append({REPLACEMENT_KEY: cast_member[0],
							 DATES_KEY: cast_member[1].split(";"),
							 NAME_KEY: cast_member[2],
							 ROLE_KEY: cast_member[3].split(";"),
							 CAST_LINK_KEY: cast_member[4],
							 TAG_KEY: cast_member[5]})
	return cast_members


def get_show_facts(link):
	show_facts = dict()
	
	lines = get_webpage(link)

	index = 0

	while index < len(lines):
		line = lines[index]

		if line == BOOK_TAG:
			show_facts[BOOK_KEY] = get_set_of_people(lines[index + 1])
		if line == MUSIC_TAG:
			show_facts[MUSIC_KEY] = get_set_of_people(lines[index + 1])
		if line == LYRICS_TAG:
			show_facts[LYRICS_KEY] = get_set_of_people(lines[index + 1])
		if line.startswith(RUNTIME_TAG):
			show_facts[RUNTIME_KEY] = lines[index].replace(RUNTIME_TAG, '').replace(RUNTIME_END_TAG, '').strip()
		if line == OPENING_DATE_TAG:
			show_facts[OPENING_DATE_KEY] = format_date(lines[index + 5], lines[index + 6], lines[index + 7])
		if line == CLOSING_DATE_TAG:
			show_facts[CLOSING_DATE_KEY] = format_date(lines[index + 5], lines[index + 6], lines[index + 7])
		if line == PREVIEWS_TAG:
			show_facts[PREVIEWS_KEY] = process_span_line(lines[index + 5])
		if line == PERFORMANCES_TAG:
			show_facts[PERFORMANCES_KEY] = process_span_line(lines[index + 6])
		if line == TOTAL_CURRENT_GROSS_TAG:
			show_facts[TOTAL_CURRENT_GROSS_KEY] = lines[index + 1]
		if line == HIGHEST_WEEKLY_GROSS_TAG:
			show_facts[HIGHEST_WEEKLY_GROSS_KEY] = lines[index + 1]
		if line == AVERAGE_TICKET_PRICE_TAG:
			show_facts[AVERAGE_TICKET_PRICE_KEY] = lines[index + 1]
		if line == AVERAGE_PERCENT_CAPACITY_TAG:
			show_facts[AVERAGE_PERCENT_CAPACITY_KEY] = lines[index + 1]
		if "personlistpage" in line and show_facts.get(CAST_MEMBERS_KEY, None) is None:
			cast_url = line.replace(LINK_MARKER, '').replace('"', '').replace('&amp;', '&')
			print(cast_url)
			show_facts[CAST_MEMBERS_KEY] = get_cast_information(cast_url)
		index += 1

	return show_facts

def print_previous_shows(page_dict):
	for (title, date) in page_dict:
		print("Title: " + title + ", Date: " + date + ", URL: " + page_dict[(title, date)])

def print_dict(jsondict):
	print(json.dumps(jsondict, sort_keys = True, indent = 4))

def plot_grosses(weekly_grosses):
	size = len(weekly_grosses)

	# https://note.nkmk.me/en/python-list-initialize/
	# x is the week
	# y is the gross
	weekly_grosses_x = [0] * size
	weekly_grosses_y = [0] * size	

	for week in weekly_grosses:
		index = size - (weekly_grosses[week][RECENTNESS_KEY])
		weekly_grosses_x[index] = week
		weekly_grosses_y[index] = float(weekly_grosses[week][GROSS_KEY][1:].replace(',', ''))

	# https://www.geeksforgeeks.org/python-introduction-matplotlib/
	plt.plot(weekly_grosses_x, weekly_grosses_y)

	# https://stackoverflow.com/questions/1221108/barchart-with-vertical-labels-in-python-matplotlib
	plt.xticks(rotation='vertical')

	# https://stackoverflow.com/questions/20337664/cleanest-way-to-hide-every-nth-tick-label-in-matplotlib-colorbar
	# with
	# https://www.delftstack.com/howto/matplotlib/how-to-hide-axis-text-ticks-and-or-tick-labels-in-matplotlib/
	ax = plt.gca()
	for label in ax.xaxis.get_ticklabels()[::2]:
		label.set_visible(False)

	plt.show()

if __name__ == '__main__':
	args = get_args()

	# sweeney_todd = 'https://www.playbill.com/production/gross?production=651e8a52-1de9-42b8-b3f9-88a56c5c0baa'
	# wicked = 'https://www.playbill.com/production/gross?production=00000150-aea6-d936-a7fd-eef6ecdd0001'
	# hadestown = 'https://www.playbill.com/production/gross?production=00000167-5ad2-d052-a567-dfdb48060000'
	# phantom = 'https://www.playbill.com/production/gross?production=00000150-aea4-d936-a7fd-eef4dee60001'

	# hadestown_grosses = process_show_grosses(phantom)
	# plot_grosses(hadestown_grosses)

	previous_show_pages = dict()
	for theater in THEATERS:
		previous_show_pages.update(process_previous_shows_at_theater(THEATERS["Walter Kerr Theatre"]))
		for previous_show_page in previous_show_pages:
			print(previous_show_page, get_show_facts(previous_show_pages[previous_show_page]))
		break

	# get_cast_information('https://www.playbill.com/personlistpage/person-list?production=00000167-5ad2-d052-a567-dfdb48060000&type=op#cc')