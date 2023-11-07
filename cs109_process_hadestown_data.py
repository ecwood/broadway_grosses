WEEK_DATE_KEY = 'week_date'
WEEK_KEY = 'week'
YEAR_KEY = 'year'
GROSS_KEY = 'gross'
WEIGHTING_KEY = 'weight'

SKIP_WEEKS = ['2019-03-24', '2021-09-05']

MAX_EARNINGS = 1700000.00


def uniform_weightings(data):
	normalization_constant = 0
	for data_point in data:
		normalization_constant += (data_point[WEEK_DATE_KEY] not in SKIP_WEEKS) * 1

	for data_point in data:
		data_point[WEIGHTING_KEY] = (data_point[WEEK_DATE_KEY] not in SKIP_WEEKS) * 1 / normalization_constant

	return data


def nearest_grouped_week_weightings(data, num_weeks_to_group):
	normalization_constant = 0

	num_groups_total = int(len(data) / num_weeks_to_group)

	week_index = 0
	for data_point in data:
		normalization_constant += (data_point[WEEK_DATE_KEY] not in SKIP_WEEKS) * (num_groups_total - int(week_index / num_weeks_to_group))
		week_index += 1

	week_index = 0
	for data_point in data:
		data_point[WEIGHTING_KEY] = (data_point[WEEK_DATE_KEY] not in SKIP_WEEKS) * (num_groups_total - int(week_index / num_weeks_to_group)) / normalization_constant
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

	for weighted_data_point in weighted_data:
		region_index = int(float(weighted_data_point[GROSS_KEY]) / region_bound)
		regions[region_index] += weighted_data_point[WEIGHTING_KEY]

	for region_index in range(len(regions)):
		lower_range = format_monetary_value(str(region_bound * region_index))
		upper_range = format_monetary_value(str(region_bound * (region_index + 1)))
		earning_range = lower_range + '-' + upper_range
		print(earning_range + '\t' + str(regions[region_index]))


def import_data():
	data = list()

	with open('cs109_hadestown_data.tsv') as hadestown_in_data:
		for data_line in hadestown_in_data:
			data_line_split = data_line.split('\t')
			week_date = data_line_split[0]
			week = data_line_split[2]
			year = data_line_split[3]
			gross = data_line_split[4]

			data.append({WEEK_DATE_KEY: week_date,
						 WEEK_KEY: week,
						 YEAR_KEY: year,
						 GROSS_KEY: gross})

	return data


if __name__ == '__main__':
	hadestown_data = import_data()

	for x in range(1, 52):
		hadestown_weighted_data = nearest_grouped_week_weightings(hadestown_data, x)
		divide_into_regions(hadestown_weighted_data, 10)
		print("\n")