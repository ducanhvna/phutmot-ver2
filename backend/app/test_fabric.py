from sqlalchemy import create_engine

# Thông tin kết nối
TENANT_ID = "b77cc0b4-29c1-48c6-95fc-33791df200a3"
CLIENT_ID = "dbe7f28c-11f2-44df-900d-933c00218bdd"
CLIENT_SECRET = "jRI8Q~VMv9HMjINqMQaqDlI6qlgY.Rqo1sZ.5bRc"
SERVER = "wtahzn6bfhderfp4gn4r34qaum-tjyx4mk6erfelj2h7ifw6ym73u.datawarehouse.fabric.microsoft.com"  # Thay bằng server của bạn
DATABASE = "school"  # Thay bằng tên database của bạn

# Chuỗi kết nối ODBC
DATABASE_URL = f"mssql+pyodbc://{CLIENT_ID}:{CLIENT_SECRET}@{SERVER}/{DATABASE}?driver=ODBC+Driver+17+for+SQL+Server"

# Tạo engine
engine = create_engine(DATABASE_URL)

# Kiểm tra kết nối
with engine.connect() as connection:
    result = connection.execute("SELECT GETDATE()")
    print("Kết nối thành công:", result.fetchone())
