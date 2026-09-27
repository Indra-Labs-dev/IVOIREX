"""IVOIREX V1 Ultra API: bounded product loops with persisted PostgreSQL entities."""
import os
from datetime import datetime,timedelta,timezone
import jwt
from fastapi import Depends,FastAPI,HTTPException,Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
from passlib.context import CryptContext
from pydantic import BaseModel,EmailStr,Field
from sqlalchemy import func,select
from sqlalchemy.orm import Session
from app.core.database import Base,engine,session
from app.models.domain import User,Course,Enrollment,Post,Challenge,Project,Opportunity
SECRET=os.getenv('JWT_SECRET','development-only-secret'); crypt=CryptContext(schemes=['bcrypt'],deprecated='auto'); bearer=HTTPBearer(auto_error=False)
class Register(BaseModel): email:EmailStr;username:str=Field(pattern=r'^[A-Za-z0-9_]{3,32}$');password:str=Field(min_length=8,max_length=72)
class Login(BaseModel): email:EmailStr;password:str
class Content(BaseModel): content:str=Field(min_length=1,max_length=2000)
def db_user(credentials:HTTPAuthorizationCredentials=Depends(bearer),db:Session=Depends(session)):
 if not credentials: raise HTTPException(401,'Authentication required')
 try: subject=jwt.decode(credentials.credentials,SECRET,algorithms=['HS256'])['sub']
 except jwt.PyJWTError: raise HTTPException(401,'Invalid session')
 user=db.get(User,subject)
 if not user:raise HTTPException(401,'Unknown user')
 return user
def issue(user:User):return jwt.encode({'sub':user.id,'exp':datetime.now(timezone.utc)+timedelta(days=7)},SECRET,algorithm='HS256')
def data(u:User):return {'id':u.id,'username':u.username,'email':u.email,'city':u.city,'skills':u.skills.split(',') if u.skills else [],'xp':u.xp,'level':u.xp//250+1,'streak':u.streak,'reputation':u.reputation}
app=FastAPI(title='IVOIREX V1 Ultra',version='1.0.0')
app.add_middleware(CORSMiddleware,allow_origins=os.getenv('CORS_ORIGINS','http://localhost:43100').split(','),allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
@app.on_event('startup')
def startup():
 Base.metadata.create_all(engine)
 with next(session()) as db:
  if not db.scalar(select(func.count(Course.id))):
   db.add_all([Course(title='Python pour créer à Abidjan',summary='Les fondations utiles pour automatiser, analyser et prototyper.',category='Développement',level='Débutant',xp=180),Course(title='Cybersécurité citoyenne',summary='Sécurise tes comptes et découvre les réflexes du terrain.',category='Cybersécurité',level='Débutant',xp=160),Course(title='IA appliquée aux services',summary='Du prompt au prototype responsable.',category='Intelligence artificielle',level='Intermédiaire',xp=240),Course(title='Data pour décisions locales',summary='Lire les données avant de construire.',category='Data',level='Intermédiaire',xp=220),Course(title='Entreprendre depuis la lagune',summary='Valider une idée et lancer un produit.',category='Entrepreneuriat',level='Débutant',xp=150)])
   db.add_all([Challenge(title='Signal de la lagune',prompt='2, 6, 12, 20, ? — quel est le prochain nombre ?',answer='30',xp=75),Project(title='Mobilité Cocody',description='Exemple de projet : parcours de transport communautaire.',example=True),Project(title='Lagune Watch',description='Exemple de projet : suivi participatif de la qualité de l’eau.',example=True),Opportunity(company='Orange Digital Center',title='Hackathon Climate Tech',kind='concours',location='Abidjan',description='Construis une réponse concrète aux enjeux de la ville.')]);db.commit()
@app.get('/health')
def health():return {'status':'ok'}
@app.get('/ready')
def ready(db:Session=Depends(session)):db.execute(select(1));return {'status':'ready'}
@app.post('/api/v1/auth/register',status_code=201)
def register(body:Register,db:Session=Depends(session)):
 if db.scalar(select(User).where((User.email==str(body.email).lower())|(User.username==body.username))):raise HTTPException(409,'Email or username already used')
 u=User(email=str(body.email).lower(),username=body.username,password_hash=crypt.hash(body.password));db.add(u);db.commit();db.refresh(u);return {'token':issue(u),'user':data(u)}
@app.post('/api/v1/auth/login')
def login(body:Login,db:Session=Depends(session)):
 u=db.scalar(select(User).where(User.email==str(body.email).lower()))
 if not u or not crypt.verify(body.password,u.password_hash):raise HTTPException(401,'Invalid email or password')
 return {'token':issue(u),'user':data(u)}
@app.get('/api/v1/profiles/me')
def profile(u:User=Depends(db_user)):return data(u)
@app.get('/api/v1/courses')
def courses(q:str='',db:Session=Depends(session)):return [{'id':c.id,'title':c.title,'summary':c.summary,'category':c.category,'level':c.level,'xp':c.xp} for c in db.scalars(select(Course).where(Course.title.ilike(f'%{q}%'))).all()]
@app.post('/api/v1/courses/{course_id}/enroll',status_code=201)
def enroll(course_id:str,u:User=Depends(db_user),db:Session=Depends(session)):
 if not db.get(Course,course_id):raise HTTPException(404,'Course not found')
 if db.scalar(select(Enrollment).where(Enrollment.user_id==u.id,Enrollment.course_id==course_id)):raise HTTPException(409,'Already enrolled')
 db.add(Enrollment(user_id=u.id,course_id=course_id));db.commit();return {'enrolled':True}
@app.post('/api/v1/posts',status_code=201)
def post(body:Content,u:User=Depends(db_user),db:Session=Depends(session)):db.add(Post(author_id=u.id,content=body.content));u.xp+=20;u.reputation+=1;db.commit();return {'xp':u.xp}
@app.get('/api/v1/search')
def search(q:str=Query(min_length=1),db:Session=Depends(session)):
 like=f'%{q}%';courses=db.scalars(select(Course).where(Course.title.ilike(like))).all();projects=db.scalars(select(Project).where(Project.title.ilike(like))).all();users=db.scalars(select(User).where(User.username.ilike(like))).all();return {'total':len(courses)+len(projects)+len(users),'courses':[{'id':x.id,'title':x.title}for x in courses],'projects':[{'id':x.id,'title':x.title}for x in projects],'users':[{'id':x.id,'username':x.username}for x in users]}
@app.get('/api/v1/world/activity')
def activity(db:Session=Depends(session)):return {'members':db.scalar(select(func.count(User.id))),'challenges':db.scalar(select(func.count(Challenge.id))),'courses':db.scalar(select(func.count(Course.id))),'projects':db.scalar(select(func.count(Project.id)))}
