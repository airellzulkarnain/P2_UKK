from fastapi import APIRouter, HTTPException, Depends
from ..connection import MySQLConnection


router = APIRouter(tags=['Resepsionis'], prefix='/resepsionis')

@router.get('/')
def root(sql: MySQLConnection = Depends(MySQLConnection)):
   sql.execute('SELECT * FROM reservasi')
   result = sql.fetchall()
   sql.close()
   return result
