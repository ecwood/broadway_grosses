import json

YEAR_LEN = 52

SKIP_WEEKS = ['2001-09-16', '2001-09-23', '2007-11-18', '2007-11-25', '2021-09-05']

LAST_WEEK_PRE_COVID = '2020-03-08'

def import_data():
	data = dict()

	with open('cs109_data.tsv') as in_data:
		for data_line in in_data:
			data_line_split = data_line.strip().split('\t')
			week_date = data_line_split[0]
			show = data_line_split[1]
			week = data_line_split[2]
			year = data_line_split[3]
			gross = float(data_line_split[4])

			if show not in data:
				data[show] = list()
			else:
				if len(data[show]) == 0 or len(data[show][-1]) == YEAR_LEN:
					data[show].append([])
				if week_date in SKIP_WEEKS or (len(data[show][-1]) > 0 and data[show][-1][-1][0] == LAST_WEEK_PRE_COVID):
					data[show].pop()
					continue

				data[show][-1].append((week_date, week, year, gross))

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


def list_average(vals):
	list_sum = 0

	for val in vals:
		list_sum += val

	return list_sum / len(vals)

def list_sum(vals):
	list_sum = 0

	for val in vals:
		list_sum += val

	return list_sum

def get_yearly_weighting(year_data):
	yearly_weighting = dict()

	all_grosses = list()

	for (_, _, _, gross) in year_data:
		all_grosses.append(gross)

	yearly_average = list_average(all_grosses)

	for (_, week, _, gross) in year_data:
		yearly_weighting[week] = gross / yearly_average

	return yearly_weighting


if __name__ == '__main__':
	data = import_data()

	all_weightings = dict()

	for show in data:
		for year_data in data[show]:
			yearly_weighting = get_yearly_weighting(year_data)

			for week in yearly_weighting:
				if week not in all_weightings:
					all_weightings[week] = list()
				all_weightings[week].append(yearly_weighting[week])

	for week in all_weightings:
		print(week, list_average(all_weightings[week]))