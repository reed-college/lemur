from datetime import datetime
from sqlalchemy import (Column, Integer, String, DateTime, Text, ForeignKey, Enum)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum
# Notes: if the schema is changed, you need to change __tablename__ to create a
# new schema and clear the old one

Base = declarative_base()


class IdPrimaryKeyMixin(object):
    id = Column(String(128), primary_key=True)


class DateTimeMixin(object):
    created_on = Column(DateTime, default=datetime.now)
    updated_on = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# Store general info of a lab
class Lab_info(Base):
    __tablename__ = 'Lab_info'
    lab_id = Column(String(128), nullable=False, unique=True, primary_key=True)
    lab_name = Column(String(128), nullable=False)
    class_name = Column(String(128), nullable=False)
    prof_name = Column(String(128), nullable=False)
    lab_desc = Column(String(2048))
    lab_status = Column(Enum('Activated', 'Downloaded', 'Unactivated',
                             name='lab_status'))

    # one-to-many: a lab can have multiple rows
    lab_rows = relationship('Lab_rows', back_populates='lab',
                            cascade="all, delete, delete-orphan")

    def __repr__(self):
        tpl = 'Lab_info<lab_id: {lab_id}, lab_name: {lab_name}, class_name: {class_name}, prof_name: {prof_name}, lab_desc: {lab_desc}, lab_status: {lab_status}>'
        formatted = tpl.format(lab_id=self.lab_id, lab_name=self.lab_name,
                               class_name=self.class_name,
                               prof_name=self.prof_name,
                               lab_desc=self.lab_desc,
                               lab_status=self.lab_status)
        return formatted


# Store rows' info of a lab
class Lab_rows(Base):
    __tablename__ = 'Lab_rows'
    row_id = Column(String(128), nullable=False, unique=True, primary_key=True)
    row_name = Column(String(512), nullable=False)
    row_desc = Column(String(512))
    row_order = Column(Integer, nullable=False)
    value_type = Column(Enum('Number', 'Text', name='value_type'))
    value_range = Column(String(64))
    value_candidates = Column(String(512))

    lab_id = Column(String(128), ForeignKey('Lab_info.lab_id'))
    lab = relationship("Lab_info", back_populates="lab_rows")

    # one-to-many: a row can have multiple data
    row_datas = relationship('Lab_data', back_populates='row',
                             cascade="all, delete, delete-orphan")

    def __repr__(self):
        return 'Lab_rows<'+'lab_id: '+self.lab_id+'row_id: '+self.row_id+', row_name: '+self.row_name+'>'


# Store data entered by students
class Lab_data(Base, DateTimeMixin):
    __tablename__ = 'Lab_data'
    data_id = Column(String(128), nullable=False, unique=True,
                     primary_key=True)
    student_name = Column(String(256), nullable=False)
    row_data = Column(String(512), nullable=False)

    row_id = Column(String(128), ForeignKey('Lab_rows.row_id'))
    row = relationship("Lab_rows", back_populates="row_datas")

    def __repr__(self):
        tpl = 'Lab_data<row_id: {row_id}, data_id: {data_id}, row_data: {row_data}>'
        formatted = tpl.format(row_id=self.row_id, data_id=self.data_id,
                               row_data=self.row_data)
        return formatted
