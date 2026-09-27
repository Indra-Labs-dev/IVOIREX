import uuid
from datetime import datetime,timezone
from sqlalchemy import String,Integer,Text,Boolean,DateTime,ForeignKey,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.core.database import Base
def uid(): return str(uuid.uuid4())
def now(): return datetime.now(timezone.utc)
class User(Base):
 __tablename__='users';id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid);email:Mapped[str]=mapped_column(String(255),unique=True,index=True);username:Mapped[str]=mapped_column(String(32),unique=True,index=True);password_hash:Mapped[str]=mapped_column(String(255));city:Mapped[str]=mapped_column(String(60),default='Abidjan');skills:Mapped[str]=mapped_column(Text,default='');xp:Mapped[int]=mapped_column(Integer,default=0);reputation:Mapped[int]=mapped_column(Integer,default=0);streak:Mapped[int]=mapped_column(Integer,default=1);created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class Course(Base):
 __tablename__='courses';id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid);title:Mapped[str]=mapped_column(String(150),index=True);summary:Mapped[str]=mapped_column(Text);category:Mapped[str]=mapped_column(String(50),index=True);level:Mapped[str]=mapped_column(String(30));xp:Mapped[int]=mapped_column(Integer)
class Enrollment(Base):
 __tablename__='enrollments';id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid);user_id:Mapped[str]=mapped_column(ForeignKey('users.id'));course_id:Mapped[str]=mapped_column(ForeignKey('courses.id'));progress:Mapped[int]=mapped_column(Integer,default=0);completed:Mapped[bool]=mapped_column(Boolean,default=False);__table_args__=(UniqueConstraint('user_id','course_id'),)
class Post(Base):
 __tablename__='posts';id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid);author_id:Mapped[str]=mapped_column(ForeignKey('users.id'));content:Mapped[str]=mapped_column(Text);created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now);author=relationship(User)
class Challenge(Base):
 __tablename__='challenges';id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid);title:Mapped[str]=mapped_column(String(150));prompt:Mapped[str]=mapped_column(Text);answer:Mapped[str]=mapped_column(String(120));xp:Mapped[int]=mapped_column(Integer)
class Project(Base):
 __tablename__='projects';id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid);title:Mapped[str]=mapped_column(String(150));description:Mapped[str]=mapped_column(Text);example:Mapped[bool]=mapped_column(Boolean,default=False)
class Opportunity(Base):
 __tablename__='opportunities';id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid);company:Mapped[str]=mapped_column(String(120));title:Mapped[str]=mapped_column(String(150),index=True);kind:Mapped[str]=mapped_column(String(30));location:Mapped[str]=mapped_column(String(80));description:Mapped[str]=mapped_column(Text)
