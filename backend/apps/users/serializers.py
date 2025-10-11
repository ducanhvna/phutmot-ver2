from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'unique_key']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=self.generate_username(validated_data['email']),
            unique_key=self.generate_unique_key()
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def generate_username(self, email):
        return email.split('@')[0]

    def generate_unique_key(self):
        import random
        import string
        return ''.join(random.choices(string.ascii_letters + string.digits, k=8))