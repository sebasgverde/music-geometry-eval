# --------------------------------------------
# Copyright (c) 2018 sebastian garcia valencia
# --------------------------------------------

import pickle
import argparse
from itertools import groupby

def eval_song(song):
	return sum(song) / float(len(song))

def calculate_general_tonality(cmm, lm, centr):
	return cmm + lm + centr

def calculate_conjunct_melodic_motion(song):
    changes = []

    for i in range(len(song)-1):
        changes.append(abs(song[i+1] - song[i]))

    return sum(changes)/float(len(song)-1)	

def calculate_limited_macroharmony(song, span_size=12):

	lower_limit = 5
	upper_limit = 8

	def local_lim_macrohar(song, lower_limit, upper_limit):
		number_of_notes = len(set(song))
		if lower_limit <= number_of_notes <= upper_limit:
			return 1
		elif number_of_notes < lower_limit:
			return (lower_limit - number_of_notes) + 1
		else:
			return (number_of_notes - lower_limit) + 1

	if len(song) <= span_size:
		result = local_lim_macrohar(song, lower_limit, upper_limit)
	else:
		number_of_spans = (len(song) - span_size) + 1

		span_scores = []
		for i in range(number_of_spans):
			span_scores.append(local_lim_macrohar(song[i:i + span_size], lower_limit, upper_limit))

		result = sum(span_scores)/float(number_of_spans)


	return float(result)
	
def calculate_centricity(song, span_size=12, min_probability = 0.2):

	# just the frecuency, making the metric more descriptive
	def local_centricity_simple(song):
		notes_group = [len(list(group)) for key, group in groupby(song)]
		group_sum = float(sum(notes_group))
		frecuencies = [a/group_sum for a in notes_group]

		cental_note_frec = max(frecuencies)	

		return cental_note_frec

	# this is a quite more complex way to calculate the centricity based in a threshold
	# the problem is that it is no clear why it should be one no matters if the frecuency is 
	# just about the threshold or is 1.9 meaning always the same note
	def local_centricity(song, min_probability):
		notes_group = [len(list(group)) for key, group in groupby(song)]
		group_sum = float(sum(notes_group))
		frecuencies = [a/group_sum for a in notes_group]

		cental_note_frec = max(frecuencies)
		if cental_note_frec >= min_probability:
			return 1
		else:
			return (min_probability - cental_note_frec) * 10 + 1

	if len(song) <= span_size:
		# result = local_centricity(song, min_probability)	
		result = local_centricity_simple(song)	
	else:
		number_of_spans = (len(song) - span_size) + 1

		span_scores = []
		for i in range(number_of_spans):

			# span_scores.append(local_centricity(song[i:i + span_size], min_probability))
			span_scores.append(local_centricity_simple(song[i:i + span_size]))

		result = sum(span_scores)/float(number_of_spans)


	return float(result)

parser = argparse.ArgumentParser(
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--input_pickle', type=str, default='example_pickle_song.p',
                    help='uri of the pickle with the data')
parser.add_argument('--type', type=str, default='song',
                    help='song or song_list')


# some testing

# # --------------------CMM--------------------------------
# print('CMM : {0}'.format(calculate_conjunct_melodic_motion([60,61,62,63,62,63])))
# print('CMM : {0}'.format(calculate_conjunct_melodic_motion([60,62,62,63,62,63])))
# print('CMM : {0}'.format(calculate_conjunct_melodic_motion([60,61,62,62,63,62,63])))
# print('CMM : {0}'.format(calculate_conjunct_melodic_motion([60,61,62,65,62,63])))

# # --------------------LM--------------------------------
# print('LM : {0}'.format(calculate_limited_macroharmony([60,61,62,63,64,65,66,67,68,69,70])))
# print('LM : {0}'.format(calculate_limited_macroharmony([60,61,62,63,64,65,66,67,67,67,67,67])))
# print('LM : {0}'.format(calculate_limited_macroharmony([60,61,62,63])))
# print('LM : {0}'.format(calculate_limited_macroharmony([60,61,62,63,64,65,66,67,67,67,67,67,65,65,66,67,67,78])))
# # --------------------CEN--------------------------------
# print('CEN : {0}'.format(calculate_centricity([60,61,62,62,62,62,61,61])))
# print('CEN : {0}'.format(calculate_centricity([60,62,63,64,65,66,67])))
# print('CEN : {0}'.format(calculate_centricity([60,61,62,62,62,62,61,61,65,65,65,65,54,54,54,54,67,68,69,60,61])))
# print('CEN : {0}'.format(calculate_centricity([60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,61,62])))
