from math import asin, sqrt, sin, cos, radians
import pyodbc


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
            CREATE TABLE IF NOT EXISTS cities (
                city_name TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                UNIQUE (city_name, latitude, longitude)
            );
            """)

    def get_city_coordinates(self, city):
        self._initialize()
        try:
            self.cur.execute("""
                    SELECT * FROM cities
                    WHERE city_name = ?;
                """, (city))
            return self.cur.fetchone()
        except pyodbc.Error as e:
            print("Error querying feed:", e)
            raise

    def insert_city_coordinates(self, city_name, latitude, longitude):
        self._initialize()
        try:
            self.cur.execute("""
                INSERT INTO cities (city_name, latitude, longitude)
                VALUES (?, ?, ?);
            """, (city_name, latitude, longitude))
            return self.cur.rowcount
        except pyodbc.Error as e:
            print("Error inserting city:", e)
            raise

    def close(self):
        self.conn.close()


class CitiesDistance:
    def __init__(self):
        pass

    def get_cities_distance(self):
        while True:
            city1 = input(f"Please enter the first city: ").strip()
            city2 = input(f"Please enter the second city: ").strip()

            if not city1 or not city2:
                print(f"Please enter a city.")
                continue

            db = DBConnection('final_task.db')
            latitudes = []
            longitudes = []

            for i, city in enumerate([city1, city2], 1):
                get_coordinates = db.get_city_coordinates(city)
                if get_coordinates is None:
                    latitude = float(input(f"Please enter city latitude for city {city}: "))
                    longitude = float(input(f"Please enter city longitude for city {city}: "))
                    db.insert_city_coordinates(city, latitude, longitude)
                else:
                    latitude = get_coordinates[1]
                    longitude = get_coordinates[2]

                latitudes.append(latitude)
                longitudes.append(longitude)

            db.close()
            distance = self.haversine(latitudes[0], longitudes[0], latitudes[1], longitudes[1])
            print(f"The distance between cities {city1} and {city2} is {distance:.2f} km")
            return distance

    def haversine(self, lat1, lon1, lat2, lon2):
        # convert degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        # haversine formula
        a = 6371 * 2 * asin(sqrt(
        sin((lat2 - lat1)/2)**2 +
        cos(lat1) * cos(lat2) * sin((lon2 - lon1)/2)**2
        ))
        return a


if __name__ == '__main__':
    cd = CitiesDistance()
    cities_distance = cd.get_cities_distance()

