from django.urls import path, include

from .views import product_views, attributegroup_views, attributesubgroup_views, attribute_views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'products', product_views.ProductViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path("product/", product_views.products_index, name="products_index"),    
    path("product/edit/", product_views.products_edit, name="products_edit"),
    path("product/edit/<int:product_id>/", product_views.products_edit, name="products_edit"),
    path("product/delete/<int:product_id>/", product_views.products_delete, name="products_delete"),

    path("productmaster/", product_views.productmaster_index, name="productmaster_index"),

    path("attributegroup/", attributegroup_views.attributegroups_index, name="attributegroups_index"),    
    path("attributegroup/edit/", attributegroup_views.attributegroups_edit, name="attributegroups_edit"),
    path("attributegroup/edit/<int:attributegroup_id>/", attributegroup_views.attributegroups_edit, name="attributegroups_edit"),
    path("attributegroup/delete/<int:attributegroup_id>/", attributegroup_views.attributegroups_delete, name="attributegroups_delete"),

    path("attributesubgroups/<int:attributegroup_id>/", attributesubgroup_views.attributesubgroups_index, name="attributesubgroups_index"),
    path("attributesubgroups/edit/", attributesubgroup_views.attributesubgroups_edit, name="attributesubgroups_edit"),
    path("attributesubgroups/edit/<int:attributesubgroup_id>/", attributesubgroup_views.attributesubgroups_edit, name="attributesubgroups_edit"),
    path("attributesubgroups/delete/<int:attributesubgroup_id>/", attributesubgroup_views.attributesubgroups_delete, name="attributesubgroups_delete"),

    path("attribute/<int:attributesubgroup_id>", attribute_views.attributes_index, name="attributes_index"),    
    path("attribute/edit/", attribute_views.attributes_edit, name="attributes_edit"),
    path("attribute/edit/<int:attribute_id>/", attribute_views.attributes_edit, name="attributes_edit"),
    path("attribute/delete/<int:attribute_id>/", attribute_views.attributes_delete, name="attributes_delete"),
]