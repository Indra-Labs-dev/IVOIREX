import os
os.environ['DATABASE_URL']='sqlite:///./test_ivoirex.db'
os.environ['JWT_SECRET']='test-secret'
from fastapi.testclient import TestClient
from app.main import app
c=TestClient(app)
def test_core_journey():
 r=c.post('/api/v1/auth/register',json={'email':'nava@example.com','username':'nava','password':'safe_password_123'}); assert r.status_code==201
 h={'Authorization':'Bearer '+r.json()['token']}
 courses=c.get('/api/v1/courses').json(); assert courses
 cid=courses[0]['id']; assert c.post(f'/api/v1/courses/{cid}/enroll',headers=h).status_code==201
 assert c.post(f'/api/v1/courses/{cid}/complete',headers=h).json()['progress']==100
 assert c.post('/api/v1/posts',headers=h,json={'content':'Je commence mon parcours IVOIREX !'}).status_code==201
 assert c.get('/api/v1/search?q=web').status_code==200
