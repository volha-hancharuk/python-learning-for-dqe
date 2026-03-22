from abc import ABC, abstractmethod
from datetime import datetime, date
import os
import task_3_refactored
import task_7
import json
import xml.etree.ElementTree as ET


protected_words = ['Berlin','New York','Prague','Tokyo','March','Sydney','Opera House','April','Toronto','Barcelona',
                   'Dubai','Moscow','Paris','Louvre','iPhone','Pro','Desert','Titanium','Manhattan','R18','GB',
                   'PlayStation','MacBook','Air','M3','Trek Marlin','V15','Submariner','Date','LN','Taylor Swift','The',
                   'Eras','Tour','Final','size L','European','Dates','London','Winter','Full','Moon','Edition',
                   'Alpe d’Huez','NBA','Lakers','Warriors','Regular','Season','Los Angeles','Music','Spheres','World',
                   'Mexico City','Blossom','Festival','Opening','Night','Kyoto','Main Stage','Bangkok','Food','Soleil',
                   'Las Vegas','International','Comedy','Gala','Carnival','Sambadrome','Parade','Melbourne','Return',
                   'Rio de Janeiro','Shows']


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


class AskFile:
    def __init__(self, file_format: str = None):
        self.file_format = file_format

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
                     and f.lower().endswith(self.file_format)]
            if not files:
                print(f"No files found in default folder.")
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
                select_file = input(f"Select file number: "
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
            elif not user_input.endswith(self.file_format):
                print(f"Incorrect file type is added.")
                return None
            else:
                print(f"File {user_input} is not found.")
                return None


class File(ABC):
    def __init__(self, file_to_publish):
        self.file_to_publish = file_to_publish

    def process_text_file(self, file_path):
        pass


class TextFile(File):
    def __init__(self, file_to_publish: str = None):
        super().__init__(file_to_publish)

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
        failed = []
        for existing_feed in existing_feeds:
            lines = existing_feed.split('\n')
            try:
                if lines[0].upper().startswith('NEWS'):
                    text = lines[1]
                    city = lines[2]
                    record = News(text, city)
                    print(f"\n\n{record.publish()}")
                    added_count += 1
                elif lines[0].upper().startswith('PRIVATE AD'):
                    text = lines[1]
                    expiration_date = lines[2]
                    record = PrivateAd(text, expiration_date)
                    print(f"\n\n{record.publish()}")
                    added_count += 1
                elif lines[0].upper().startswith('EVENT'):
                    text = lines[1]
                    city = lines[2]
                    event_date = lines[3]
                    record = Event(text, city, event_date)
                    print(f"\n\n{record.publish()}")
                    added_count += 1
                else:
                    raise ValueError(f"Incorrect format record '{existing_feed}'.")
                news_feed = NewsFeed(self.file_to_publish)
                news_feed._add_record_if_not_exists(record)

            except Exception as e:
                print(f"\nSkipped invalid record:\n{existing_feed}\n→ {e}\n")
                failed.append(existing_feed)

        if failed:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n\n".join(failed))
        if added_count == len(existing_feeds):
            print(f"All records are successfully added. File {file_path} is removing")
            os.remove(file_path)
        return


class JsonFile(File):
    """For successful processing json should be in format:
    {
    "1": [
        {
            "publication_type": "news/private ad/event",
            "text": "test",
            "city": "city", for news/event
            "exp_date": "25/03/2026" for private ad
            "evn_date": "20/03/2026" for event
        }
    ]
    }"""
    def __init__(self, file_to_publish: str = None):
        super().__init__(file_to_publish)

    def process_text_file(self, file_path):
        if not os.path.isfile(file_path):
            print(f"File not found: {file_path}")
            return 0

        with open(file_path, encoding="utf-8") as f:
            existing_feeds = json.load(f)

        if existing_feeds == {}:
            print(f"File is empty.")
            os.remove(file_path)
            print(f"File {os.path.basename(file_path)} successfully removed.")
            return None

        added_count = 0
        failed = {}
        feeds_count = 0
        for number, list in existing_feeds.items():
            feeds_count += len(list)
            try:
                for feed in list:
                    if feed["publication_type"] == 'news':
                        text = feed["text"]
                        city = feed["city"]
                        record = News(text, city)
                        print(f"\n\n{record.publish()}")
                        added_count += 1
                    elif feed["publication_type"] == 'ad':
                        text = feed["text"]
                        expiration_date = feed["exp_date"]
                        record = PrivateAd(text, expiration_date)
                        print(f"\n\n{record.publish()}")
                        added_count += 1
                    elif feed["publication_type"] == 'event':
                        text = feed["text"]
                        city = feed["city"]
                        event_date = feed["evn_date"]
                        record = Event(text, city, event_date)
                        print(f"\n\n{record.publish()}")
                        added_count += 1
                    else:
                        raise ValueError(f"Incorrect format record '{feed}'.")
                    news_feed = NewsFeed(self.file_to_publish)
                    news_feed._add_record_if_not_exists(record)

            except Exception as e:
                print(f"Skipped invalid record:\n{list}\n→ {e}\n")
                if number not in failed:
                    failed[number] = []
                failed[number].append(feed)

        if failed:
            json.dump(failed, open(file_path, "w"), indent=4)

        if added_count == feeds_count:
            print(f"All records are successfully added. File {file_path} is removing")
            os.remove(file_path)
        return


class XmlFile(File):
    """For successful processing xml should be in format:
    <feeds>
        <item>
            <publication_type>news/private ad/event</publication_type>
            <text>text</text>
            <city>city</city>   for news/event
            <exp_date>25/03/2026</exp_date>   for private ad
            <evn_date>25/03/2026</evn_date>   for event
        </item>
    </feeds>
    """
    def __init__(self, file_to_publish: str = None):
        super().__init__(file_to_publish)

    def process_text_file(self, file_path):
        if not os.path.isfile(file_path):
            print(f"File not found: {file_path}")
            return 0

        if os.path.getsize(file_path) == 0:
            print(f"File is empty.")
            os.remove(file_path)
            print(f"File {os.path.basename(file_path)} successfully removed.")
            return None

        xml_file = ET.parse(file_path)
        root = xml_file.getroot()

        added_count = 0
        xml_idx = 0
        failed = ET.Element('feeds')
        items_len = len(root.findall('.//item'))
        for item in root.findall('.//item'):
            try:
                publication_type = item.find('publication_type').text.lower()
                if publication_type == 'news':
                    text = item.find('text').text
                    city = item.find('city').text
                    record = News(text, city)
                    print(f"\n\n{record.publish()}")
                    added_count += 1

                elif publication_type == 'ad':
                    text = item.find('text').text
                    expiration_date = item.find('exp_date').text
                    record = PrivateAd(text, expiration_date)
                    print(f"\n\n{record.publish()}")
                    added_count += 1

                elif publication_type == 'event':
                    text = item.find('text').text
                    city = item.find('city').text
                    event_date = item.find('evn_date').text
                    record = Event(text, city, event_date)
                    print(f"\n\n{record.publish()}")
                    added_count += 1
                else:
                    raise ValueError(f"Incorrect format record '{item}'.")
                news_feed = NewsFeed(self.file_to_publish)
                news_feed._add_record_if_not_exists(record)

            except Exception as e:
                print(f"Skipped invalid record:\n{item}\n→ {e}\n")
                failed_item = ET.SubElement(failed, 'item')

                publication_type_elem = item.find('publication_type')
                if publication_type_elem is not None:
                    ET.SubElement(failed_item, 'publication_type').text = publication_type_elem.text

                text_elem = item.find('text')
                if text_elem is not None:
                    ET.SubElement(failed_item, 'text').text = text_elem.text

                city_elem = item.find('city')
                if city_elem is not None:
                    ET.SubElement(failed_item, 'city').text = city_elem.text

                exp_elem = item.find('exp_date')
                if exp_elem is not None:
                    ET.SubElement(failed_item, 'exp_date').text = exp_elem.text

                event_elem = item.find('evn_date')
                if event_elem is not None:
                    ET.SubElement(failed_item, 'evn_date').text = event_elem.text
                xml_idx += 1

        if len(failed):
            tree = ET.ElementTree(failed)
            ET.indent(tree, space="    ", level=0)  # 4 spaces
            tree.write(file_path, encoding="utf-8")

        if added_count == items_len:
            print(f"All records are successfully added. File {file_path} is removing")
            os.remove(file_path)
        return


class NewsFeed:
    def __init__(self, filename: str = "news_feed.txt"):
        self.filename = filename

        if not os.path.exists(filename) or os.path.getsize(filename) == 0:
            with open(filename, "w", encoding="utf-8") as f:
                f.write("News feed:\n\n")
            print(f"Created new feed file: {filename}")
            print("Added initial header: 'News feed:'")

    def _add_record_if_not_exists(self, record):
        if record is None:
            return False

        published = record.publish()
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            content = ""

        if published.strip() in content:
            print("Record already exists (skipped)")
            return False

        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(published)
        print(f"\nRecord added to {self.filename}")

        with open(self.filename, 'r') as f:
            content = f.read()
            task_7.count_words(content)
            task_7.count_letters(content)

        return True

    def interactive_mode(self):
        while True:
            select_adding_type = input(f"Please select how you want to add a feed:\n"
                                       f"1 - manually\n"
                                       f"2 - using text file\n"
                                       f"3 - using json file\n"
                                       f"4 - using xml file\n"
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

                    elif select_feed_type == 'private ad':
                        text = input("Ad text: ").strip()
                        exp = input("Expiration (DD/MM/YYYY): ").strip()
                        record = PrivateAd(text, exp)

                    elif select_feed_type == 'event':
                        text = input("Ad text: ").strip()
                        city = input("City: ").strip()
                        exp = input("Expiration (DD/MM/YYYY HH:MM): ").strip()
                        record = Event(text, city, exp)

                    else:
                        print("Wrong type. Use exactly news, private ad, event")
                        continue

                    self._add_record_if_not_exists(record)
                    return

            elif select_adding_type == '2':
                file_path = AskFile(".txt")._ask_file_path()
                if not file_path:
                    return
                importer = TextFile(self.filename)
                importer.process_text_file(file_path)
                return

            elif select_adding_type == '3':
                file_path = AskFile(".json")._ask_file_path()
                if not file_path:
                    return
                importer = JsonFile(self.filename)
                importer.process_text_file(file_path)
                return

            elif select_adding_type == '4':
                file_path = AskFile(".xml")._ask_file_path()
                if not file_path:
                    return
                importer = XmlFile(self.filename)
                importer.process_text_file(file_path)
                return

            elif select_adding_type == '0':
                break

            else:
                print("Invalid choice.")
                continue


if __name__ == '__main__':
    feed1 = NewsFeed()
    feed1.interactive_mode()

