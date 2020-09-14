# --------------------------------------------
# Copyright (c) 2018 sebastian garcia valencia
# --------------------------------------------

import pickle
import argparse
from itertools import groupby

# ----------------------------
# polyphonic
# ----------------------------



def calculate_polyphonic_limited_macroharmony_feature_vec(song_feature_vec, span_size=8, lower_limit = 5, upper_limit = 8):
	# my_list=[[0,0],[0,0],[1,0][0,0][1,1]]

	"""
	It calculates the percentage of spans in wich the total of distinct
	notes is in the range [5,8]
	"""

	def count_distinct_notes_feature_vec(song_feature_vec_span):
		"""
		For each note, it checks if it sounds at least one time in the span,
		it only looks for the first channel since if a held note reach a new
		span it will count it.

		:returns: the total of distinct notes
		"""
		notes_counter = 0
		for i in range(song_feature_vec_span.shape[1]):
			if len([x for x in song_feature_vec_span[:,i] if x[0]==1]) > 0:
				 notes_counter+=1
		return notes_counter

	time_steps = song_feature_vec.shape[0]

	if time_steps <= span_size:
		span_scores = [count_distinct_notes_feature_vec(song_feature_vec)]
	else:
		number_of_spans = (time_steps - span_size) + 1

		span_scores = []
		for i in range(number_of_spans):
			span_scores.append(count_distinct_notes_feature_vec(song_feature_vec[i:i + span_size]))

		# print span_scores


	in_range_counter = 0
	for x in span_scores:
	    if x >= lower_limit and x <= upper_limit:
	        in_range_counter +=1
	result = in_range_counter/float(len(span_scores))

	return result

def calculate_polyphonic_centricity_feature_vec(song_feature_vec, span_size=4):

	"""
	calculates the frequency of the most frequent note for every span
	and then returns the average
	"""

	def frequency_notes_feature_vec(song_feature_vec_span):
		"""
		It counts the efective number of notes that are played in a span
		(including repetitive notes) then calculates the frecuancy of each
		one and returns the maximal
		"""
		notes_counter_array = []
		for i in range(song_feature_vec_span.shape[1]):
			notes_counter_array.append(len([x for x in song_feature_vec_span[:,i] if x[0]==1 and x[1]==1]))

		total_notes = float(sum(notes_counter_array))
		if total_notes > 0:
			frecuencies = [a/total_notes for a in notes_counter_array]
			return max(frecuencies)
		else:
			return 0


	time_steps = song_feature_vec.shape[0]

	import pdb; pdb.set_trace()
	if time_steps <= span_size:
		span_scores = [frequency_notes_feature_vec(song_feature_vec)]
	else:
		number_of_spans = (time_steps - span_size) + 1

		span_scores = []
		for i in range(number_of_spans):
			span_scores.append(frequency_notes_feature_vec(song_feature_vec[i:i + span_size]))
		# import pdb
		# pdb.set_trace()
		# print span_scores

	return sum(span_scores)/len(span_scores)

""""
----------------------------
 monophonic with time
----------------------------

In this case the base representations is a list where each element is a list
[pitch, time] where pitch is a midi int value and time is an int from 1 (16th note)
to 16 (whole note)
"""
def time_rep_song_to_16th_note_grid(time_rep_song):
	"""
	Transform the time_rep_song into an array of 16th note with pitches in the onsets

	[[60,4],[62,2],[60,2]] -> [60,0,0,0,62,0,60,0]
	"""

	grid_16th = []
	for pair_p_t in time_rep_song:
		grid_16th.extend([pair_p_t[0]] + [0 for _ in range(pair_p_t[1]-1)])

	return grid_16th

def calculate_time_supported_conjunct_melodic_motion(time_rep_song):
	"""
	this is just about the notes, so convert to pitch array and use
	normal cmm method
	"""
	song = [elem[0] for elem in time_rep_song]

	return calculate_conjunct_melodic_motion(song)

def calculate_time_supported_limited_macroharmony(time_rep_song, span_size=12, slide_windowsize=4):
	"""
	calculates the metric over 16th notes grids with a moving window of a quarter
	note (4)
	"""
	grid_16th_song = time_rep_song_to_16th_note_grid(time_rep_song)
	lower_limit = 5
	upper_limit = 8

	def local_lim_macrohar(song, lower_limit, upper_limit):
		# ignore 0s
		song = [elem for elem in song if elem != 0 ]
		number_of_notes = len(set(song))
		if lower_limit <= number_of_notes <= upper_limit:
			return 1
		elif number_of_notes < lower_limit:
			return (lower_limit - number_of_notes) + 1
		else:
			return (number_of_notes - lower_limit) + 1

	if len(grid_16th_song) <= span_size:
		result = local_lim_macrohar(grid_16th_song, lower_limit, upper_limit)
	else:
		number_of_spans = (len(grid_16th_song) - span_size)/slide_windowsize + 1

		span_scores = []
		for i in range(number_of_spans):
			span_scores.append(local_lim_macrohar(grid_16th_song[i*slide_windowsize:i*slide_windowsize + span_size], lower_limit, upper_limit))

		result = sum(span_scores)/float(number_of_spans)


	return float(result)

def calculate_time_supported_centricity(time_rep_song, span_size=12, slide_windowsize=4):
	"""
	calculates the metric over 16th notes grids with a moving window of a quarter
	note (4)
	"""
	grid_16th_song = time_rep_song_to_16th_note_grid(time_rep_song)

	# just the frecuency, making the metric more descriptive
	def local_centricity_simple(song):
		# ignore 0s
		song = [elem for elem in song if elem != 0 ]

		notes_group = [len(list(group)) for key, group in groupby(song)]
		group_sum = float(sum(notes_group))
		frecuencies = [a/group_sum for a in notes_group]

		cental_note_frec = max(frecuencies)

		return cental_note_frec

	if len(grid_16th_song) <= span_size:
		result = local_centricity_simple(grid_16th_song)
	else:
		number_of_spans = (len(grid_16th_song) - span_size)/slide_windowsize + 1

		span_scores = []
		for i in range(number_of_spans):

			span_scores.append(local_centricity_simple(grid_16th_song[i*slide_windowsize:i*slide_windowsize + span_size]))

		result = sum(span_scores)/float(number_of_spans)


	return float(result)


# assert time_rep_song_to_16th_note_grid([[60,4],[62,2],[60,2]]) ==  [60,0,0,0,62,0,60,0]


# ----------------------------
# monophonic
# ----------------------------
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

