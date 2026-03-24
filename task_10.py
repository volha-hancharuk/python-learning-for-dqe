from abc import ABC, abstractmethod
from datetime import datetime, date
import os
import task_3_refactored
import task_7
import json
import xml.etree.ElementTree as ET
import pyodbc


protected_words = ['Berlin','New York','Prague','Tokyo','March','Sydney','Opera House','April','Toronto','Barcelona',
                   'Dubai','Moscow','Paris','Louvre','iPhone','Pro','Desert','Titanium','Manhattan','R18','GB',
                   'PlayStation','MacBook','Air','M3','Trek Marlin','V15','Submariner','Date','LN','Taylor Swift','The',
                   'Eras','Tour','Final','size L','European','Dates','London','Winter','Full','Moon','Edition',
                   'Alpe d’Huez','NBA','Lakers','Warriors','Regular','Season','Los Angeles','Music','Spheres','World',
                   'Mexico City','Blossom','Festival','Opening','Night','Kyoto','Main Stage','Bangkok','Food','Soleil',
                   'Las Vegas','International','Comedy','Gala','Carnival','Sambadrome','Parade','Melbourne','Return',
                   'Rio de Janeiro','Shows','Wilanów','RAM']


class DBConnection:
    def __init__(self, db):
        self.db = db

        conn_str = (
            "DRIVER=SQLite3;"
            f"DATABASE={self.db};"
        )

        self.conn = pyodbc.connect(conn_str, autocommit=True)
        self.cur = self.conn.cursor()

    def _initialize(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS news_feed (
                type TEXT NOT NULL CHECK(type IN ('NEWS', 'PRIVATE AD', 'EVENT')),
                text TEXT NOT NULL,
                city TEXT,
                date TEXT
            )
            """)

    def _get_feed(self, type_, text, city=None):
        try:
            if city is None:
                self.cur.execute("""
                            SELECT * FROM news_feed
                            WHERE type = ? 
                              AND text = ? 
                              AND city IS NULL
                        """, (type_, text))
            else:
                self.cur.execute("""
                            SELECT * FROM news_feed
                            WHERE type = ? 
                              AND text = ? 
                              AND city = ?
                        """, (type_, text, city))
            return self.cur.fetchone() is not None
        except pyodbc.Error as e:
            print("Error querying feed:", e)
            raise

    def _insert_feed(self, type_, text, city=None, date=None):
        try:
            self.cur.execute("""
                INSERT INTO news_feed (type, text, city, date)
                VALUES (?, ?, ?, ?)
            """, (type_, text, city, date))
            return self.cur.rowcount
        except pyodbc.Error as e:
            print("Error inserting feed:", e)
            raise

    def add_feed_to_db(self, type_, text, city=None, date=None):
        self._initialize()
        try:
            exists = self._get_feed(type_, text, city)
            if not exists:
                rowcount = self._insert_feed(type_, text, city, date)
            else:
                rowcount = 0
            return rowcount
        except ValueError as e:
            print("Something goes wrong with adding feed:", e)
            raise
        finally:
            self.close()

    def close(self):
        self.conn.close()


class NewsFeedItems(ABC):
    def __init__(self, text, file_to_publish):
        self.text = text.strip()
        self.file_to_publish = file_to_publish
        self.timestamp = datetime.now()

    @abstractmethod
    def publish(self):
        pass

    def publish_feed_to_text_file(self, record):
        if record is None:
            return False

        with open(self.file_to_publish, "a", encoding="utf-8") as f:
            f.write(record)
            print(f"\nRecord added to {self.file_to_publish}")

        with open(self.file_to_publish, 'r') as f:
            content = f.read()
            task_7.count_words(content)
            task_7.count_letters(content)

        return True


class News(NewsFeedItems):
    def __init__(self, text, city, file_to_publish):
        super().__init__(text, file_to_publish)
        self.city = city
        self.timestamp = datetime.now().strftime("%d/%m/%Y %H:%m")

    def publish(self):
        pub_type = 'NEWS'
        text = task_3_refactored.capitalize_text(self.text, protected_words, '.*')
        text = ''.join(text)
        record = (f"{pub_type} -------------------------\n"
                  f"{text}\n"
                  f"{self.city.capitalize()}, {self.timestamp}\n\n")
        db = DBConnection('task_10.db')
        rowcount = db.add_feed_to_db(pub_type, text, self.city, self.timestamp)
        if rowcount == 1:
            self.publish_feed_to_text_file(record)
        else:
            print("Record already exists (skipped)")
        return record


class PrivateAd(NewsFeedItems):
    def __init__(self, text, expiration_date, file_to_publish):
        super().__init__(text, file_to_publish)
        self.expiration_date = expiration_date

    def publish(self):
        pub_type = 'PRIVATE AD'
        text = task_3_refactored.capitalize_text(self.text, protected_words, '.*')
        text = ''.join(text)
        days_delta = self._calculate_date_delta(self.expiration_date)
        record = (f"{pub_type} -------------------\n"
                  f"{text}\n"
                  f"Actual until: {self.expiration_date}, {days_delta}\n\n")
        db = DBConnection('task_10.db')
        rowcount = db.add_feed_to_db(type_=pub_type, text=text, date=self.expiration_date)
        if rowcount == 1:
            self.publish_feed_to_text_file(record)
        else:
            print("Record already exists (skipped)")
        return record

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
    def __init__(self, text, city, event_time, file_to_publish):
        super().__init__(text, file_to_publish)
        self.city = city
        self.event_time = event_time

    def publish(self):
        pub_type = 'EVENT'
        text = task_3_refactored.capitalize_text(self.text, protected_words, '.*')
        text = ''.join(text)
        record = (f"{pub_type} ------------------------\n"
                  f"{text}\n"
                  f"{self.city.capitalize()}, {self.event_time}\n\n")
        db = DBConnection('task_10.db')
        rowcount = db.add_feed_to_db(pub_type, text, self.city, self.event_time)
        if rowcount == 1:
            self.publish_feed_to_text_file(record)
        else:
            print("Record already exists (skipped)")
        return record


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
                    record = News(text, city, self.file_to_publish)
                    print(f"\n\n{record.publish()}")
                    added_count += 1
                elif lines[0].upper().startswith('PRIVATE AD'):
                    text = lines[1]
                    expiration_date = lines[2]
                    record = PrivateAd(text, expiration_date, self.file_to_publish)
                    print(f"\n\n{record.publish()}")
                    added_count += 1
                elif lines[0].upper().startswith('EVENT'):
                    text = lines[1]
                    city = lines[2]
                    event_date = lines[3]
                    record = Event(text, city, event_date, self.file_to_publish)
                    print(f"\n\n{record.publish()}")
                    added_count += 1
                else:
                    raise ValueError(f"Incorrect format record '{existing_feed}'.")

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
                        record = News(text, city, self.file_to_publish)
                        print(f"\n\n{record.publish()}")
                        added_count += 1
                    elif feed["publication_type"] == 'ad':
                        text = feed["text"]
                        expiration_date = feed["exp_date"]
                        record = PrivateAd(text, expiration_date, self.file_to_publish)
                        print(f"\n\n{record.publish()}")
                        added_count += 1
                    elif feed["publication_type"] == 'event':
                        text = feed["text"]
                        city = feed["city"]
                        event_date = feed["evn_date"]
                        record = Event(text, city, event_date, self.file_to_publish)
                        print(f"\n\n{record.publish()}")
                        added_count += 1
                    else:
                        raise ValueError(f"Incorrect format record '{feed}'.")

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
                    record = News(text, city, self.file_to_publish)
                    print(f"\n\n{record.publish()}")
                    added_count += 1

                elif publication_type == 'ad':
                    text = item.find('text').text
                    expiration_date = item.find('exp_date').text
                    record = PrivateAd(text, expiration_date, self.file_to_publish)
                    print(f"\n\n{record.publish()}")
                    added_count += 1

                elif publication_type == 'event':
                    text = item.find('text').text
                    city = item.find('city').text
                    event_date = item.find('evn_date').text
                    record = Event(text, city, event_date, self.file_to_publish)
                    print(f"\n\n{record.publish()}")
                    added_count += 1
                else:
                    raise ValueError(f"Incorrect format record '{item}'.")

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
                        record = News(text, city, self.filename)

                    elif select_feed_type == 'private ad':
                        text = input("Ad text: ").strip()
                        exp = input("Expiration (DD/MM/YYYY): ").strip()
                        record = PrivateAd(text, exp, self.filename)

                    elif select_feed_type == 'event':
                        text = input("Ad text: ").strip()
                        city = input("City: ").strip()
                        exp = input("Expiration (DD/MM/YYYY HH:MM): ").strip()
                        record = Event(text, city, exp, self.filename)

                    else:
                        print("Wrong type. Use exactly news, private ad, event")
                        continue

                    print(f"\n\n{record.publish()}")
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

