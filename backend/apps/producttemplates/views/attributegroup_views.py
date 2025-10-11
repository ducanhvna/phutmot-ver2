from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from apps.producttemplates.models import AttributeGroup

@login_required
def attributegroups_index(request):
    """
    Hiển thị danh sách các AttributeGroup.
    """
    attributegroups = AttributeGroup.objects.all().order_by('name')
    context = {
        'attributegroups': attributegroups,
    }
    return render(request, 'attributegroups/index.html', context)

@login_required
def attributegroups_edit(request, attributegroup_id=None):
    """
    Thêm mới hoặc cập nhật AttributeGroup.
    """
    attributegroup = None
    page_title = 'Thêm Nhóm Thuộc tính Mới'

    if attributegroup_id:
        attributegroup = get_object_or_404(AttributeGroup, pk=attributegroup_id)
        page_title = f'Chỉnh sửa: {attributegroup.display_name}'

    if request.method == 'POST':
        name = request.POST.get('name')
        display_name = request.POST.get('display_name')
        description = request.POST.get('description')

        if not name or not display_name:
            messages.error(request, "Tên và Tên hiển thị không được để trống.")
            return redirect(request.path)

        try:
            if attributegroup:
                # Cập nhật
                attributegroup.name = name
                attributegroup.display_name = display_name
                attributegroup.description = description
                attributegroup.modified_user = request.user
                attributegroup.save()
                messages.success(request, f'Đã cập nhật nhóm thuộc tính "{attributegroup.display_name}".')
            else:
                # Tạo mới
                attributegroup = AttributeGroup.objects.create(
                    name=name,
                    display_name=display_name,
                    description=description,
                    created_user=request.user,
                    modified_user=request.user,
                )
                messages.success(request, f'Đã thêm nhóm thuộc tính "{attributegroup.display_name}" thành công.')
            
            return redirect('attributegroups:attributegroups_index')

        except IntegrityError:
            messages.error(request, "Tên nhóm thuộc tính đã tồn tại. Vui lòng chọn tên khác.")
        except Exception as e:
            messages.error(request, f"Có lỗi xảy ra: {e}")
            
    context = {
        'attributegroup': attributegroup,
        'page_title': page_title,
    }
    return render(request, 'attributegroups/edit.html', context)

@login_required
def attributegroups_delete(request, attributegroup_id):
    attributegroup = get_object_or_404(AttributeGroup, pk=attributegroup_id)
    
    # Check if the request method is POST for a more secure deletion process
    if request.method == 'POST':
        attributegroup.delete()
        messages.success(request, f'Đã xóa nhóm thuộc tính "{attributegroup.display_name}" thành công.')
    
    # Redirect back to the index page, regardless of the request method
    return redirect('attributegroups:attributegroups_index')