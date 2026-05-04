class GenreCreateDTO:
    def __init__(self, name):
        self.name = name


class GenreUpdateDTO:
    def __init__(self, name):
        self.name = name


class MovieCreateDTO:
    def __init__(
        self, title, summary, release_year, duration_minutes, age_limit, genre_ids=()):
        self.title = title
        self.summary = summary
        self.release_year = release_year
        self.duration_minutes = duration_minutes
        self.age_limit = age_limit
        self.genre_ids = genre_ids


class MovieUpdateDTO:
    def __init__(self):
        self.title = None
        self.summary = None
        self.release_year = None
        self.duration_minutes = None
        self.age_limit = None
        self.genre_ids = None
