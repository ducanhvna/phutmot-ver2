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


class CustomerCreatePopupSerializer(serializers.ModelSerializer):
    """Serializer dùng riêng cho /api/customers/create/ để FE auto-fill popup.

    Các key bổ sung (permanent_address/street/street2/city) được derive từ Customer.address.
    """

    info = serializers.SerializerMethodField(read_only=True)
    permanent_address = serializers.SerializerMethodField(read_only=True)
    street = serializers.SerializerMethodField(read_only=True)
    street2 = serializers.SerializerMethodField(read_only=True)
    city = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Customer
        fields = [
            'id', 'username', 'phone_number', 'id_card_number', 'old_id_card_number',
            'name', 'english_name', 'verification_status',
            'gender', 'birth_date', 'email', 'address',
            'permanent_address', 'street', 'street2', 'city',
            'info'
        ]



    def get_info(self, obj):
        # Reuse the same lightweight logic as the default serializer
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

    def _get_address_dict(self, obj):
        address = getattr(obj, 'address', None)
        return address if isinstance(address, dict) else {}

    def get_permanent_address(self, obj):
        address = self._get_address_dict(obj)
        return (
            address.get('permanent_address')
            or address.get('dia_chi')
            or address.get('street')
            or ''
        )

    def get_street(self, obj):
        address = self._get_address_dict(obj)
        return address.get('street') or address.get('dia_chi') or ''

    def get_street2(self, obj):
        address = self._get_address_dict(obj)
        return address.get('street2') or address.get('phuong') or ''

    def get_city(self, obj):
        address = self._get_address_dict(obj)
        return address.get('city') or address.get('tinh') or ''