import random
from collections import Counter


# random.seed(1)                                                  # for debugging purpose to generate stable random list
# 1. create a list of random number of dicts (from 2 to 10)
dict_list = []                                                    # initialize empty list of dictionaries

for _ in range(random.randint(2, 10)):                      # initialize number of dictionaries and call everyone
    keys_num = random.randint(2, 10)                        # generate number of elements in dictionary
    gen_dict = {}                                                 # generate empty dictionary
    for _ in range(keys_num):                                     # used for iterating over a sequence in dictionary
        k = chr(random.randint(ord('a'), ord('a')+9))             # initialize letter as key
        if k not in gen_dict:                                     # check to avoid duplicates
            gen_dict[k] = random.randint(0, 100)            # add key:value pair into generated dictionary
    dict_list.append(dict(sorted(gen_dict.items())))              # add generated dictionary to list of dictionaries

# 2. get previously generated list of dicts and create one common dict:
common_dict = {}                                                  # initialize empty common dict
counts = Counter()                                                # count time of key appearance in all dictionaries

for d in dict_list:                                               # iterate with every dict in dict list
    counts.update(d.keys())                                       # if letter appeared -> add count +1

for kc, vc in counts.items():                                     # iterate with key, value in counted keys
    if counts[kc] == 1:                                           # if letter appears 1 time
        for d in dict_list:                                       # iterate with every dict in dict list
            if kc in d:                                           # check if letter is in dict
                value = d[kc]                                     # save value of letter
                common_dict[kc] = value                           # add key:value pair into common dict
                break                                             # stop iteration whet condition met
    elif counts[kc] > 1:                                          # if letter appears more then 1 time
        indexed_letters = {}                                      # initialize dict to save key with index and value
        for i, d in enumerate(dict_list, 1):                      # iterate with every dict in dict list
            if kc in d:                                           # check if letter is in dict
                value = d[kc]                                     # save value of letter
                indexed_letters[f'{kc}_{i}'] = value              # add key:value pair into indexed letters dict
        max_value = max(indexed_letters.values())                 # find max value in indexed letters dict
        for k, v in indexed_letters.items():                      # iterate with every dict indexed letters dict
            if v == max_value:                                    # check if value is equal to max value
                max_key = k                                       # save key of max value
                break                                             # stop iteration whet condition met
        common_dict[max_key] = max_value                          # add key:value pair into common dict


if __name__ == '__main__':
    print(dict_list)
    print(dict(sorted(common_dict.items())))

