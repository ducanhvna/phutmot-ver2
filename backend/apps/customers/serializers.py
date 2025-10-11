from rest_framework import serializers
from .models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'username', 'phone_number', 'id_card_number', 'old_id_card_number', 'name', 'english_name', 'verification_status', 'info']