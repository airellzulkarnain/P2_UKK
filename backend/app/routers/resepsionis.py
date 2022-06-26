from fastapi import APIRouter, HTTPException, Depends, Request
from ..connection import MySQLConnection


router = APIRouter(tags=['Resepsionis'], prefix='/resepsionis')


@router.get('/reservasi')
def retrive_data(req: Request, cursor: MySQLConnection = Depends(MySQLConnection)):
   pass


@router.put('/update_status/{id_reservasi}')
def update_status(id_reservasi: int, cursor: MySQLConnection = Depends(MySQLConnection)):
   pass

