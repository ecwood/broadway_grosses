import json
import random
from itertools import combinations
import math

# Lowered for testing purposes
BOOTSTRAPPING_ROUNDS = 100000

MAX_EARNINGS = 4500000.00

WEEKLY_OPERATING_COST_ESTIMATES = [650000, 850000]

FAILURE_WEEK_ESTIMATES = [1, 2, 4] # I tried 8 but it spent hours not finishing

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

def import_data(weighting_type):
	hadestown_grosses = list()
	with open('hadestown_weightings-' + weighting_type + '.json') as hadestown_weightings_file:
		hadestown_grosses = json.load(hadestown_weightings_file)

	multiplier_distributions = list()
	with open('weekly_weightings.json') as weekly_weightings_file:
		multiplier_distributions = json.load(weekly_weightings_file)

	return hadestown_grosses, multiplier_distributions

def get_probability_of_exceeding_operating_cost(gross_distribution, weekly_operating_cost):
	exceeding_operating_cost_trials = 0
	total_trials = 1
	for gross_trial in gross_distribution:
		total_trials += 1
		if gross_trial > weekly_operating_cost:
			exceeding_operating_cost_trials += 1

	return exceeding_operating_cost_trials / total_trials

def get_list_product(vals):
	list_prod = 1
	for val in vals:
		list_prod *= val
	return list_prod

def get_lasting_probability(probabilities_of_exceeding_operating_cost, failing_weeks_before_close):
	probabilities_of_exceeding_operating_cost_keys = sorted(probabilities_of_exceeding_operating_cost.keys())
	lasting_probs = dict()
	for full_index in range(len(probabilities_of_exceeding_operating_cost_keys)):
		full_index_week = probabilities_of_exceeding_operating_cost_keys[full_index]
		weeks_considered = list()
		for week_index in range(0, full_index):
			weeks_considered.append(probabilities_of_exceeding_operating_cost[probabilities_of_exceeding_operating_cost_keys[week_index]])

		end_prob = probabilities_of_exceeding_operating_cost[full_index_week]
		total_product = get_list_product(weeks_considered) * end_prob
		prob = 0
		combos = list()

		if failing_weeks_before_close > (full_index + 1):
			lasting_probs[full_index_week] = 0
			continue

		if failing_weeks_before_close > 1:
			for base_combo in list(combinations(weeks_considered, failing_weeks_before_close - 1)):
				combos.append(list(base_combo) + [end_prob])
		else:
			combos.append([end_prob])

		for combo in combos:
			curr_prob = 1
			for item in combo:
				curr_prob *= (1 - item) / item
			prob += (curr_prob * total_product)
		lasting_probs[full_index_week] = prob

	return lasting_probs

def print_lasting_probs(lasting_probs):
	data = list()
	header = ["Week"]
	ex_weighting_type = str()
	ex_weekly_operating_cost = int()
	ex_failing_weeks_before_close = int()
	sum_prior_probs = dict()
	expectations = dict()
	for weighting_type in lasting_probs:
		for weekly_operating_cost in lasting_probs[weighting_type]:
			for failing_weeks_before_close in lasting_probs[weighting_type][weekly_operating_cost]:
				header.append(weighting_type + ", " + str(weekly_operating_cost) + ", " + str(failing_weeks_before_close) + "Exactly")
				header.append(weighting_type + ", " + str(weekly_operating_cost) + ", " + str(failing_weeks_before_close) + "More")
				ex_weighting_type = weighting_type
				ex_weekly_operating_cost = weekly_operating_cost
				ex_failing_weeks_before_close = failing_weeks_before_close
				if weighting_type not in sum_prior_probs:
					sum_prior_probs[weighting_type] = dict()
				if weekly_operating_cost not in sum_prior_probs[weighting_type]:
					sum_prior_probs[weighting_type][weekly_operating_cost] = dict()
				sum_prior_probs[weighting_type][weekly_operating_cost][failing_weeks_before_close] = 0

				if weighting_type not in expectations:
					expectations[weighting_type] = dict()
				if weekly_operating_cost not in expectations[weighting_type]:
					expectations[weighting_type][weekly_operating_cost] = dict()
				expectations[weighting_type][weekly_operating_cost][failing_weeks_before_close] = 0
	data.append(header)

	lasting_probs_keys = sorted(lasting_probs[ex_weighting_type][ex_weekly_operating_cost][ex_failing_weeks_before_close].keys())
	
	for week_index in range(len(lasting_probs_keys)):
		week = lasting_probs_keys[week_index]
		week_list = [str(week)]

		for weighting_type in lasting_probs:
			for weekly_operating_cost in lasting_probs[weighting_type]:
				for failing_weeks_before_close in lasting_probs[weighting_type][weekly_operating_cost]:
					prob = lasting_probs[weighting_type][weekly_operating_cost][failing_weeks_before_close][week]
					week_list.append(str(prob))
					expectations[weighting_type][weekly_operating_cost][failing_weeks_before_close] += prob * week
					sum_prior_probs[weighting_type][weekly_operating_cost][failing_weeks_before_close] += prob
					week_list.append(str(1- sum_prior_probs[weighting_type][weekly_operating_cost][failing_weeks_before_close]))
		data.append(week_list)

	for datapoint in data:
		print('\t'.join(datapoint))

	print("=============")
	print("Expectations:")

	for weighting_type in expectations:
		print(weighting_type + ": " + str(expectations[weighting_type]))



if __name__ == '__main__':
	all_lasting_probs = dict()
	for weighting_type in ["uniform", "linear", "quadratic", "exponential"]:
		all_lasting_probs[weighting_type] = dict()
		hadestown_grosses, multiplier_distributions = import_data(weighting_type)

		weekly_distributions = dict()

		probabilities_of_exceeding_operating_cost = dict()

		for week in multiplier_distributions:
			weekly_distributions[week] = run_bootstrapping(hadestown_grosses, multiplier_distributions[week])
			
			for weekly_operating_cost in WEEKLY_OPERATING_COST_ESTIMATES:
				if weekly_operating_cost not in probabilities_of_exceeding_operating_cost:
					probabilities_of_exceeding_operating_cost[weekly_operating_cost] = dict()
				probabilities_of_exceeding_operating_cost[weekly_operating_cost][int(week)] = get_probability_of_exceeding_operating_cost(weekly_distributions[week], weekly_operating_cost)

		for weekly_operating_cost in probabilities_of_exceeding_operating_cost:
			all_lasting_probs[weighting_type][weekly_operating_cost] = dict()
			for failing_weeks_before_close in FAILURE_WEEK_ESTIMATES:
				lasting_probs = get_lasting_probability(probabilities_of_exceeding_operating_cost[weekly_operating_cost], failing_weeks_before_close)
				all_lasting_probs[weighting_type][weekly_operating_cost][failing_weeks_before_close] = lasting_probs

	print_lasting_probs(all_lasting_probs)


	# print_weekly_distribution_stats(weekly_distributions)
