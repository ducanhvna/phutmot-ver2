from django.db import models
import unicodedata

def strip_accents(text):
    """
    Loại bỏ dấu tiếng Việt và chuyển về lowercase
    """
    if not text:
        return None
    text = unicodedata.normalize('NFD', text)
    text = ''.join([c for c in text if unicodedata.category(c) != 'Mn'])
    return text.lower()
# {
#   "gender": "Female",
#   "birth_date": "1995-10-06",
#   "age": 30,
#   "address": {
#     "full": "Minh Khai, Hai Bà Trưng, Hà Nội",
#     "ward_id": 73,
#     "district_id": 535,
#     "province_id": 35
#   },
#   "email": "tolayangxa@gmail.com",
#   "tax_code": null,
#   "representative": null,
#   "store_type": 1,
#   "store_notes": null,
#   "is_active": true,
#   "created_at": "2024-08-03T15:44:07.433",
#   "last_updated": "2024-08-03T15:44:07.433",
#   "orders": [
#     {
#       "order_code": "00003747",
#       "date": "2024-08-06",
#       "salesperson": "HIEN",
#       "amount": 15504000,
#       "invoice_url": "https://tchd.ehoadon.vn/Invoice_View/C2/4M/C24MBA-00003747-TBKYECBSW46-CK.pdf"
#     },
#     {
#       "order_code": "00004216",
#       "date": "2024-08-14",
#       "salesperson": "TRANG",
#       "amount": 7752000,
#       "invoice_url": "https://tchd.ehoadon.vn/Invoice_View/C2/4M/C24MBA-00004216-NBPUT6RA2VC-CK.pdf"
#     },
#     {
#       "order_code": "00006744",
#       "date": "2024-09-25",
#       "salesperson": "HUYENTMDT",
#       "amount": 8164000,
#       "invoice_url": null
#     }
#   ]
# }

class Customer(models.Model):
    username = models.CharField(max_length=150, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    id_card_number = models.CharField(max_length=20, null=True)
    old_id_card_number = models.CharField(max_length=20, blank=True, null=True)
    other_id_card_number = models.TextField(blank=True, null=True)
    name = models.CharField(max_length=255)
    english_name = models.CharField(max_length=255, blank=True, null=True)
    verification_status = models.BooleanField(default=False)

    # Trường bổ sung
    gender = models.CharField(max_length=10, choices=[("Male", "Male"), ("Female", "Female")], blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.JSONField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    # Trường info chứa thông tin về store profile
    info = models.JSONField(blank=True, null=True, help_text='Thông tin về store profile')

    def save(self, *args, **kwargs):
        # Tự động sinh english_name từ name
        if self.name:
            self.english_name = strip_accents(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
