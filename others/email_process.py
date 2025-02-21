import imaplib
import email
from email.header import decode_header

# Thông tin đăng nhập
username = "hrm@apec.com.vn "
password = "Apec@2025!"

# Kết nối tới máy chủ IMAP
mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login(username, password)

# Chọn hộp thư (INBOX)
mail.select("sent")

# Tìm kiếm tất cả email
status, messages = mail.search(None, "ALL")

# Lấy danh sách ID email
email_ids = messages[0].split()
print(email_ids)
# Đọc từng email
for email_id in email_ids:
    # Lấy dữ liệu email
    status, msg_data = mail.fetch(email_id, "(RFC822)")
    print(msg_data)
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            # Phân tích email
            msg = email.message_from_bytes(response_part[1])
            from_ = msg.get("From")
            print("From:", from_)
            to_ = msg.get("To")
            print("To:", to_)
            # subject, encoding = decode_header(msg["Subject"])[0]
            # if isinstance(subject, bytes):
            #     subject = subject.decode(encoding if encoding else "utf-8")
            # print("Subject:", subject)
            
            # # Kiểm tra phần nội dung email
            # if msg.is_multipart():
            #     for part in msg.walk():
            #         content_type = part.get_content_type()
            #         content_disposition = str(part.get("Content-Disposition"))
            #         try:
            #             if "attachment" not in content_disposition:
            #                 payload = part.get_payload(decode=True)
            #                 print("Body:", payload.decode())
            #         except Exception as ex:
            #             print(ex)
            # else:
            #     payload = msg.get_payload(decode=True)
            #     print("Body:", payload.decode())

# Đóng kết nối
mail.logout()
