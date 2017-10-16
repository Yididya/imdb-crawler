from sqlalchemy import *
from settings import DATABASE

class Repository:
    def __init__(self, showLog = False):
        """
        Initialize database structure
        """

        self.__showLog = showLog
        self.__engine = create_engine('mysql+pymysql://' + DATABASE['USER'] + ':' + DATABASE['PASSWORD'] + '@localhost:' + DATABASE['PORT'] + '/MovieDB?charset=utf8mb4', echo=self.__showLog, pool_size=20, pool_recycle=3600)
        self.__metadata = MetaData()

        self.__persons = Table('person', self.__metadata,
            Column('id', Integer, primary_key = True),
            Column('name', String(255), nullable = False, unique = True)
        )

        self.__movies = Table('movie', self.__metadata,
            Column('id', Integer, primary_key = True),
            Column('title', String(255), nullable = False, unique = True),
            Column('imdb_link', String(255), nullable = False, unique = True),
            Column('release_date', Date, nullable = True),
            Column('rating', Float, nullable = True),
            Column('synopsis', Text, nullable = True),
            Column('running_time', String(10), nullable=True),
            Column('budget', String(20), nullable=True),
            Column('gross_usa', String(20), nullable=True),
            Column('gross_worldwide', String(20), nullable=True),
            Column('genre', String(50), nullable=True)
        )
        self.__actors = Table('actor', self.__metadata, 
            Column('id', Integer, primary_key = True, autoincrement=True),
            Column('person_id', Integer, primary_key = True),
            Column('name', String(255), nullable=False, unique=True),
            Column('imdb_link', String(255), nullable=False, unique=True),
            Column('roles', String(255), nullable=True),
            Column('mini_bio', Text, nullable=True),
            Column('birth_date', Date, nullable=True),
            Column('birth_place', String(255), nullable=True),
            Column('known_for', Text, nullable=True),
            Column('height', Float, nullable=True)
        )
        self.__actor_characters = Table('actor_character', self.__metadata,
            Column('id', Integer, primary_key = True),
            Column('actor_id', None, ForeignKey('actor.id')),
            Column('movie_id', None, ForeignKey('movie.id')),
            Column('character_name', String(255), nullable = True)
        )

        self.__directors = Table('director', self.__metadata,
            Column('id', Integer, primary_key = True),
            Column('person_id', None, ForeignKey('person.id')),
            Column('movie_id', None, ForeignKey('movie.id'))
        )

        self.__reviews = Table('review', self.__metadata,
            Column('id', Integer, primary_key=True),
            Column('movie_id', None, ForeignKey('movie.id')),
            Column('review_title', String(300, collation='utf8mb4_unicode_ci'), nullable=True),
            Column('review_detail', Text(collation='utf8mb4_unicode_ci'), nullable=True),
        )

    def create_schema(self):
        """
        Create schema in database.
        """
        self.__metadata.drop_all(self.__engine)
        self.__metadata.create_all(self.__engine)
    def create_schema_if_none(self):
        if not self.__engine.dialect.has_table(self.__engine, 'movie'):
            self.create_schema()
    # Person methods
    def get_person_id(self, name):
        result = self.__engine.connect().execute(
            select([self.__persons.c.id],
                and_(self.__persons.c.name == name)
            )
        )

        first_row = result.fetchone()

        if first_row == None:
            return None
        else:
            return first_row[0]

    def save_person(self, name):
        result = self.__engine.connect().execute(
            self.__persons.insert()
            .values(name = name)
        )

        return result.inserted_primary_key[0]

#    def updatePerson(self, id, name):
#        conn = self.__engine.connect()
#
#        conn.execute(
#            self.__persons.update().
#            where(self.__persons.c.Id == id).
#            values(Name = name)
#        )

    def save_person_if_none(self, name):
        person_id = self.get_person_id(name)

        if person_id == None:
            return self.save_person(name)
        else:
            return person_id

    # Movie methods
    def get_movie_id(self, title):
        result = self.__engine.connect().execute(
            select([self.__movies.c.id],
                and_(self.__movies.c.title == title)
            )
        )

        first_row = result.fetchone()

        if first_row == None:
            return None
        else:
            return first_row[0]

    def insert_movie(self, movie):
        result = self.__engine.connect().execute(
            self.__movies.insert()
            .values(title = movie.title,
                    imdb_link = movie.imdb_link,
                    genre = ', '.join(movie.genre),
                    release_date = movie.release_date,
                    rating = movie.rating,
                    running_time = movie.running_time,
                    budget = movie.budget,
                    gross_usa = movie.gross_usa,
                    gross_worldwide = movie.gross_worldwide,
                    synopsis = movie.synopsis)
        )

        return result.inserted_primary_key[0]
    
    def insert_actor(self, actor):
        person_id = self.save_person_if_none(actor.name)
        result = self.__engine.connect().execute(
            self.__actors.insert()
            .values(imdb_link = actor.imdb_link,
                    person_id = person_id,
                    name = actor.name,
                    roles = ', '.join(actor.roles),
                    mini_bio = actor.mini_bio,
                    birth_date = actor.birth_date,
                    birth_place = actor.birth_place,
                    known_for = actor.known_for)
        )

        return result.inserted_primary_key[0], person_id

    def save_movie(self, movie):
        movie_id = self.get_movie_id(movie.title)

        if movie_id == None:
            movie_id = self.insert_movie(movie)
        else:
            return

        for director_name in movie.directors:
            self.save_director(movie_id, director_name)

        for cast in movie.actor_character_pairs:
            actor_id, _ = self.get_or_create_actor(cast['actor'])
            self.save_actor_character(movie_id, actor_id, cast['character'])
        
        for review in movie.reviews:
            self.save_review(movie_id, review)

    # Director methods
    def save_director(self, movie_id, director_name):
        person_id = self.save_person_if_none(director_name)
        result = self.__engine.connect().execute(
            self.__directors.insert()
            .values(movie_id = movie_id, person_id = person_id)
        )

        return result.inserted_primary_key[0]
    
    def get_or_create_actor(self, actor):
        result = self.__engine.connect().execute(
            select([self.__actors.c.id, self.__actors.c.person_id],
                and_(self.__actors.c.name == actor.name)
            )
        )

        first_row = result.fetchone()

        if first_row == None:
            return self.insert_actor(actor)
        else:
            return first_row[0], first_row[1] # actors_id, # person_id

    def save_actor_character(self, movie_id, actor_id, character_name):

        result = self.__engine.connect().execute(
            self.__actor_characters.insert()
            .values(movie_id = movie_id, actor_id = actor_id, character_name = character_name)
        )

        return result.inserted_primary_key[0]

    def save_review(self, movie_id, review):
        result = self.__engine.connect().execute(
            self.__reviews.insert()
            .values(movie_id=movie_id, review_title=review['title'], review_detail=review['detail'])
        )

        return result.inserted_primary_key[0]

    
    def get_num_movies(self):
        result =  self.__engine.execute(
            select([func.count('id')]).select_from(self.__movies)
        )
        
        return result.fetchone()[0]