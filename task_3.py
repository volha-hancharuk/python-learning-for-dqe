import re

text = """homEwork:
	tHis iz your homeWork, copy these Text to variable.

	You NEED TO normalize it fROM letter CASEs point oF View. also, create one MORE senTENCE witH LAST WoRDS of each existING SENtence and add it to the END OF this Paragraph.

	it iZ misspeLLing here. fix“iZ” with correct “is”, but ONLY when it Iz a mistAKE.

	last iz TO calculate nuMber OF Whitespace characteRS in this Text. caREFULL, not only Spaces, but ALL whitespaces. I got 87."""

splitted_text = re.split(r'[.:]', text)																# split the text to sentences by comma and colon
splitted_text.pop(-1)																						# remove excessive empty sentence appeared after split
normalized_text = []																					    # initialize empty list to collect normalized sentences
additional_sentence = []																					# initialize empty list to collect the last words in all sentences

for i, sentence in enumerate(splitted_text):																# iterate over each sentence
    if i == 0:																								# condition for the first word to save colon at the and of string
        capitalized_sentence = sentence.capitalize()														# make the first letter capital
        normalized_text.append(f"{capitalized_sentence}:")													# add sentence to the normalized text list
    elif i > 0:																								# condition for other sentences in text
        capitalized_sentence = sentence.strip().capitalize()												# remove excessive whitespaces and capitalize the first letter in the sentence
        sentence_without_mistakes = capitalized_sentence.replace(' iz ', ' is ')							# replace misspelled "iz" with correct "is"
        formatted_sentence = re.sub(r'[A-Za-z].*', f'{sentence_without_mistakes}.', sentence)	# replace text in initial sentence with capitalized text saving initial whitespaces
        if formatted_sentence.endswith('paragraph.'):                                                       # condition to check the sentence ends with "paragraph"
            index_to_add_sentence = i                                                                       # save index of sentence to add a new sentence after that
        words = re.split(r'\s', formatted_sentence)													# split words in sentence by space
        last_word = words[-1].strip('.')																	# save the last word in sentence
        normalized_text.append(formatted_sentence)															# add formatted sentence to the formatted text
        additional_sentence.append(f"{last_word}")															# add last words to additional sentence list

additional_sentence[0] = additional_sentence[0].capitalize()                                                # make the first letter of the first word capitalized in the list of additional words
new_sentence = ''.join(' ' + word for word in additional_sentence)                                          # join words in additional words list to the sentence
normalized_text.insert(index_to_add_sentence + 1, f'{new_sentence}.')                               # add a new sentence to the end of the second paragraph

space_num = 0                                                                                               # initialize the sum of whitespaces
for s in text:                                                                                              # iterate over symbols in the initial text
    if s.isspace():                                                                                         # check if the symbol is whitespace
        space_num += 1                                                                                      # update sum if symbol is whitespace


if __name__ == '__main__':
    print(''.join(normalized_text))
    print(f'\n\nI have got {space_num} whitespaces.')
