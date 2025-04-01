from rest_framework import serializers


class ProductCategorySerializer(serializers.Serializer):
    ToiDa = serializers.IntegerField()
    ThemTrang = serializers.IntegerField()
    KhoiTaoThemTrang = serializers.IntegerField()
    GiaTrang = serializers.IntegerField()
    GiaBan = serializers.IntegerField()
    Indi_ID_Trang = serializers.IntegerField()
    Indi_ID = serializers.IntegerField()
    so_trang_mac_dinh = serializers.IntegerField()
