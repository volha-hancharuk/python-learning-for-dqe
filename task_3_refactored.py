import re


def get_new_sentence(capitalized_text):
    additional_sentence = []                                                                                    # create empty list to store last words from each sentence
    for sentence in capitalized_text:                                                                           # iterate through each sentence in the processed text list
        if ' ' in sentence:                                                                                     # check that sentence contains at least one space (means more than one word)
            words = re.split(r'\s', sentence)                                                           # split sentence into words using any whitespace as separator
            last_word = words[-1].strip('.')                                                                    # take last word and remove trailing period if exists
            additional_sentence.append(f"{last_word}")                                                          # add last word to the list
    additional_sentence[0] = additional_sentence[0].capitalize()                                                # capitalize first word of the new constructed sentence
    return ' '.join(' ' + word for word in additional_sentence)                                                 # join all collected words into one string, adding space before each word


def fix_mistake(mistake, replacement):
    def decorator(func):                                                                                        # receives function to decorate
        def wrapper(*args, **kwargs):                                                                                      # wrapper replaces original function
            result = func(*args, **kwargs)                                                                                 # call original function first
            return [s.replace(mistake, replacement) for s in result]                                            # replace mistake with replacement in each sentence
        return wrapper                                                                                          # return modified wrapper instead of original function
    return decorator                                                                                            # return decorator function


@fix_mistake(' iz ', ' is ')                                                                 # apply decorator: fix " iz " after capitalization function runs
def capitalize_text(text, protected_words=[], sentence_pattern: str = r'[^.!?:]+[.!?:]+'):
    split_text = re.findall(sentence_pattern, text)                                                   # split full text into sentences including punctuation
    capitalized_text = []                                                                                       # empty list to store normalized sentences
    for sentence in split_text:															    	                # iterate through each sentence
        capitalized_sentence = sentence.strip().capitalize()												    # remove excessive whitespaces and capitalize the first letter in the sentence
        for w in protected_words:
            capitalized_sentence = re.sub(rf'\b{w.lower()}\b', w, capitalized_sentence, flags=re.IGNORECASE)    # to prevent lower case for last names, cities, etc.
        capitalized_sentence = re.sub(r'[A-Za-z].*', f'{capitalized_sentence}', sentence)	        # replace text in initial sentence with capitalized text keeping original leading spaces/indentation
        capitalized_text.append(capitalized_sentence)															# add formatted sentence to list
    return capitalized_text


def add_sentence_to_text(end_pattern, text, new_sentence):
    for i, sentence in enumerate(text):                                                                         # iterate through sentences with index
        if sentence.endswith(end_pattern):                                                                      # check if sentence ends with specific pattern
            text.insert(i + 1, f'{new_sentence}.')                                                              # insert new sentence right after matching sentence
    return text


def count_spaces(text):
    space_num = 0                                                                                               # initialize the counter of whitespaces
    for s in text:                                                                                              # iterate through every character in text
        if s.isspace():                                                                                         # check if the symbol is whitespace
            space_num += 1                                                                                      # increment counter
    return space_num


if __name__ == '__main__':
    text = """homEwork:
    tHis iz your homeWork, copy these Text to variable.

    You NEED TO normalize it fROM letter CASEs point oF View. also, create one MORE senTENCE witH LAST WoRDS of each existING SENtence and add it to the END OF this Paragraph.

    it iZ misspeLLing here. fix“iZ” with correct “is”, but ONLY when it Iz a mistAKE.

    last iz TO calculate nuMber OF Whitespace characteRS in this Text. caREFULL, not only Spaces, but ALL whitespaces. I got 87."""
    c_text = capitalize_text(text)                                                                              # normalize text and fix "iz" mistake via decorator
    # print(c_text)
    new_sentence = get_new_sentence(c_text)                                                                     # generate new sentence from last words
    new_text_list = add_sentence_to_text('paragraph.', c_text, new_sentence)                         # insert new sentence after sentence ending with "paragraph."
    # print(new_text_list)
    # normalized_text = lambda x: ''.join(x)                                                                    # alternative lambda way to join list into string (commented)
    normalized_text = ''.join(new_text_list)                                                                    # join all sentences into single string
    print(normalized_text)                                                                                      # print final normalized text
    # space_num = sum(s.isspace() for s in text)                                                                # alternative whitespace counting methods (commented)
    # space_num = sum(map(lambda s: 1 if s.isspace() else 0, text))                                             # alternative whitespace counting methods (commented)
    print(f'\n\n\tI have got {count_spaces(text)} whitespaces.')                                                # print total number of whitespace characters in original text
