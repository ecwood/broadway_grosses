import json
import random

BOOTSTRAPPING_ROUNDS = 1000000

MAX_EARNINGS = 4500000.00

WEEKLY_OPERATING_COST = 650000.00

def run_bootstrapping(hadestown_grosses, multiplier_distribution):
	weekly_distribution = list()
	for x in range(BOOTSTRAPPING_ROUNDS):
		random_gross = hadestown_grosses[random.randint(0, len(hadestown_grosses) - 1)]
		random_multiplier = multiplier_distribution[random.randint(0, len(multiplier_distribution) - 1)]
		weekly_distribution.append(random_gross * random_multiplier)

	return weekly_distribution

def calculate_expectation(vals):
	list_sum = 0

	for val in vals:
		list_sum += val

	return list_sum / len(vals)

def calculate_variance(vals):
	variance_data = list()
	average = calculate_expectation(vals)

	for datapoint in vals:
		variance_data.append(pow(average - datapoint, 2))

	return calculate_expectation(variance_data)

def print_weekly_distribution_stats(weekly_distributions):
	for week in sorted(weekly_distributions.keys()):
		distribution_list = weekly_distributions[week]
		expectation = calculate_expectation(distribution_list)
		variance = calculate_variance(distribution_list)
		print("Week " + str(week))
		print("\tWeekly Distribution Expectation: " + str(expectation))
		print("\tWeekly Distribution Variance: " + str(variance))

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
		region_index = int(weighted_data_point / region_bound)
		regions[region_index] += 1

	for region_index in range(len(regions)):
		lower_range = format_monetary_value(str(region_bound * region_index))
		upper_range = format_monetary_value(str(region_bound * (region_index + 1)))
		earning_range = lower_range + '-' + upper_range
		earning_range_to_weighting[earning_range] = regions[region_index]

	return earning_range_to_weighting


def earning_range_dictionary_to_tsv(earning_range_to_weightings):
	weightings = list()
	for earning_range in earning_range_to_weightings:
		line_str = earning_range + "\t"
		line_str += str(earning_range_to_weightings[earning_range]) + "\t"
		line_str.strip()

		print(line_str)

def import_data():
	hadestown_grosses = list()
	with open('hadestown_weightings.json') as hadestown_weightings_file:
		hadestown_grosses = json.load(hadestown_weightings_file)

	multiplier_distributions = list()
	with open('weekly_weightings.json') as weekly_weightings_file:
		multiplier_distributions = json.load(weekly_weightings_file)

	return hadestown_grosses, multiplier_distributions

def get_probability_of_exceeding_operating_cost(gross_distribution):
	exceeding_operating_cost_trials = 0
	total_trials = 1
	for gross_trial in gross_distribution:
		total_trials += 1
		if gross_trial > WEEKLY_OPERATING_COST:
			exceeding_operating_cost_trials += 1

	return exceeding_operating_cost_trials / total_trials


if __name__ == '__main__':
	hadestown_grosses, multiplier_distributions = import_data()

	weekly_distributions = dict()

	for week in multiplier_distributions:
		weekly_distributions[week] = run_bootstrapping(hadestown_grosses, multiplier_distributions[week])
		probability_of_exceeding_operating_cost = get_probability_of_exceeding_operating_cost(weekly_distributions[week])
		print("Week " + week + " Probability of Exceeding Operating Cost: " + str(probability_of_exceeding_operating_cost))

	# print_weekly_distribution_stats(weekly_distributions)
