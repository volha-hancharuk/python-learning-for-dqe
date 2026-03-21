from abc import ABC, abstractmethod
from datetime import datetime, date
import os
import task_3_refactored
import task_7


protected_words = ['M2', 'Służewiec', 'Poland', 'Prime Minister', 'Tusk', 'European', 'April', 'Warsaw', 'Half Marathon',
                   'Mokotów', 'Wilanów', 'National Bank', 'Middle East', 'Leonardo', 'Michał Anioł', 'Art Box',
                   'mObywatel', 'EU', 'ID', 'Poles', 'Yumi Zouma', 'Live', 'Hydrozagadka', 'Dawid Podsiadło',
                   'Arena Tour', 'Chopin', 'Piano', 'Concert', 'Heart', 'Gallery', 'ZPAF', 'Ichiko Aoba', 'size L',
                   'Pardon', 'To Tu', 'Indie', 'Night', 'Special', 'IKEA', 'BRIMNES', 'Rockrider ST']


class NewsFeedItems(ABC):
    def __init__(self, text):
        self.text = text.strip()
        self.timestamp = datetime.now()

    @abstractmethod
    def publish(self):
        pass


class News(NewsFeedItems):
    def __init__(self, text, city):
        super().__init__(text)
        self.city = city
        self.timestamp = datetime.now().strftime("%d/%m/%Y %H:%m")

    def publish(self):
        text = task_3_refactored.capitalize_text(self.text, protected_words, '.*')
        return (f"NEWS -------------------------\n"
                f"{''.join(text)}\n"
                f"{self.city.capitalize()}, {self.timestamp}\n\n")


class PrivateAd(NewsFeedItems):
    def __init__(self, text, expiration_date):
        super().__init__(text)
        self.expiration_date = expiration_date

    def publish(self):
        text = task_3_refactored.capitalize_text(self.text, protected_words, '.*')
        days_delta = self._calculate_date_delta(self.expiration_date)
        return (f"PRIVATE AD -------------------\n"
                f"{''.join(text)}\n"
                f"Actual until: {self.expiration_date}, {days_delta}\n\n")

    @staticmethod
    def _calculate_date_delta(exp_date):
        today = date.today()
        delta = datetime.strptime(exp_date, "%d/%m/%Y").date() - today
        if delta.days < 0:
            return "expired"
        elif delta.days == 0:
            return "today"
        elif delta.days == 1:
            return f"{delta.days} day left"
        else:
            return f"{delta.days} days left"


class Event(NewsFeedItems):
    def __init__(self, text, city, event_time):
        super().__init__(text)
        self.city = city
        self.event_time = event_time

    def publish(self):
        text = task_3_refactored.capitalize_text(self.text, protected_words, '.*')
        return (f"EVENT ------------------------\n"
                f"{''.join(text)}\n"
                f"{self.city.capitalize()}, {self.event_time}\n\n")


class TextFile:
    def __init__(self, filename_to_publish: str = None):
        self.filename_to_publish = filename_to_publish

    def _ask_file_path(self):
        default_folder = "feeds"
        print(f"Default folder is {default_folder}\n"
              f"Press Enter to proceed\n"
              f"Or enter full path to your file")
        user_input = input(f">>>").strip()

        if not user_input:
            if not os.path.exists(default_folder):
                print(f"Default folder {default_folder} does not exist.")
                return None

            files = [f for f in os.listdir(default_folder)
                     if os.path.isfile(os.path.join(default_folder, f))
                     and f.lower().endswith(".txt")]
            if not files:
                print(f"No text files found in default folder.")
                return None

            if len(files) == 1:
                file = files[0]
                full_file_path = os.path.join(default_folder, file)
                print(f"File for using: {full_file_path}")
                return str(full_file_path)

            print(f"\nThe following files are found:")
            for i, file in enumerate(files, 1):
                print(f"{i} {file}")

            while True:
                select_file = input(f"Select number of file: "
                                    f">>>").strip()
                if not select_file:
                    return None
                try:
                    idx = int(select_file) - 1
                    if 0 <= idx < len(files):
                        file = files[idx]
                        full_file_path = os.path.join(default_folder, file)
                        print(f"File for using: {full_file_path}")
                        return str(full_file_path)
                    else:
                        print("Invalid number.")
                except ValueError:
                    print("Please enter a number.")

        else:
            if os.path.isfile(user_input):
                return user_input
            else:
                print(f"File {user_input} is not found.")
                return

    def process_text_file(self, file_path):
        """For successful processing. the records should be in format:
         NEWS/PRIVATE AD/EVENT
         Some text related to record
         City (for NEWS/EVENT)
         Date (for PRIVATE AD)
         DATE TIME (for EVENT)"""
        if not os.path.isfile(file_path):
            print(f"File not found: {file_path}")
            return 0

        with open(file_path, encoding="utf-8") as f:
            file_content = f.read()
            existing_feeds = file_content.split('\n\n')

        if existing_feeds == ['']:
            print(f"File is empty.")
            os.remove(file_path)
            print(f"File {os.path.basename(file_path)} successfully removed.")
            return

        added_count = 0
        successful = []
        failed = []
        for existing_feed in existing_feeds:
            lines = existing_feed.split('\n')
            try:
                if lines[0].upper().startswith('NEWS'):
                    text = lines[1]
                    city = lines[2]
                    record = News(text, city)
                    print(record.publish())
                    added_count += 1
                elif lines[0].upper().startswith('PRIVATE AD'):
                    text = lines[1]
                    expiration_date = lines[2]
                    record = PrivateAd(text, expiration_date)
                    print(record.publish())
                    added_count += 1
                elif lines[0].upper().startswith('EVENT'):
                    text = lines[1]
                    city = lines[2]
                    event_date = lines[3]
                    record = Event(text, city, event_date)
                    print(record.publish())
                    added_count += 1
                else:
                    raise ValueError(f"Incorrect format record '{existing_feed}'.")
                successful.append(existing_feed)
                with open(self.filename_to_publish, "a", encoding="utf-8") as f:
                    f.write(record.publish())
            except Exception as e:
                print(f"Skipped invalid record:\n{existing_feed}\n→ {e}\n")
                failed.append(existing_feed)

        if failed:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n\n".join(failed))
        if added_count == len(existing_feeds):
            print(f"All records are successfully added. File {file_path} is removing")
            os.remove(file_path)
        return


class NewsFeed:
    def __init__(self, filename: str = "news_feed.txt"):
        self.filename = filename

        if not os.path.exists(filename):
            with open(filename, "w", encoding="utf-8") as f:
                f.write("News feed:\n\n")
            print(f"Created new feed file: {filename}")
            print("Added initial header: 'News feed:'")

    def interactive_mode(self):
        while True:
            select_adding_type = input(f"Please select how you want to add a feed:\n"
                                       f"1 - manually\n"
                                       f"2 - using text file\n"
                                       f"0 - quit/exit\n"
                                       f"Please enter 1, 2 or 0\n"
                                       f">>>").strip()

            if not select_adding_type:
                print(f"Please enter a number.")
                continue

            if select_adding_type == '1':
                while True:
                    select_feed_type = input(f"Please select type of feed (news, private ad, event): ")
                    if select_feed_type == 'news':
                        text = input("News text: ").strip()
                        city = input("City: ").strip()
                        record = News(text, city)
                        break
                    elif select_feed_type == 'private ad':
                        text = input("Ad text: ").strip()
                        exp = input("Expiration (DD/MM/YYYY): ").strip()
                        record = PrivateAd(text, exp)
                        break
                    elif select_feed_type == 'event':
                        text = input("Ad text: ").strip()
                        city = input("City: ").strip()
                        exp = input("Expiration (DD/MM/YYYY HH:MM): ").strip()
                        record = Event(text, city, exp)
                        break
                    else:
                        print("Wrong type. Use exactly news, private ad, event")
                        continue

                    with open(self.filename, "a", encoding="utf-8") as f:
                        f.write(record.publish())

                    print(f"\nRecord added to {self.filename}")
                    break

            elif select_adding_type == '2':
                file_path = TextFile(None)._ask_file_path()
                if not file_path:
                    return
                importer = TextFile(self.filename)
                importer.process_text_file(file_path)

            elif select_adding_type == '0':
                break
            else:
                print("Invalid choice.")
                continue

            with open(self.filename, 'r') as f:
                content = f.read()
                task_7.count_words(content)
                task_7.count_letters(content)

            return


if __name__ == '__main__':
    feed1 = NewsFeed()
    feed1.interactive_mode()

