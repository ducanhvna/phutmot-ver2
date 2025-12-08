from rest_framework import serializers
from .models import Customer


def _mask_id(value):
    if value is None:
        return value
    s = str(value)
    if len(s) <= 6:
        return s
    return s[:3] + ('*' * (len(s) - 6)) + s[-3:]


class CustomerSerializer(serializers.ModelSerializer):
    info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Customer
        fields = [
            'id', 'username', 'phone_number', 'id_card_number', 'old_id_card_number',
            'name', 'english_name', 'verification_status', 'info'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['id_card_number'] = _mask_id(instance.id_card_number)
        data['old_id_card_number'] = _mask_id(instance.old_id_card_number)
        return data

    def get_info(self, obj):
        info = getattr(obj, 'info', None)
        if isinstance(info, dict) and 'orders' in info:
            try:
                return {'orders_count': len(info.get('orders') or [])}
            except Exception:
                return {'orders_count': 0}

        orders_rel = getattr(obj, 'orders', None)
        if orders_rel is not None:
            try:
                return {'orders_count': orders_rel.count()}
            except Exception:
                try:
                    return {'orders_count': len(orders_rel)}
                except Exception:
                    return {'orders_count': 0}

        return info


class CustomerListSerializer(serializers.ModelSerializer):
    info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Customer
        fields = [
            'id', 'username', 'phone_number', 'id_card_number', 'old_id_card_number',
            'name', 'english_name', 'verification_status', 'info'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['id_card_number'] = _mask_id(instance.id_card_number)
        data['old_id_card_number'] = _mask_id(instance.old_id_card_number)
        return data

    def get_info(self, obj):
        info = getattr(obj, 'info', None)
        if isinstance(info, dict) and 'orders' in info:
            try:
                return {'orders_count': len(info.get('orders') or [])}
            except Exception:
                return {'orders_count': 0}

        orders_rel = getattr(obj, 'orders', None)
        if orders_rel is not None:
            try:
                return {'orders_count': orders_rel.count()}
            except Exception:
                try:
                    return {'orders_count': len(orders_rel)}
                except Exception:
                    return {'orders_count': 0}

        return info