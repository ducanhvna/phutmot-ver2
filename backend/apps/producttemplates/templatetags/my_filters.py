# my_app/templatetags/my_filters.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    # Kiểm tra nếu giá trị đầu vào là dictionary
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    # Nếu không phải, trả về None hoặc một giá trị mặc định khác
    return None