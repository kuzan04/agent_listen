# agent_listen
Co-op (SGC Services)

**WARNING**: the script need to call the superuser of os you!!

## Example

````shell
INTERFACE= ขาอินเตอร์เน็ตที่ต้องการเปิดใช้งาน
PORT= port ที่ต้องการให้ listener
DB_HOST= database ip host
DB_PORT= database port
DB_USER= database username
DB_PASSWORD= database password
DB_NAME= database name
# ========================================================================
# set path on file from client directory 
# ========================================================================
SOURCINATION= ที่อยู่ของการจัดเก็บไฟล์ FTP in listener
DESTINATION_LOG= ที่อยู่หลังจากรับไฟล์ Log from FTP in lister
DESTINATION_DOC= ที่อยู่หลังจากรับไฟล์ Doc, CSV, XCSV from FTP in lister
# ========================================================================
SOURCINATION= ที่อยู่ของการจัดเก็บไฟล์ FTP in listener
# Table here for client logs hash0
# ========================================================================
TB_LOG0= ชื่อ:ตามโดย columns or fields ต่อกันด้วย ',' ไปจนถึงตัวสุดท้ายก็ไม่ต้องใส่
# ========================================================================
# Table here client directory/file *NOTE* must have column ID!!
# ========================================================================
TB_FILE= ชื่อ:ตามโดย columns or fields ต่อกันด้วย ',' ไปจนถึงตัวสุดท้ายก็ไม่ต้องใส่ 
# ========================================================================
# Table here client check database *NOTE* must have column ID!!
# ========================================================================
TB_DB_CHECK= ชื่อ:ตามโดย columns or fields ต่อกันด้วย ',' ไปจนถึงตัวสุดท้ายก็ไม่ต้องใส่
# ========================================================================
# ========================================================================
TB_HISTORY= ชื่อ:ตามโดย columns id ของ agent manager เท่านั้น
# ========================================================================

````
