# agent_listen
Co-op (SGC Services)

## Example

````shell
INTERFACE= ขาอินเตอร์เน็ตที่ต้องการเปิดใช้งาน
PORT= port ที่ต้องการให้ listener
DB_HOST= database ip host
DB_PORT= database port
DB_USER= database username
DB_PASSWORD= database password
DB_NAME= database name
# ============================================================================================================================================
# set path on file from client directory 
# ============================================================================================================================================
SOURCINATION= ที่อยู่ของการจัดเก็บไฟล์ FTP in listener
DESTINATION_LOG= ที่อยู่หลังจากรับไฟล์ Log from FTP in lister
DESTINATION_DOC= ที่อยู่หลังจากรับไฟล์ Doc, CSV, XCSV from FTP in lister
# ============================================================================================================================================
# Table here for client logs hash0
# ============================================================================================================================================
TB_LOG0="TB_TR_PDPA_AGENT_LOG0_HASH:device_name, os_name, path, name_file, total_line, value, value_md5, value_sha1"
# ============================================================================================================================================
# Table here client directory/file *NOTE* must have column ID!!
# ============================================================================================================================================
TB_FILE="TB_TR_PDPA_AGENT_FILE_DIR:id, device_name, os_name, path, name_file, size"
# ============================================================================================================================================
# Table here client check database *NOTE* must have column ID!!
# ============================================================================================================================================
TB_DB_CHECK="TB_TR_PDPA_AGENT_DATABASE_CHECK:field_1, field_2, field_3, field_4, field_5, field_6, field_7, field_8, field_9, field_0, from_client"
# ============================================================================================================================================
````
