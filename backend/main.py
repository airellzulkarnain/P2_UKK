from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import general, admin, resepsionis
import json


CORS = dict()
with open('app/config.json','r') as file: 
   CORS = json.loads(file.read())['CORS']
app = FastAPI(title='P2_UKK', version='0.0.1')
app.add_middleware(CORSMiddleware, **CORS)
app.mount('/images', StaticFiles(directory='app/images'), name='images')
# app.include_router(admin.router)
app.include_router(general.router)
# app.include_router(resepsionis.router)
