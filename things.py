import sqlalchemy

from sqlalchemy import create_engine

engine = create_engine('sqlite:///:memory:', echo=True)

# create a declaratice base class
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# define a class representing a User table
from sqlalchemy import Column, Integer, String
class User(Base):
    # at least a __tablename__ and a primary key are required
    __tablename__ = 'users'
    # Firebird and Oracle require sequences to generate new primary keys
    from sqlalchemy import Sequence
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    # otherwise:
    #id = Column(Integer, primary_key=True)
    name = Column(String(50))
    fullname = Column(String(50))
    password = Column(String(50))

    def __repr__(self):
        return f"<User(id='{self.id}', " \
               f"name='{self.name}', " \
               f"fullname='{self.fullname}', " \
               f"password='{self.password}'>"

# print table metadata?
print(User.__table__)

# create the table
Base.metadata.create_all(engine)

# Create a User object
# note the user isn't actually being added to the DB at this point
# thus the id is None
ed_user = User(name='ed', fullname='Ed Jones', password='edspassword')
print(f"password = {ed_user.password}")
print(f"id = {str(ed_user.id)}")

# create an actual session with the database
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

# add the user to the session
session.add(ed_user)
# add does not immediately create the row
# you need to query to trigger a flush, or do an explicit commit()

our_user = session.query(User).filter_by(name='ed').first()
print(f"our_user = {our_user}")

# add several User objects
session.add_all([
    User(name='eric', fullname='Eric Davis', password='asdasd'),
    User(name='colin', fullname='Colin Davis', password='qweqwe'),
    User(name='jenn', fullname='Jennifer Davis', password='zxczxc')])

# change a password
ed_user.password = 'dfgdfg'

# Session sees the data yet to be changed
print(f'Dirty! {session.dirty}')

# And the data to be added:
print(f'New! {session.new}')

session.commit()

# print the users
our_users = session.query(User)
print(type(our_users))
for user in our_users:
    print(user)

# an alternative
for user in session.query(User).order_by(User.name):
    print(user.id, user.fullname)

# or
for name, fullname in session.query(User.name, User.fullname):
    print(name, fullname)