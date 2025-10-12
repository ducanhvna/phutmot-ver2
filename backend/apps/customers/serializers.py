from rest_framework import serializers
from .models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    id_card_number = serializers.SerializerMethodField()
    old_id_card_number = serializers.SerializerMethodField()
    info = serializers.SerializerMethodField()
    class Meta:
        model = Customer
        fields = ['id', 'username', 'phone_number', 'id_card_number', 'old_id_card_number', 'name', 'english_name', 'verification_status', 'info']

    def _mask_id(self, value):
        """Mask value showing first 3 and last 3 characters, middle replaced with '*'"""
        if value is None:
            return value
        s = str(value)
        if len(s) <= 6:
            # Too short to mask sensibly, return as-is
            return s
        return s[:3] + ('*' * (len(s) - 6)) + s[-3:]

    def get_id_card_number(self, obj):
        return self._mask_id(getattr(obj, 'id_card_number', None))

    def get_old_id_card_number(self, obj):
        return self._mask_id(getattr(obj, 'old_id_card_number', None))

    def get_info(self, obj):
        """If possible, return only orders count in info.

        - If `info` is a dict with key 'orders' (iterable/list), return {'orders_count': N}
        - Else, if object has related `orders` manager, return its count
        - Otherwise return original `info` value
        """
        info = getattr(obj, 'info', None)
        if isinstance(info, dict) and 'orders' in info:
            try:
                return {'orders_count': len(info.get('orders') or [])}
            except Exception:
                return {'orders_count': 0}

        orders_rel = getattr(obj, 'orders', None)
        if orders_rel is not None:
            # try to call count() for queryset-like, fall back to len()
            try:
                return {'orders_count': orders_rel.count()}
            except Exception:
                try:
                    return {'orders_count': len(orders_rel)}
                except Exception:
                    return {'orders_count': 0}

        return info

class CustomerListSerializer(serializers.ModelSerializer):
    id_card_number = serializers.SerializerMethodField()
    old_id_card_number = serializers.SerializerMethodField()
    info = serializers.SerializerMethodField()
    class Meta:
        model = Customer
        fields = ['id', 'username', 'phone_number', 'id_card_number', 'old_id_card_number', 'name', 'english_name', 'verification_status', 'info']

    def _mask_id(self, value):
        if value is None:
            return value
        s = str(value)
        if len(s) <= 6:
            return s
        return s[:3] + ('*' * (len(s) - 6)) + s[-3:]

    def get_id_card_number(self, obj):
        return self._mask_id(getattr(obj, 'id_card_number', None))

    def get_old_id_card_number(self, obj):
        return self._mask_id(getattr(obj, 'old_id_card_number', None))

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