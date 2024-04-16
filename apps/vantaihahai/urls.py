from django.urls import path
from django.contrib.auth.models import User
from .views import SyncUserDevice, GetListCompany, GetListHrmEmployees, GetListHrmAttendanceReport, \
        ThongtintaixeApi, Tatcachuyendi, Cacchuyenhomnay, CapnhatkmKetthuc, CapnhatHanghoa, \
        CapnhatkmBatdau, CapnhatDiadiemBatdau, CapnhatDiadiemKetthuc, Danhsachtatcaxe, \
        Thongtinxe, ListYeucaubaotrixe, TaoghichuBaotri, Danhsachcactinh, ListHuyentheotinh, \
        TatcaDiadiem, DanhsachMathang, Taohanhtrinh
urlpatterns = [
    path("syncuser/", SyncUserDevice.as_view(), name='vantai_api_syncuser'),
    path("listcompany/", GetListCompany.as_view(), name='vantai_api_listcompany'),
    path("hrmemployees/", GetListHrmEmployees.as_view(), name='vantai_api_list_employee'),
    path("hrmattendances/", GetListHrmAttendanceReport.as_view(), name='v2_list_attendance'),
    path("api/core/thongtintaixe/", ThongtintaixeApi.as_view(), name='hahai_thongtintaixe'),
    path("api/core/tatcachuyendicuataixe/", Tatcachuyendi.as_view(), name='hahai_tatcachuyendicuataixe'),
    path("api/core/tatcachuyendihomnay/", Cacchuyenhomnay.as_view(), name='hahai_tatcachuyendihomnay'),
    path("api/core/<int:hanhtrinh>/capnhatkmketthuc/", CapnhatkmKetthuc.as_view(), name='hahai_capnhatkmketthuc'),
    path("api/core/<int:hanhtrinh>/capnhathanghoa/", CapnhatHanghoa.as_view(), name='hahai_capnhathanghoa'),
    path("api/core/<int:hanhtrinh>/capnhatkmbatdau/", CapnhatkmBatdau.as_view(), name='hahai_capnhatkmbatdau'),
    path("api/core/<int:hanhtrinh>/capnhatlocbatdau/", CapnhatDiadiemBatdau.as_view(), name='hahai_capnhatlocbatdau'),
    path("api/core/<int:hanhtrinh>/capnhatlocketthuc/", CapnhatDiadiemKetthuc.as_view(), name='hahai_capnhatlocketthuc'),
    path("api/core/danhsachtatcaxe/", Danhsachtatcaxe.as_view(), name='hahai_danhsachtatcaxe'),

    path("api/core/<int:equitment>/thongtinxe/", Thongtinxe.as_view(), name="hahai_thongtinxe"),

    path("api/core/<int:equitment>/danhsachyeucaubaotri/", ListYeucaubaotrixe.as_view(), name="list_yeucaubaotri"),
    path("api/core/<int:equitment>/taoghichu/", TaoghichuBaotri.as_view(), name="capnhat_ghichubaotri"),
    path("api/core/danhsachcactinh/", Danhsachcactinh.as_view(), name="list_tinh"),
    path("api/core/<int:province>/danhsachcachuyen/", ListHuyentheotinh.as_view(), name="list_huyen"),
    # district
    path("api/core/<int:district>/danhsachcacphuong/", ListHuyentheotinh.as_view(), name="list_phuong"),
    path("api/core/danhsachcacdiadiem/", TatcaDiadiem.as_view(), name="list_diadiem"),
    path("api/core/danhsachmathang/", DanhsachMathang.as_view(), name="list_mathang"),
    path("api/core/taohanhtrinh/", Taohanhtrinh.as_view(), name="hahai_taohanhtrinh"),
]