from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Max

from apps.producttemplates.models import AttributeGroup, AttributeSubGroup

@login_required
def attributesubgroups_index(request, attributegroup_id=None):
    # ưu tiên param URL (nếu view được gọi như /attributesubgroups/6/)
    group_id = attributegroup_id or request.GET.get('group_id')

    group = None
    if group_id:
        try:
            group = get_object_or_404(AttributeGroup, pk=int(group_id))
            subgroups = AttributeSubGroup.objects.filter(group=group).order_by('sequence')
        except (ValueError, TypeError):
            group = None
            subgroups = AttributeSubGroup.objects.all().order_by('name')
    else:
        subgroups = AttributeSubGroup.objects.all().order_by('name')

    context = {
        'group': group,
        'subgroups': subgroups,
        'attributegroups_list': AttributeGroup.objects.all().order_by('name')
    }
    return render(request, 'attributesubgroups/index.html', context)

@login_required
def attributesubgroups_edit(request, attributesubgroup_id=None):
    """
    Nếu attributesubgroup_id có -> edit (group lấy từ đối tượng)
    Nếu không -> create (bắt buộc có group_id qua GET hoặc POST)
    Luồng của bạn: luôn đi từ group -> subgroup, nên template chỉ hiển thị group info (hidden input)
    """
    attributesubgroup = None
    group = None
    page_title = 'Thêm Nhóm Con Mới'

    # Nếu edit -> load subgroup và group từ đó
    if attributesubgroup_id:
        attributesubgroup = get_object_or_404(AttributeSubGroup, pk=attributesubgroup_id)
        group = attributesubgroup.group
        page_title = f'Chỉnh sửa: {attributesubgroup.display_name or attributesubgroup.name}'
    else:
        # Tạo mới: bắt buộc có group_id trong GET khi mở form, hoặc trong POST khi submit
        group_id = request.GET.get('group_id') or request.POST.get('group_id')
        if group_id:
            try:
                group = AttributeGroup.objects.get(pk=int(group_id))
            except (AttributeGroup.DoesNotExist, ValueError, TypeError):
                group = None

    # Nếu không có group -> redirect về danh sách group (luồng của bạn luôn có group, nên đây là lỗi)
    if not group:
        messages.error(request, "Thiếu nhóm cha (group_id). Vui lòng mở trang tạo từ trang Attribute Group.")
        try:
            return redirect(reverse('product:attributegroups_index'))
        except Exception:
            return redirect('attributegroups_index')

    # Xử lý POST (lưu)
    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()
        display_name = (request.POST.get('display_name') or '').strip()
        description = (request.POST.get('description') or '').strip()

        # validate cơ bản
        if not name or not display_name:
            messages.error(request, "Tên (code) và Tên hiển thị không được để trống.")
        else:
            try:
                if attributesubgroup:
                    # update
                    attributesubgroup.name = name
                    attributesubgroup.display_name = display_name
                    attributesubgroup.description = description
                    try:
                        attributesubgroup.modified_user = request.user
                    except Exception:
                        pass
                    attributesubgroup.save()
                    messages.success(request, f'Đã cập nhật nhóm con "{attributesubgroup.display_name}".')
                else:
                    # create: lấy sequence = max + 1
                    max_sequence = AttributeSubGroup.objects.filter(group=group).aggregate(Max('sequence'))['sequence__max'] or 0
                    attributesubgroup = AttributeSubGroup.objects.create(
                        group=group,
                        name=name,
                        display_name=display_name,
                        description=description,
                        sequence=max_sequence + 1,
                        created_user=getattr(request, 'user', None),
                        modified_user=getattr(request, 'user', None),
                    )
                    messages.success(request, f'Đã thêm nhóm con "{attributesubgroup.display_name}" thành công.')

                # Sau khi lưu -> redirect về danh sách subgroup của group cha
                try:
                    return redirect(reverse('product:attributesubgroups_index', args=[group.id]))
                except Exception:
                    return redirect('attributesubgroups_index', attributegroup_id=group.id)
            except IntegrityError:
                messages.error(request, "Tên nhóm con đã tồn tại. Vui lòng chọn tên khác.")
            except Exception as e:
                messages.error(request, f"Có lỗi xảy ra: {e}")

    # Render form (GET hoặc POST có lỗi)
    context = {
        'attributesubgroup': attributesubgroup,
        'page_title': page_title,
        'group': group,
        'group_id': group.id,
    }
    return render(request, 'attributesubgroups/edit.html', context)

@login_required
def attributesubgroups_delete(request, attributesubgroup_id):
    attributesubgroup = get_object_or_404(AttributeSubGroup, pk=attributesubgroup_id)
    if request.method == 'POST':
        attributesubgroup.delete()
        messages.success(request, f'Đã xóa nhóm con "{attributesubgroup.display_name}" thành công.')
    
    return redirect('producttemplates:attributesubgroups_index')