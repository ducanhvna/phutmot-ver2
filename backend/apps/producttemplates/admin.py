from django.contrib import admin
from .models import AttributeGroup, AttributeSubGroup, Attribute, Tag, Product

admin.site.register(AttributeGroup)
admin.site.register(AttributeSubGroup)
admin.site.register(Attribute)
admin.site.register(Tag)
admin.site.register(Product)
