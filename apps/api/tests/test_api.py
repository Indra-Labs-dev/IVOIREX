import os
os.environ['DATABASE_URL']='sqlite:///./test_ivoirex.db';os.environ['JWT_SECRET']='test-secret'
from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
def test_auth_learning_and_search():
 response=client.post('/api/v1/auth/register',json={'email':'aya@example.com','username':'aya_ci','password':'safe-password-123'})
 assert response.status_code==201
 token=response.json()['token'];headers={'Authorization':f'Bearer {token}'}
 assert client.get('/api/v1/profiles/me',headers=headers).status_code==200
 courses=client.get('/api/v1/courses').json();assert len(courses)>=5
 assert client.post(f"/api/v1/courses/{courses[0]['id']}/enroll",headers=headers).status_code==201
 assert client.post('/api/v1/posts',headers=headers,json={'content':'Je construis mon premier projet.'}).status_code==201
 assert client.get('/api/v1/search?q=Python').json()['total']>=1
