from pydantic import BaseModel
from datetime import date


class reservation(BaseModel):
   id_tipe_kamar: int
   nama_pemesan: str
   email: str
   no_telp: str
   jumlah_kamar: int
   nama_tamu: str
   tanggal_check_in: date
   tanggal_check_out: date
