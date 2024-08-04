from __init__ import CURSOR, CONN
from employee import Employee

class Review:
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if not isinstance(value, int) or value < 2000:
            raise ValueError("Year must be an integer greater than or equal to 2000.")
        self._year = value

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Summary must be a non-empty string.")
        self._summary = value

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        sql = "SELECT id FROM employees WHERE id = ?"
        result = CURSOR.execute(sql, (value,)).fetchone()
        if result is None:
            raise ValueError("Employee ID must be a valid ID from the employees table.")
        self._employee_id = value

    @classmethod
    def create_table(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employees(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        if self.id is None:
            sql = """
                INSERT INTO reviews (year, summary, employee_id)
                VALUES (?, ?, ?)
            """
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
            self.id = CURSOR.lastrowid
        else:
            sql = """
                UPDATE reviews
                SET year = ?, summary = ?, employee_id = ?
                WHERE id = ?
            """
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))

        CONN.commit()
        Review.all[self.id] = self

    @classmethod
    def create(cls, year, summary, employee_id):
        review = cls(year=year, summary=summary, employee_id=employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, db_row):
        review_id, year, summary, employee_id = db_row

        # Check if the instance is already cached
        if review_id in cls.all:
            review = cls.all[review_id]
            review.year = year
            review.summary = summary
            review.employee_id = employee_id
        else:
            review = cls(year=year, summary=summary, employee_id=employee_id, id=review_id)
            cls.all[review_id] = review

        return review

    @classmethod
    def find_by_id(cls, id):
            """Return a Review instance having the attribute values from the table row."""
            sql = """
                SELECT * FROM reviews
                WHERE id = ?
                LIMIT 1
                """
            row = CURSOR.execute(sql, (id,)).fetchone()
            return cls.instance_from_db(row) if row else None


    def update(self):
        self.save()

    def delete(self):
        if self.id:
            sql = """
                DELETE FROM reviews WHERE id = ?
            """
            CURSOR.execute(sql, (self.id,))
            CONN.commit()

            if self.id in Review.all:
                del Review.all[self.id]
            self.id = None

    @classmethod
    def get_all(cls):
        sql = """
            SELECT * FROM reviews
        """
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]
