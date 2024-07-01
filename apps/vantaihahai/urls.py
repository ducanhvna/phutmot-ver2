from django.urls import path
from django.contrib.auth.models import User
from .views import SyncUserDevice, GetListCompany, GetListHrmEmployees, GetListHrmAttendanceReport, \
        ThongtintaixeApi, Tatcachuyendi, Cacchuyenhomnay, CapnhatkmKetthuc, CapnhatHanghoa, \
        CapnhatkmBatdau, CapnhatDiadiemBatdau, CapnhatDiadiemKetthuc, Danhsachtatcaxe, \
        Thongtinxe, ListYeucaubaotrixe, TaoghichuBaotri, Danhsachcactinh, ListHuyentheotinh, \
        TatcaDiadiem, DanhsachMathang, Taohanhtrinh, Taobaotri,fetchChatView, Fetchmessagevehicle
urlpatterns = [
    path("syncuser/", SyncUserDevice.as_view(), name='vantai_api_syncuser'),
    path("listcompany/", GetListCompany.as_view(), name='vantai_api_listcompany'),
    path("hrmemployees/", GetListHrmEmployees.as_view(), name='vantai_api_list_employee'),
    path("hrmattendances/", GetListHrmAttendanceReport.as_view(), name='v2_list_attendance'),
    path("thongtintaixe/", ThongtintaixeApi.as_view(), name='hahai_thongtintaixe'),
    path("tatcachuyendicuataixe/", Tatcachuyendi.as_view(), name='hahai_tatcachuyendicuataixe'),
    path("tatcachuyendihomnay/", Cacchuyenhomnay.as_view(), name='hahai_tatcachuyendihomnay'),
    path("<int:hanhtrinh>/fetchfleetChat/", fetchChatView.as_view(), name='hahai_fetchChat'),
    path("<int:hanhtrinh>/capnhatkmketthuc/", CapnhatkmKetthuc.as_view(), name='hahai_capnhatkmketthuc'),
    path("<int:hanhtrinh>/capnhathanghoa/", CapnhatHanghoa.as_view(), name='hahai_capnhathanghoa'),
    path("<int:hanhtrinh>/capnhatkmbatdau/", CapnhatkmBatdau.as_view(), name='hahai_capnhatkmbatdau'),
    path("<int:hanhtrinh>/capnhatlocbatdau/", CapnhatDiadiemBatdau.as_view(), name='hahai_capnhatlocbatdau'),
    path("<int:hanhtrinh>/capnhatlocketthuc/", CapnhatDiadiemKetthuc.as_view(), name='hahai_capnhatlocketthuc'),
    path("danhsachtatcaxe/", Danhsachtatcaxe.as_view(), name='hahai_danhsachtatcaxe'),

    path("<int:equitment>/thongtinxe/", Thongtinxe.as_view(), name="hahai_thongtinxe"),
    path("<int:equitment>/fetchmessagevehicle/", Fetchmessagevehicle.as_view(), name="hahai_fetchmessagevehicle"),

    path("<int:equitment>/danhsachyeucaubaotri/", ListYeucaubaotrixe.as_view(), name="list_yeucaubaotri"),
    path("<int:equitment>/taoghichu/", TaoghichuBaotri.as_view(), name="capnhat_ghichubaotri"),
    path("danhsachcactinh/", Danhsachcactinh.as_view(), name="list_tinh"),
    path("<int:province>/danhsachcachuyen/", ListHuyentheotinh.as_view(), name="list_huyen"),
    # district
    path("<int:district>/danhsachcacphuong/", ListHuyentheotinh.as_view(), name="list_phuong"),
    path("danhsachcacdiadiem/", TatcaDiadiem.as_view(), name="list_diadiem"),
    path("danhsachmathang/", DanhsachMathang.as_view(), name="list_mathang"),
    path("taohanhtrinh/", Taohanhtrinh.as_view(), name="hahai_taohanhtrinh"),
    path("taobaotri/", Taobaotri.as_view(), name="hahai_taobaotri"),
]