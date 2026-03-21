import csv
from collections import Counter
import re


def get_content_from_text_file(filename):
    with open(filename, 'r') as f:
        file_content = f.read()
        return file_content


def count_words(file_content):
    words = re.split(r"(\s|\n|\n\n)", file_content)
    words_counter = Counter()
    for w in words:
        words = re.findall(r"^[a-ząćęłńóśźż']+$", w.lower())
        words_counter.update(words)
    with open('counted_words.csv', 'w', newline='') as f:
        write_counted_words = csv.DictWriter(f, fieldnames=['word', 'count'])
        for k, v in words_counter.items():
            write_counted_words.writerow({'word': k, 'count': v})
    print(f"Counted words are added to counted_words.csv")


def count_letters(file_content):
    letters_counter = Counter()
    upper_letters_counter = Counter()
    for i in file_content:
        letter = re.findall(r'[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ]', i)
        if letter:
            letters_counter.update(i.lower())
            if i.isupper():
                upper_letters_counter.update(i)
    with open('counted_letters.csv', 'w', newline='') as f:
        headers = ['letter', 'count_all', 'count_uppercase', 'percentage']
        write_headers = csv.writer(f)
        write_headers.writerow(headers)
        write_counted_letters = csv.DictWriter(f, fieldnames=headers)
        for k, v in letters_counter.items():
            if k.upper() in upper_letters_counter:
                count_up = upper_letters_counter[k.upper()]
            else:
                count_up = 0
            perc = round(count_up / v * 100, 2)
            write_counted_letters.writerow({'letter': k, 'count_all': v, 'count_uppercase': count_up, 'percentage': perc})
    print(f"Counted letters are added to counted_letters.csv")


if __name__ == '__main__':
    text = get_content_from_text_file('news_feed.txt')
    count_w = count_words(text)
    count_l = count_letters(text)