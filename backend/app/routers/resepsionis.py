from fastapi import APIRouter, HTTPException, Depends, Request
from ..connection import MySQLConnection


router = APIRouter(tags=['Resepsionis'], prefix='/resepsionis')


@router.get('/reservasi')
def retrive_data(req: Request, cursor: MySQLConnection = Depends(MySQLConnection)):
   pass


@router.put('/update_status/{id_reservasi}')
def update_status(id_reservasi: int, cursor: MySQLConnection = Depends(MySQLConnection)):
   cursor.execute('''SELECT status.nama_status FROM status 
                     WHERE status.id_status = (SELECT id_status 
                     FROM reservasi WHERE id_reservasi = %s) LIMIT 1''', (id_reservasi, ))
   status = cursor.fetchone()['nama_status']

   if status == 'BOOKED' or status == 'CHECKED_IN':
      cursor.execute('UPDATE reservasi SET id_status=((SELECT id_status FROM status WHERE nama_status = %s)+1) WHERE id_reservasi=%s', 
      (status, id_reservasi))
      cursor.commit()
      cursor.close()
      return {"message": "STATUS UPDATED", "last_status": status}

   else: 
      return {"message": "STATUS UPDATE FAILED", "last_status":status}

