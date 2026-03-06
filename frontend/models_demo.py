from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Base, User, Restaurant, MenuItem, Review

# Use a local SQLite DB for demo
engine = create_engine("sqlite:///frontend/demo.db", echo=False)

# create tables
Base.metadata.create_all(engine)

# insert a sample row and print
with Session(engine) as sess:
    r = Restaurant(name="Demo Diner", cuisine="International",
                   location="123 Demo St", dietary_tags="vegan", description="Demo")
    sess.add(r)
    sess.commit()

    restaurants = sess.query(Restaurant).all()
    for rest in restaurants:
        print(rest)