import json
import math

WEEK_DATE_KEY = 'week_date'
WEEK_KEY = 'week'
YEAR_KEY = 'year'
GROSS_KEY = 'gross'
WEIGHTING_KEY = 'weight'

SKIP_WEEKS = ['2019-03-24', '2021-09-05']

MAX_EARNINGS = 1700000.00

NUM_GROUPINGS = 30


def uniform_weightings(data):
	for data_point in data:
		data_point[WEIGHTING_KEY] = (data_point[WEEK_DATE_KEY] not in SKIP_WEEKS) * 1

	return data


def linear_week_weightings(data, num_weeks_to_group):
	week_index = 0
	for data_point in data:
		data_point[WEIGHTING_KEY] = (data_point[WEEK_DATE_KEY] not in SKIP_WEEKS) * (int(week_index / num_weeks_to_group) + 1)
		week_index += 1

	return data

def quadratic_week_weightings(data, num_weeks_to_group):
	week_index = 0
	for data_point in data:
		data_point[WEIGHTING_KEY] = (data_point[WEEK_DATE_KEY] not in SKIP_WEEKS) * pow((int(week_index / num_weeks_to_group) + 1), 2)
		week_index += 1

	return data

def exponential_week_weightings(data, num_weeks_to_group):
	week_index = 0
	for data_point in data:
		data_point[WEIGHTING_KEY] = (data_point[WEEK_DATE_KEY] not in SKIP_WEEKS) * math.ceil(pow(2, (int(week_index / num_weeks_to_group) + 1) / 2)) # divide by 2 to prevent overflow
		week_index += 1

	return data

def format_monetary_value(raw_string):
	split_string = raw_string.split('.')
	raw_decimal = split_string[1]
	if len(raw_decimal) >= 2:
		decimal = raw_decimal[0:2]
	else:
		decimal = raw_decimal + '0' * (2 - len(raw_decimal))

	major_monetary_val = ''
	index_from_decimal = 0
	raw_major_monetary_val = split_string[0]
	for index in range(len(raw_major_monetary_val) - 1, -1, -1):
		index_from_decimal += 1
		comma = ((index_from_decimal % 3) == 0) * ','
		major_monetary_val = comma + raw_major_monetary_val[index] + major_monetary_val

	return '$' + major_monetary_val.strip(',') + '.' + decimal



def divide_into_regions(weighted_data, num_regions):
	region_bound = MAX_EARNINGS / num_regions
	regions = [0] * num_regions

	earning_range_to_weighting = dict()

	for weighted_data_point in weighted_data:
		region_index = int(float(weighted_data_point[GROSS_KEY]) / region_bound)
		regions[region_index] += weighted_data_point[WEIGHTING_KEY]

	for region_index in range(len(regions)):
		lower_range = format_monetary_value(str(region_bound * region_index))
		upper_range = format_monetary_value(str(region_bound * (region_index + 1)))
		earning_range = lower_range + '-' + upper_range
		earning_range_to_weighting[earning_range] = regions[region_index]

	return earning_range_to_weighting

def calculate_expectation(vals):
	list_sum = 0

	for val in vals:
		list_sum += val

	return list_sum / len(vals)

def import_data():
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


	multiplier_distributions = dict()
	with open('weekly_weightings.json') as weekly_weightings_file:
		multiplier_distributions_loaded = json.load(weekly_weightings_file)

		for week in multiplier_distributions_loaded:
			multiplier_distributions[week] = calculate_expectation(multiplier_distributions_loaded[week])

	data = list()

	with open('cs109_hadestown_data.tsv') as hadestown_in_data:
		for data_line in hadestown_in_data:
			data_line_split = data_line.split('\t')
			week_date = data_line_split[0]
			formal_week = data_line_split[2]
			year = data_line_split[3]
			gross = data_line_split[4]

			week = week_definitions[week_date.replace(year, '')]

			week_modified_gross = str(float(gross) / multiplier_distributions[str(week)])

			data.append({WEEK_DATE_KEY: week_date,
						 WEEK_KEY: formal_week,
						 YEAR_KEY: year,
						 GROSS_KEY: week_modified_gross})


	return data


def update_dictionary(new_dictionary, key, existing_dictionary):
	for dict_key in new_dictionary:
		if dict_key not in existing_dictionary:
			existing_dictionary[dict_key] = dict()
		existing_dictionary[dict_key][key] = new_dictionary[dict_key]

	return existing_dictionary


def earning_range_dictionary_to_tsv(earning_range_to_weightings):
	weightings = list()
	for earning_range in earning_range_to_weightings:
		weightings = earning_range_to_weightings[earning_range].keys()

		header = "Earning Range\t"
		for weighting in weightings:
			header += weighting + "\t"
		header.strip()
		break

	print(header)

	for earning_range in earning_range_to_weightings:
		line_str = earning_range + "\t"
		for weighting in weightings:
			line_str += str(earning_range_to_weightings[earning_range][weighting]) + "\t"
		line_str.strip()

		print(line_str)

def save_weightings_list_json(hadestown_weighted_data, weightings_type):
	weightings_list = []
	for weighting in hadestown_weighted_data:
		weightings_list += [float(weighting[GROSS_KEY])] * weighting[WEIGHTING_KEY]

	with open('hadestown_weightings-' + weightings_type + '.json', 'w') as hadestown_weightings_file:
		hadestown_weightings_file.write(json.dumps(weightings_list, indent=4, sort_keys=True))

if __name__ == '__main__':
	hadestown_data = import_data()

	earning_range_to_weightings = dict()

	hadestown_weighted_data_uniform = uniform_weightings(hadestown_data)
	save_weightings_list_json(hadestown_weighted_data_uniform, "uniform")

	hadestown_weighted_data_linear = linear_week_weightings(hadestown_data, 4)
	save_weightings_list_json(hadestown_weighted_data_linear, "linear")

	hadestown_weighted_data_quadratic = quadratic_week_weightings(hadestown_data, 4)
	save_weightings_list_json(hadestown_weighted_data_quadratic, "quadratic")

	hadestown_weighted_data_exponential = exponential_week_weightings(hadestown_data, 4)
	save_weightings_list_json(hadestown_weighted_data_exponential, "exponential")
