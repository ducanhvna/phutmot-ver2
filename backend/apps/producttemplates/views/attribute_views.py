from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.db.models import Max

from apps.producttemplates.models import AttributeSubGroup, Attribute  


@login_required
def attributes_index(request, attributesubgroup_id=None):
    """
    Hiển thị danh sách Attribute theo AttributeSubGroup.
    URL chính: /attribute/<int:attributesubgroup_id>  (ưu tiên)
    Hoặc dùng query string: /attribute/?subgroup_id=...
    """
    # ưu tiên param URL, fallback query param
    subgroup_id = attributesubgroup_id or request.GET.get('subgroup_id')

    subgroup = None
    if subgroup_id:
        try:
            subgroup = get_object_or_404(AttributeSubGroup, pk=int(subgroup_id))
        except (ValueError, TypeError):
            subgroup = None

    if subgroup:
        # nếu related_name='attributes' trên FK
        try:
            attributes = subgroup.attributes.all().order_by('sequence')
        except Exception:
            attributes = Attribute.objects.filter(subgroup=subgroup).order_by('sequence')
    else:
        attributes = Attribute.objects.all().order_by('name')

    context = {
        'subgroup': subgroup,
        'attributes': attributes,
        'subgroups_list': AttributeSubGroup.objects.all().order_by('name'),  # nếu cần sidebar/filter
    }
    return render(request, 'attributes/index.html', context)


@login_required
def attributes_edit(request, attribute_id=None):
    """
    Tạo mới hoặc sửa Attribute.
    - Edit: attribute_id != None -> lấy đối tượng và subgroup từ đó.
    - Create: attribute_id is None -> phải có subgroup_id qua GET (?subgroup_id=...) hoặc POST (hidden input).
    """
    attribute_obj = None
    subgroup = None
    page_title = 'Thêm Attribute Mới'

    if attribute_id:
        attribute_obj = get_object_or_404(Attribute, pk=attribute_id)
        subgroup = attribute_obj.subgroup
        page_title = f'Chỉnh sửa: {attribute_obj.display_name or attribute_obj.name}'
    else:
        subgroup_id = request.GET.get('subgroup_id') or request.POST.get('subgroup_id')
        if subgroup_id:
            try:
                subgroup = AttributeSubGroup.objects.get(pk=int(subgroup_id))
            except (AttributeSubGroup.DoesNotExist, ValueError, TypeError):
                subgroup = None

    if not subgroup:
        messages.error(request, "Thiếu Subgroup (subgroup_id). Vui lòng mở trang tạo từ trang Subgroup.")
        return redirect(reverse('product:attributesubgroups_index'))

    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()
        display_name = (request.POST.get('display_name') or '').strip()
        info_raw = (request.POST.get('info') or '').strip()

        # Chuyển info thành JSON { "value": [...] }
        info_json = {}
        if info_raw:
            try:
                # nếu nhập chuỗi, ví dụ: "a, b, c"
                values = [x.strip() for x in info_raw.split(",") if x.strip()]
                info_json = {"value": values}
            except Exception:
                info_json = {"value": [info_raw]}

        if not name or not display_name:
            messages.error(request, "Tên (code) và Tên hiển thị là bắt buộc.")
        else:
            try:
                if attribute_obj:
                    attribute_obj.name = name
                    attribute_obj.display_name = display_name
                    attribute_obj.info = info_json  # Lưu JSON
                    try:
                        attribute_obj.modified_user = request.user
                    except Exception:
                        pass
                    attribute_obj.save()
                    messages.success(request, f'Đã cập nhật attribute "{attribute_obj.display_name}".')
                else:
                    max_seq = Attribute.objects.filter(subgroup=subgroup).aggregate(Max('sequence'))['sequence__max'] or 0
                    attribute_obj = Attribute.objects.create(
                        subgroup=subgroup,
                        name=name,
                        display_name=display_name,
                        sequence=max_seq + 1,
                        info=info_json,  # Lưu JSON
                        created_user=getattr(request, 'user', None),
                        modified_user=getattr(request, 'user', None),
                    )
                    messages.success(request, f'Đã thêm attribute "{attribute_obj.display_name}" thành công.')

                # redirect về list attributes của subgroup
                return redirect(reverse('product:attributes_index', args=[subgroup.id]))
            except IntegrityError:
                messages.error(request, "Tên attribute đã tồn tại. Vui lòng chọn tên khác.")
            except Exception as e:
                messages.error(request, f"Có lỗi xảy ra: {e}")

    context = {
        'attribute': attribute_obj,
        'page_title': page_title,
        'subgroup': subgroup,
        'subgroup_id': subgroup.id,
    }
    return render(request, 'attributes/edit.html', context)


@login_required
def attributes_delete(request, attribute_id):
    """
    Xóa attribute và redirect về danh sách của subgroup cha.
    """
    obj = get_object_or_404(Attribute, pk=attribute_id)
    subgroup = obj.subgroup
    try:
        obj.delete()
        messages.success(request, "Đã xóa attribute.")
    except Exception as e:
        messages.error(request, f"Có lỗi khi xóa: {e}")

    try:
        return redirect(reverse('product:attributes_index', args=[subgroup.id]))
    except Exception:
        return redirect('attributes_index', attributesubgroup_id=subgroup.id)
