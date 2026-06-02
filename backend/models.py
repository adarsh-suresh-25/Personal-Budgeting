from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

# USER TABLE
class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String)

    email = Column(String, unique=True)

    password = Column(String)

# EXPENSE TABLE
class Expense(Base):

    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)

    amount = Column(Integer)

    category = Column(String)

    description = Column(String)

    user_id = Column(Integer, ForeignKey("users.id"))