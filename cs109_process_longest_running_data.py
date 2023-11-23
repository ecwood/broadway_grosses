import json

YEAR_LEN = 52

SKIP_WEEKS = ['2001-09-16', '2001-09-23', '2007-11-18', '2007-11-25', '2021-09-05']

LAST_WEEK_PRE_COVID = '2020-03-08'

SHOWS_PER_WEEK = 8

def import_data():
	data = dict()

	week_definitions = dict()

	with open('cs109_week_definitions.tsv') as week_defs_data:
		index = 0
		for data_line in week_defs_data:
			index += 1
			if index == 1:
				continue
			data_line_split = data_line.strip().split('\t')
			week_num = int(data_line_split[0])

			for week_date in data_line_split[1:]:
				week_definitions["-" + week_date] = week_num


	with open('cs109_data.tsv') as in_data:
		for data_line in in_data:
			data_line_split = data_line.strip().split('\t')
			week_date = data_line_split[0]
			show = data_line_split[1]
			year = data_line_split[3]

			week = week_definitions[week_date.replace(year, '')]
			
			gross = float(data_line_split[4])
			num_shows = int(data_line_split[5])

			if show not in data:
				data[show] = list()
			else:
				if len(data[show]) == 0 or len(data[show][-1]) == YEAR_LEN:
					data[show].append([])
				if week_date in SKIP_WEEKS or (len(data[show][-1]) > 0 and data[show][-1][-1][0] == LAST_WEEK_PRE_COVID):
					data[show].pop()
					continue

				effective_gross = gross

				if num_shows < SHOWS_PER_WEEK:
					effective_gross = SHOWS_PER_WEEK * (gross / num_shows)
				data[show][-1].append((week_date, week, year, effective_gross))

		zero_size = list()
		for show in data:
			if len(data[show][-1]) < YEAR_LEN:
				data[show].pop()
			if len(data[show]) == 0:
				zero_size.append(show)

		for zero_year_show in zero_size:
			data.pop(zero_year_show)

		for show in data:
			print(show, len(data[show]))

	return data


def calculate_expectation(vals):
	list_sum = 0

	for val in vals:
		list_sum += val

	return list_sum / len(vals)

def list_sum(vals):
	list_sum = 0

	for val in vals:
		list_sum += val

	return list_sum

def calculate_maximum(vals):
	maximum = 0

	for val in vals:
		if val > maximum:
			maximum = val

	return maximum

def calculate_minimum(vals):
	minimum = 100

	for val in vals:
		if val < minimum:
			minimum = val

	return minimum

def calculate_variance(vals):
	variance_data = list()
	average = calculate_expectation(vals)

	for datapoint in vals:
		variance_data.append(pow(average - datapoint, 2))

	return calculate_expectation(variance_data)


def get_yearly_weighting(year_data):
	yearly_weighting = dict()

	all_grosses = list()

	for (_, _, _, gross) in year_data:
		all_grosses.append(gross)

	yearly_average = calculate_expectation(all_grosses)

	for (week_date, week, year, gross) in year_data:
		yearly_weighting[week] = (gross / yearly_average, year, week_date)

	return yearly_weighting

def get_show_weightings(all_shows_data):
	all_weightings = dict()

	for show in all_shows_data:
		for year_data in all_shows_data[show]:
			yearly_weighting = get_yearly_weighting(year_data)

			for week in yearly_weighting:
				(weekly_weighting, year, week_date) = yearly_weighting[week]
				if week not in all_weightings:
					all_weightings[week] = list()
				all_weightings[week].append((weekly_weighting, show, year, week_date))
	
	return all_weightings

def break_down_show_weightings(show_weightings):
	weekly_weighting_lists = dict()
	weightings_map = dict()

	for week in show_weightings:
		for (weekly_weighting, show, year, week_date) in show_weightings[week]:
			if week not in weekly_weighting_lists:
				weekly_weighting_lists[week] = list()
			weekly_weighting_lists[week].append(weekly_weighting)

			weightings_map[weekly_weighting] = (week_date, show, year)

	return weekly_weighting_lists, weightings_map

def print_weekly_weighting_stats(weekly_weighting_lists, weightings_map):
	for week in sorted(weekly_weighting_lists.keys()):
		weighting_list = weekly_weighting_lists[week]
		expectation = calculate_expectation(weighting_list)
		variance = calculate_variance(weighting_list)
		print("Week " + str(week))
		print("\tWeekly Multiple Expectation: " + str(expectation))
		print("\tWeekly Multiple Variance: " + str(variance))
		min_weighting = calculate_minimum(weighting_list)
		(min_week_date, min_show, min_year) = weightings_map[min_weighting]
		max_weighting = calculate_maximum(weighting_list)
		(max_week_date, max_show, max_year) = weightings_map[max_weighting]
		print("\tWeekly Multiple Minimum: " + str(min_weighting) + " on " + min_week_date + " by " + min_show)
		print("\tWeekly Multiple Maximum: " + str(max_weighting) + " on " + max_week_date + " by " + max_show)

if __name__ == '__main__':
	data = import_data()

	show_weightings = get_show_weightings(data)

	weekly_weighting_lists, weightings_map = break_down_show_weightings(show_weightings)

	print_weekly_weighting_stats(weekly_weighting_lists, weightings_map)

