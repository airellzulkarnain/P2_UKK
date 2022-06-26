from fastapi import APIRouter, Body, HTTPException, Depends
from fastapi.responses import FileResponse, StreamingResponse
from ..connection import MySQLConnection
from ..models.reservation import reservation
from datetime import date
from fpdf import FPDF, HTMLMixin
from io import BytesIO
from mysql.connector.errors import DatabaseError
# Bagian ini merupakan endpoint untuk mengambil konten dan menampilkannya ke user tanpa akun atau umum. 
# Terdiri dari bagian fasilitas dan kamar yang harus diambil dan tampilkan
class PDF(FPDF, HTMLMixin):
   pass


router = APIRouter(prefix="/general", tags=['General'])
@router.get("/kamar")
def kamar(cursor: MySQLConnection = Depends(MySQLConnection)):
   cursor.execute("""SELECT kamar.id_kamar, kamar.gambar_kamar, tipe_kamar.nama_tipe_kamar, fasilitas_kamar.nama_fasilitas_kamar FROM 
                     (kamar INNER JOIN fasilitas_kamar ON kamar.id_kamar = fasilitas_kamar.id_kamar) 
                     INNER JOIN tipe_kamar ON kamar.id_tipe_kamar = tipe_kamar.id_tipe_kamar""")
   raw_data = cursor.fetchall()
   processed_data = list()
   count = 0
   temp_id = ''
   for data in raw_data:
      if data['id_kamar'] == temp_id:
         processed_data[count]['fasilitas_kamar'].append(data['nama_fasilitas_kamar'])
      else:
         processed_data.append({'gambar_kamar': data['gambar_kamar'], 'tipe_kamar': data['nama_tipe_kamar'], 
                                            'fasilitas_kamar': [data['nama_fasilitas_kamar']]})
         count = len(processed_data)-1
         temp_id = data['id_kamar']
   cursor.close()
   return processed_data


@router.get("/fasilitas")
def fasilitas(cursor: MySQLConnection = Depends(MySQLConnection)):
   cursor.execute('SELECT nama_fasilitas_hotel, keterangan_fasilitas_hotel, gambar_fasilitas_hotel FROM fasilitas_hotel')
   data = cursor.fetchall()
   cursor.close()
   return data


@router.post("/reservasi")
def reservasi(reservasi: reservation | None = Body(None, embed=True), cursor: MySQLConnection = Depends(MySQLConnection)):
   cursor.execute("""SELECT ((SELECT jumlah_kamar FROM kamar WHERE kamar.id_tipe_kamar = %s) - COALESCE((SELECT SUM(reservasi.jumlah_kamar) 
                     FROM reservasi INNER JOIN kamar ON reservasi.id_kamar = kamar.id_kamar WHERE kamar.id_tipe_kamar = %s 
                     AND reservasi.tanggal_check_out >= %s), 0)) AS kamar_tersedia""", 
                     (reservasi.id_tipe_kamar, reservasi.id_tipe_kamar, reservasi.tanggal_check_in))
   kamar_tersedia = cursor.fetchall()[0]['kamar_tersedia']

   if kamar_tersedia >= reservasi.jumlah_kamar: 
      try: 
         cursor.execute("""INSERT INTO reservasi 
                           (id_kamar, nama_pemesan, email, no_telp, jumlah_kamar, nama_tamu, tanggal_check_in, tanggal_check_out, id_status) 
                           VALUES ((SELECT id_kamar FROM kamar WHERE id_tipe_kamar = %s), %s, %s, %s, %s, %s, %s, %s, 1)""", (reservasi.id_tipe_kamar, reservasi.nama_pemesan, reservasi.email, 
                                                                           reservasi.no_telp, reservasi.jumlah_kamar, reservasi.nama_tamu, 
                                                                           reservasi.tanggal_check_in, reservasi.tanggal_check_out))
         cursor.commit()
         id_reservasi = cursor.lastrowid()
         cursor.close()
         return {"message": "Reservasi Berhasil! Kamar telah dibooking. ", "id_reservasi": id_reservasi}
      except DatabaseError as e:
         raise HTTPException(status_code=400, detail=f'Something Went Wrong! {e}')

   else: 
      cursor.close()
      return {"message": "Reservasi Gagal! Kamar tidak tersedia atau tidak memenuhi quota pemesan. ", "kamar_tersedia": kamar_tersedia}


@router.get('/tipe_kamar')
def tipe_kamar(cursor: MySQLConnection = Depends(MySQLConnection)):
   cursor.execute("""SELECT kamar.id_kamar, tipe_kamar.nama_tipe_kamar 
                     FROM tipe_kamar INNER JOIN kamar ON kamar.id_tipe_kamar = tipe_kamar.id_tipe_kamar""")
   data = cursor.fetchall()
   cursor.close()
   return data


@router.get('/test/{id_reservasi}')
def test(id_reservasi: int, cursor: MySQLConnection = Depends(MySQLConnection)):
   cursor.execute("""SELECT id_reservasi, nama_pemesan, email, no_telp, jumlah_kamar, nama_tamu, tanggal_check_in, tanggal_check_out FROM reservasi 
                     WHERE id_reservasi = %s LIMIT 1""", (id_reservasi, ))
   data = cursor.fetchone()
   def file(**kwargs): 
      if len(kwargs) > 0: 
         pdf = PDF()
         pdf.add_page()
         pdf.write_html(f"""
         <h1>HOTEL HEBAT</h1>
         <h2>Bukti Reservasi</h2>
         <table width="100%">
            <tr>
               <td width="20%" align="left"><h7>Id Reservasi. </h7></td>
               <td width="80%" align="left"><h7>#{kwargs['id_reservasi']}</h7></td>
            </tr>
         </table>
         <table width="100%">
            <tr>
               <td width="20%">Nama Pemesan</td>
               <td width="4%" align="center">:</td>
               <td width="48%">{kwargs['nama_pemesan']}</td>
            </tr>
            <tr>
               <td width="20%">Email</td>
               <td width="4%" align="center">:</td>
               <td width="48%">{kwargs['email']}</td>
            </tr>
            <tr>
               <td width="20%">No. Telp</td>
               <td width="4%" align="center">:</td>
               <td width="48%">{kwargs['no_telp']}</td>
            </tr>
            <tr>
               <td width="20%">Nama Tamu</td>
               <td width="4%" align="center">:</td>
               <td width="48%">{kwargs['nama_tamu']}</td>
            </tr>
            <tr>
               <td width="20%">Jumlah Kamar</td>
               <td width="4%" align="center">:</td>
               <td width="48%">{kwargs['jumlah_kamar']}</td>
            </tr>
            <tr>
               <td width="20%">Tanggal Check-In</td>
               <td width="4%" align="center">:</td>
               <td width="48%">{kwargs['tanggal_check_in']}</td>
            </tr>
            <tr>
               <td width="20%">Tanggal Check-Out</td>
               <td width="4%" align="center">:</td>
               <td width="48%">{kwargs['tanggal_check_out']}</td>
            </tr>
         </table>
         """)
         pdf = pdf.output()
         pdf = BytesIO(pdf)
         yield from pdf
   cursor.close()
   try: 
      return StreamingResponse(file(**data), media_type='application/pdf')
   except TypeError:
      raise HTTPException(status_code=404, detail="Bukti reservasi tidak ditemukan.")

