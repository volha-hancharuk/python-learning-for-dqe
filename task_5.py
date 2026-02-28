from abc import ABC, abstractmethod
from datetime import datetime, date
import os


class NewsFeedItems(ABC):
    def __init__(self, text):
        self.text = text.strip()
        self.timestamp = datetime.now()

    @abstractmethod
    def add_item(self):
        pass

    @staticmethod
    def _get_date():
        while True:
            user_input = input(f"Please enter date in format DD/MM/YYYY: ").strip()
            try:
                datetime.strptime(user_input, "%d/%m/%Y").date()
                return user_input
            except ValueError:
                print("Wrong format. Use exactly DD/MM/YYYY")

    @staticmethod
    def _get_time():
        while True:
            user_input = input(f"Please enter time in format HH:MM: ").strip()
            try:
                datetime.strptime(user_input, "%H:%M").time()
                return user_input
            except ValueError:
                print("Wrong format. Use exactly HH:MM")


class News(NewsFeedItems):
    def __init__(self):
        super().__init__('NEWS -------------------------')

    def add_item(self):
        news = input(f"Please enter the news: ").strip()
        city = input(f"Please enter city: ").strip()
        self.timestamp = datetime.now().strftime("%d/%m/%Y %H:%m")
        return (f"\n{self.text}\n"
                f"{news}\n"
                f"{city.capitalize()}, {self.timestamp}\n")


class PrivateAd(NewsFeedItems):
    def __init__(self):
        super().__init__('PRIVATE AD -------------------')

    def add_item(self):
        private_ad = input(f"Please enter your add: ").strip()
        expiration_date = self._get_date()
        days_delta = self._calculate_date_delta(expiration_date)
        return (f"\n{self.text}\n"
                f"{private_ad}\n"
                f"Actual until: {expiration_date}, {days_delta}\n")

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
    def __init__(self):
        super().__init__('EVENT ------------------------')

    def add_item(self):
        artist = input(f"Please enter name of event: ").strip()
        city = input(f"Please enter city of event: ").strip()
        event_date = self._get_date()
        event_start_time = self._get_time()
        return (f"\n{self.text}\n"
                f"{artist}\n"
                f"{city.capitalize()}, {event_date} {event_start_time}\n")


class NewsFeed:
    HEADER = "News feed:\n\n"

    def __init__(self, filename: str = "news_feed.txt"):
        self.filename = filename
        self.items: list[str] = []

        if not os.path.exists(filename):
            with open(filename, "w", encoding="utf-8") as f:
                f.write(self.HEADER)
            print(f"Created new feed file: {filename}")
            print("Added initial header: 'News feed:'")
        else:
            self._load_file()

    def _load_file(self):
        try:
            with open(self.filename, encoding="utf-8") as f:
                file_content = f.read()
                existing_feeds = file_content.split('\n\n')
                for existing_feed in existing_feeds[1:]:
                    if existing_feed:
                        self.items.append(existing_feed)
        except Exception as e:
            print(f"Warning: could not load feed file: {e}")

    def _append_item(self, item: str):
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(item)
        self.items.append(item)
        print(f"→ Published: \n{item}\n")

    def add_news(self):
        news = News()
        item = news.add_item()
        self._append_item(item)

    def add_private_ad(self):
        ads = PrivateAd()
        ad = ads.add_item()
        self._append_item(ad)

    def add_event(self):
        events = Event()
        event = events.add_item()
        self._append_item(event)

    def add_feed(self):
        while True:
            select_feed_type = input(f"Please select type of feed (news, private ad, event): ")
            if select_feed_type == 'news':
                return self.add_news()
            elif select_feed_type == 'private ad':
                return self.add_private_ad()
            elif select_feed_type == 'event':
                return self.add_event()
            else:
                print("Wrong type. Use exactly news, private ad, event")

    def print_recent_feeds(self, num = 3):
        if not self.items:
            print("Feed is empty.\n")
            return

        print("\n" + "═" * 70)
        print(f" Recent feed entries (newest at bottom)")
        print("═" * 70)

        for item in self.items[-num:]:
            print(f"{item}\n")


if __name__ == '__main__':
    feed = NewsFeed()
    feed.add_feed()
    feed.add_feed()
    feed.add_feed()
    feed.print_recent_feeds(3)