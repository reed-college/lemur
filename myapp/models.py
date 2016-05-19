from datetime import datetime
from sqlalchemy import (Column, Integer, String,
                        DateTime, Text, ForeignKey, Enum)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum
#This file contains all the Flask-SQLAlchemy classes
Base = declarative_base()


class IdPrimaryKeyMixin(object):
    id = Column(Integer, primary_key=True)


class DateTimeMixin(object):
    created_on = Column(DateTime, default=datetime.now)
    updated_on = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# class Person(Base, IdPrimaryKeyMixin, DateTimeMixin):
#     __tablename__ = 'people'

#     first_name = Column(String(20), nullable=False)
#     last_name = Column(String(30), nullable=False)

#     def __repr__(self):
#         tpl = 'Person<id: {id}, {first_name} {last_name}>'
#         formatted = tpl.format(id=self.id, first_name=self.first_name,
#                                last_name=self.last_name)

#         return formatted


# class Food(Base, IdPrimaryKeyMixin, DateTimeMixin):
#     __tablename__ = 'food'

#     name = Column(String(50), nullable=False)
#     kind = Column(String(10))
#     description = Column(Text)

#     def __repr__(self):
#         tpl = 'Fruit<id: {id}, {name}'
#         formatted = tpl.format(id=self.id, name=self.name)
#         return formatted


# class Attitudes(enum.Enum):
#     love = 1
#     hate = 2
#     meh = 3


# class Preference(Base, IdPrimaryKeyMixin, DateTimeMixin):
#     __tablename__ = 'preferences'

#     person_id = Column(Integer, ForeignKey('people.id'))
#     food_id = Column(Integer, ForeignKey('food.id'))
#     attitude = Column('attitude',
#                       Enum('love', 'hate', 'meh', name='attitudes'))

#     person = relationship('Person', back_populates='preferences')
#     food = relationship('Food', back_populates='preferences')

#     def __repr__(self):
#         tpl = 'Preference<{person_id} feels {feel} about {food_id}>'
#         formatted = tpl.format(person_id=self.person_id, feel=self.attitude,
#                                food_id=self.food_id)

#         return formatted


# Person.preferences = relationship('Preference', order_by=Preference.id,
#                                   back_populates='person')

# Food.preferences = relationship('Preference', order_by=Preference.id,
#                                 back_populates='food')



