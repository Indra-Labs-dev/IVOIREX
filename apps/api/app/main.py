"""IVOIREX V1 API: focused, persisted core loops for learning, community and opportunity."""
import os, re, uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from fastapi import Depends, FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker, Session

DATABASE_URL=os.getenv("DATABASE_URL", "sqlite:///./ivoirex.db")
if DATABASE_URL.startswith("postgresql://"): DATABASE_URL=DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
engine=create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal=sessionmaker(bind=engine, autoflush=False)
SECRET=os.getenv("JWT_SECRET", "development-only-secret")
pwd=CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer=HTTPBearer(auto_error=False)

class Base(DeclarativeBase): pass
class User(Base):
 __tablename__="users"; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4())); email:Mapped[str]=mapped_column(String(255),unique=True,index=True); username:Mapped[str]=mapped_column(String(32),unique=True,index=True); password_hash:Mapped[str]=mapped_column(String(255)); bio:Mapped[str]=mapped_column(Text,default="Bâtisseur·se du futur ivoirien."); city:Mapped[str]=mapped_column(String(64),default="Abidjan"); skills:Mapped[str]=mapped_column(Text,default=""); xp:Mapped[int]=mapped_column(Integer,default=0); streak:Mapped[int]=mapped_column(Integer,default=1); reputation:Mapped[int]=mapped_column(Integer,default=0); role:Mapped[str]=mapped_column(String(16),default="USER"); created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc))
class Course(Base):
 __tablename__="courses"; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4())); title:Mapped[str]=mapped_column(String(160),index=True); summary:Mapped[str]=mapped_column(Text); category:Mapped[str]=mapped_column(String(40),index=True); level:Mapped[str]=mapped_column(String(24)); lessons:Mapped[int]=mapped_column(Integer); xp_reward:Mapped[int]=mapped_column(Integer,default=120)
class Enrollment(Base):
 __tablename__="enrollments"; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4())); user_id:Mapped[str]=mapped_column(ForeignKey("users.id")); course_id:Mapped[str]=mapped_column(ForeignKey("courses.id")); progress:Mapped[int]=mapped_column(Integer,default=0); completed:Mapped[bool]=mapped_column(Boolean,default=False); __table_args__=(UniqueConstraint("user_id","course_id"),)
class Post(Base):
 __tablename__="posts"; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4())); author_id:Mapped[str]=mapped_column(ForeignKey("users.id")); content:Mapped[str]=mapped_column(Text); tag:Mapped[str]=mapped_column(String(40),default="Général"); reactions:Mapped[int]=mapped_column(Integer,default=0); created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc)); author=relationship(User)
class Comment(Base):
 __tablename__="comments"; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4())); post_id:Mapped[str]=mapped_column(ForeignKey("posts.id")); author_id:Mapped[str]=mapped_column(ForeignKey("users.id")); content:Mapped[str]=mapped_column(Text); created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc)); author=relationship(User)
class Opportunity(Base):
 __tablename__="opportunities"; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4())); company:Mapped[str]=mapped_column(String(100)); title:Mapped[str]=mapped_column(String(160),index=True); kind:Mapped[str]=mapped_column(String(32)); location:Mapped[str]=mapped_column(String(80)); description:Mapped[str]=mapped_column(Text)
class Application(Base):
 __tablename__="applications"; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4())); user_id:Mapped[str]=mapped_column(ForeignKey("users.id")); opportunity_id:Mapped[str]=mapped_column(ForeignKey("opportunities.id")); message:Mapped[str]=mapped_column(Text); status:Mapped[str]=mapped_column(String(20),default="submitted"); __table_args__=(UniqueConstraint("user_id","opportunity_id"),)
class Challenge(Base):
 __tablename__="challenges"; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4())); title:Mapped[str]=mapped_column(String(160)); category:Mapped[str]=mapped_column(String(40)); difficulty:Mapped[str]=mapped_column(String(24)); prompt:Mapped[str]=mapped_column(Text); answer:Mapped[str]=mapped_column(String(120)); xp_reward:Mapped[int]=mapped_column(Integer)
class Submission(Base):
 __tablename__="submissions"; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4())); user_id:Mapped[str]=mapped_column(ForeignKey("users.id")); challenge_id:Mapped[str]=mapped_column(ForeignKey("challenges.id")); correct:Mapped[bool]=mapped_column(Boolean); __table_args__=(UniqueConstraint("user_id","challenge_id"),)
class Project(Base):
 __tablename__="projects"; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4())); user_id:Mapped[str]=mapped_column(ForeignKey("users.id")); title:Mapped[str]=mapped_column(String(120)); description:Mapped[str]=mapped_column(Text); technologies:Mapped[str]=mapped_column(String(200),default="")
class Event(Base):
 __tablename__="events"; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4())); title:Mapped[str]=mapped_column(String(160)); event_at:Mapped[datetime]=mapped_column(DateTime(timezone=True)); format:Mapped[str]=mapped_column(String(32)); seats:Mapped[int]=mapped_column(Integer)
class Registration(Base):
 __tablename__="registrations"; id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4())); user_id:Mapped[str]=mapped_column(ForeignKey("users.id")); event_id:Mapped[str]=mapped_column(ForeignKey("events.id")); __table_args__=(UniqueConstraint("user_id","event_id"),)

class Register(BaseModel): email:EmailStr; username:str=Field(pattern=r"^[a-zA-Z0-9_]{3,32}$"); password:str=Field(min_length=8,max_length=72)
class Login(BaseModel): email:EmailStr; password:str
class ProfilePatch(BaseModel): bio:Optional[str]=Field(None,max_length=500); city:Optional[str]=Field(None,max_length=64); skills:Optional[list[str]]=None
class TextIn(BaseModel): content:str=Field(min_length=1,max_length=2000); tag:str="Général"
class ApplyIn(BaseModel): message:str=Field(min_length=20,max_length=1500)
class ProjectIn(BaseModel): title:str=Field(min_length=3,max_length=120); description:str=Field(min_length=10,max_length=1500); technologies:list[str]=[]
class AnswerIn(BaseModel): answer:str=Field(min_length=1,max_length=120)

def db():
 s=SessionLocal()
 try: yield s
 finally: s.close()
def token(user): return jwt.encode({"sub":user.id,"role":user.role,"exp":datetime.now(timezone.utc)+timedelta(days=7)},SECRET,algorithm="HS256")
def me(credentials:HTTPAuthorizationCredentials=Depends(bearer), s:Session=Depends(db)):
 if not credentials: raise HTTPException(401,"Authentication required")
 try: payload=jwt.decode(credentials.credentials,SECRET,algorithms=["HS256"])
 except jwt.PyJWTError: raise HTTPException(401,"Invalid session")
 user=s.get(User,payload["sub"])
 if not user: raise HTTPException(401,"Unknown user")
 return user
def serialize_user(u): return {"id":u.id,"email":u.email,"username":u.username,"bio":u.bio,"city":u.city,"skills":[x for x in u.skills.split(",") if x],"xp":u.xp,"level":max(1,u.xp//250+1),"streak":u.streak,"reputation":u.reputation,"role":u.role}
def gain(s,u,amount): u.xp+=amount; u.reputation+=max(1,amount//20)

app=FastAPI(title="IVOIREX API",version="1.0.0")
app.add_middleware(CORSMiddleware,allow_origins=os.getenv("CORS_ORIGINS","http://localhost:43100").split(","),allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
@app.on_event("startup")
def start():
 Base.metadata.create_all(engine)
 with SessionLocal() as s:
  if not s.scalar(select(func.count(Course.id))):
   s.add_all([Course(title="Fondations du web moderne",summary="HTML, CSS et JavaScript pour lancer ton premier produit.",category="Développement",level="Débutant",lessons=6,xp_reward=180),Course(title="Data & IA pratique",summary="Comprendre les données et prototyper avec l'IA.",category="IA",level="Intermédiaire",lessons=5,xp_reward=240),Course(title="Cybersécurité citoyenne",summary="Protéger les comptes, réseaux et projets.",category="Cybersécurité",level="Débutant",lessons=4,xp_reward=160)])
   s.add_all([Opportunity(company="Djamo",title="Stage Product Design",kind="stage",location="Abidjan · Hybride",description="Conçois des expériences financières accessibles."),Opportunity(company="Julaya",title="Junior Backend Engineer",kind="emploi",location="Abidjan",description="Construis des APIs de paiement fiables."),Opportunity(company="Orange Digital Center",title="Hackathon Climate Tech",kind="concours",location="Abidjan",description="Propose une solution utile pour la ville.")])
   s.add_all([Challenge(title="Décode le signal",category="Logique",difficulty="Débutant",prompt="Quel est le prochain nombre : 2, 6, 12, 20, ?",answer="30",xp_reward=75),Challenge(title="Sécurité express",category="Cybersécurité",difficulty="Débutant",prompt="Quelle pratique protège le mieux un mot de passe ? Réponds par un mot.",answer="gestionnaire",xp_reward=90),Challenge(title="Prompt responsable",category="IA",difficulty="Intermédiaire",prompt="Quel mot indique que l'on doit vérifier les résultats d'une IA : ?",answer="sources",xp_reward=100)])
   s.add(Event(title="Build Night — Abidjan",event_at=datetime.now(timezone.utc)+timedelta(days=12),format="Meetup",seats=80)); s.commit()
@app.get("/health")
def health(): return {"status":"ok","service":"ivoirex-api"}
@app.get("/ready")
def ready(s:Session=Depends(db)): s.execute(select(1)); return {"status":"ready"}
@app.post("/api/v1/auth/register",status_code=201)
def register(body:Register,s:Session=Depends(db)):
 if s.scalar(select(User).where((User.email==body.email)|(User.username==body.username))): raise HTTPException(409,"Email or username already used")
 u=User(email=str(body.email).lower(),username=body.username,password_hash=pwd.hash(body.password)); s.add(u);s.commit();s.refresh(u);return {"token":token(u),"user":serialize_user(u)}
@app.post("/api/v1/auth/login")
def login(body:Login,s:Session=Depends(db)):
 u=s.scalar(select(User).where(User.email==str(body.email).lower()))
 if not u or not pwd.verify(body.password,u.password_hash): raise HTTPException(401,"Invalid email or password")
 return {"token":token(u),"user":serialize_user(u)}
@app.get("/api/v1/profiles/me")
def profile(u:User=Depends(me)): return serialize_user(u)
@app.patch("/api/v1/profiles/me")
def edit_profile(body:ProfilePatch,u:User=Depends(me),s:Session=Depends(db)):
 for k,v in body.model_dump(exclude_none=True).items(): setattr(u,k,",".join(v) if k=="skills" else v)
 s.commit();return serialize_user(u)
@app.get("/api/v1/courses")
def courses(q:str="",s:Session=Depends(db)): return [{"id":c.id,"title":c.title,"summary":c.summary,"category":c.category,"level":c.level,"lessons":c.lessons,"xp":c.xp_reward} for c in s.scalars(select(Course).where(Course.title.ilike(f"%{q}%"))).all()]
@app.post("/api/v1/courses/{course_id}/enroll",status_code=201)
def enroll(course_id:str,u:User=Depends(me),s:Session=Depends(db)):
 if not s.get(Course,course_id): raise HTTPException(404,"Course not found")
 if s.scalar(select(Enrollment).where(Enrollment.user_id==u.id,Enrollment.course_id==course_id)): raise HTTPException(409,"Already enrolled")
 e=Enrollment(user_id=u.id,course_id=course_id);s.add(e);s.commit();return {"id":e.id,"progress":0}
@app.post("/api/v1/courses/{course_id}/complete")
def complete(course_id:str,u:User=Depends(me),s:Session=Depends(db)):
 e=s.scalar(select(Enrollment).where(Enrollment.user_id==u.id,Enrollment.course_id==course_id));c=s.get(Course,course_id)
 if not e or not c: raise HTTPException(404,"Enrollment not found")
 if not e.completed: e.progress=100;e.completed=True;gain(s,u,c.xp_reward);s.commit()
 return {"progress":100,"xp":u.xp,"certificate":f"IVO-{course_id[:8]}"}
@app.get("/api/v1/posts")
def posts(s:Session=Depends(db)): return [{"id":p.id,"content":p.content,"tag":p.tag,"reactions":p.reactions,"author":p.author.username,"created_at":p.created_at} for p in s.scalars(select(Post).order_by(Post.created_at.desc())).all()]
@app.post("/api/v1/posts",status_code=201)
def create_post(body:TextIn,u:User=Depends(me),s:Session=Depends(db)): p=Post(author_id=u.id,content=body.content,tag=body.tag);s.add(p);gain(s,u,20);s.commit();return {"id":p.id,"xp":u.xp}
@app.post("/api/v1/posts/{post_id}/comments",status_code=201)
def comment(post_id:str,body:TextIn,u:User=Depends(me),s:Session=Depends(db)):
 if not s.get(Post,post_id):raise HTTPException(404,"Post not found")
 c=Comment(post_id=post_id,author_id=u.id,content=body.content);s.add(c);gain(s,u,5);s.commit();return {"id":c.id}
@app.post("/api/v1/posts/{post_id}/react")
def react(post_id:str,s:Session=Depends(db)):
 p=s.get(Post,post_id)
 if not p:raise HTTPException(404,"Post not found")
 p.reactions+=1;s.commit();return {"reactions":p.reactions}
@app.get("/api/v1/opportunities")
def opportunities(q:str="",kind:str="",s:Session=Depends(db)):
 stmt=select(Opportunity).where(Opportunity.title.ilike(f"%{q}%"));
 if kind: stmt=stmt.where(Opportunity.kind==kind)
 return [{"id":x.id,"company":x.company,"title":x.title,"kind":x.kind,"location":x.location,"description":x.description} for x in s.scalars(stmt).all()]
@app.post("/api/v1/opportunities/{oid}/apply",status_code=201)
def apply(oid:str,body:ApplyIn,u:User=Depends(me),s:Session=Depends(db)):
 if not s.get(Opportunity,oid):raise HTTPException(404,"Opportunity not found")
 if s.scalar(select(Application).where(Application.user_id==u.id,Application.opportunity_id==oid)):raise HTTPException(409,"Already applied")
 a=Application(user_id=u.id,opportunity_id=oid,message=body.message);s.add(a);gain(s,u,30);s.commit();return {"status":a.status}
@app.get("/api/v1/challenges")
def challenges(s:Session=Depends(db)): return [{"id":x.id,"title":x.title,"category":x.category,"difficulty":x.difficulty,"prompt":x.prompt,"xp":x.xp_reward} for x in s.scalars(select(Challenge)).all()]
@app.post("/api/v1/challenges/{cid}/submit")
def submit(cid:str,body:AnswerIn,u:User=Depends(me),s:Session=Depends(db)):
 c=s.get(Challenge,cid)
 if not c:raise HTTPException(404,"Challenge not found")
 if s.scalar(select(Submission).where(Submission.user_id==u.id,Submission.challenge_id==cid)):raise HTTPException(409,"Already submitted")
 correct=body.answer.strip().lower()==c.answer.lower();s.add(Submission(user_id=u.id,challenge_id=cid,correct=correct));
 if correct:gain(s,u,c.xp_reward)
 s.commit();return {"correct":correct,"xp_awarded":c.xp_reward if correct else 0}
@app.get("/api/v1/projects")
def projects(s:Session=Depends(db)): return [{"id":p.id,"title":p.title,"description":p.description,"technologies":p.technologies.split(","),"author":s.get(User,p.user_id).username} for p in s.scalars(select(Project)).all()]
@app.post("/api/v1/projects",status_code=201)
def create_project(body:ProjectIn,u:User=Depends(me),s:Session=Depends(db)): p=Project(user_id=u.id,title=body.title,description=body.description,technologies=",".join(body.technologies));s.add(p);gain(s,u,60);s.commit();return {"id":p.id,"xp":u.xp}
@app.get("/api/v1/events")
def events(s:Session=Depends(db)): return [{"id":e.id,"title":e.title,"date":e.event_at,"format":e.format,"seats":e.seats} for e in s.scalars(select(Event)).all()]
@app.post("/api/v1/events/{eid}/register",status_code=201)
def event_register(eid:str,u:User=Depends(me),s:Session=Depends(db)):
 if not s.get(Event,eid):raise HTTPException(404,"Event not found")
 if s.scalar(select(Registration).where(Registration.user_id==u.id,Registration.event_id==eid)):raise HTTPException(409,"Already registered")
 s.add(Registration(user_id=u.id,event_id=eid));gain(s,u,25);s.commit();return {"registered":True}
@app.get("/api/v1/search")
def search(q:str=Query(min_length=1),s:Session=Depends(db)):
 q=f"%{q}%";return {"courses":[{"id":x.id,"title":x.title} for x in s.scalars(select(Course).where(Course.title.ilike(q))).all()],"opportunities":[{"id":x.id,"title":x.title} for x in s.scalars(select(Opportunity).where(Opportunity.title.ilike(q))).all()],"users":[{"id":x.id,"username":x.username} for x in s.scalars(select(User).where(User.username.ilike(q))).all()]}
@app.post("/api/v1/ai/chat")
def ai_chat(body:TextIn,u:User=Depends(me),s:Session=Depends(db)):
 courses=s.scalars(select(Course).limit(2)).all(); return {"provider":"rules-v1","message":f"{u.username}, je te recommande {courses[0].title} puis un projet concret. Tes compétences actuelles : {u.skills or 'à définir'}."}
