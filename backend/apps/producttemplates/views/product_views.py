import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from ..serializers import ProductSerializer
from rest_framework import viewsets
from apps.producttemplates.models import Product, AttributeGroup, Attribute

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


# ----------------------------
# Helpers (tái sử dụng)
# ----------------------------
def _safe_to_str(v):
    if isinstance(v, (dict, list)):
        try:
            return json.dumps(v, ensure_ascii=False)
        except Exception:
            return str(v)
    return str(v)


def _is_blank(v):
    if v is None:
        return True
    s = str(v).strip()
    return s == '' or s.lower() in ('null', 'none')


def parse_info_field(info_field):
    """
    Chuẩn hoá 1 field info (có thể là dict/list/scalar hoặc JSON string)
    -> trả về list các string (mỗi phần tử sẽ hiển thị trên 1 dòng).
    Quy tắc:
      - Nếu dict có key 'value' (case-insensitive) và value là list -> tách từng phần tử (không show 'value:')
      - Nếu dict khác -> show "key: value" (mở rộng list)
      - Nếu top-level list -> tách từng phần tử
      - Nếu scalar (hoặc JSON string scalar) -> trả về 1 phần tử nếu không rỗng
      - Bỏ phần tử rỗng/[]/null
    """
    out = []
    if info_field in (None, ''):
        return out

    # nếu là dict/python object
    if isinstance(info_field, dict):
        # xử lý 'value' nếu có (case-insensitive)
        lower_map = {k.lower(): k for k in info_field.keys()}
        if 'value' in lower_map:
            real_key = lower_map['value']
            v = info_field.get(real_key)
            if isinstance(v, list):
                for item in v:
                    if isinstance(item, list) and len(item) == 0:
                        continue
                    if not _is_blank(item):
                        out.append(_safe_to_str(item))
            else:
                if not _is_blank(v):
                    out.append(_safe_to_str(v))
            # process other keys as "key: value"
            for k, other_v in info_field.items():
                if k == real_key:
                    continue
                if isinstance(other_v, list):
                    for item in other_v:
                        if isinstance(item, list) and len(item) == 0:
                            continue
                        if not _is_blank(item):
                            out.append(f"{k}: {_safe_to_str(item)}")
                else:
                    if not _is_blank(other_v):
                        out.append(f"{k}: {_safe_to_str(other_v)}")
        else:
            # không có 'value' -> flatten keys
            for k, v in info_field.items():
                if isinstance(v, list):
                    for item in v:
                        if isinstance(item, list) and len(item) == 0:
                            continue
                        if not _is_blank(item):
                            out.append(f"{k}: {_safe_to_str(item)}")
                else:
                    if not _is_blank(v):
                        out.append(f"{k}: {_safe_to_str(v)}")
        return out

    # nếu là list
    if isinstance(info_field, list):
        for item in info_field:
            if isinstance(item, list) and len(item) == 0:
                continue
            if not _is_blank(item):
                out.append(_safe_to_str(item))
        return out

    # nếu là chuỗi JSON hay scalar string -> thử parse JSON, fallback scalar
    try:
        parsed = json.loads(info_field)
        return parse_info_field(parsed)
    except Exception:
        if not _is_blank(info_field):
            return [str(info_field)]
        return []


def build_groups_and_flat_attrs(attribute_groups_qs):
    """
    Tạo groups_data và flat_attributes từ queryset AttributeGroup.
    groups_data structure:
      [
        {
          'obj': group_instance,
          'subgroups': [ {'obj': subgroup_instance, 'attributes': [attr_entry,...]}, ... ],
          'total_cols': int
        },
        ...
      ]
    flat_attributes: list of attribute entries in header order.
    Mỗi attribute entry = {'obj': attr_instance_or_none, 'name': display_name_or_name, 'values': [...]}
    Note: attribute.info được parse để gán vào 'values' (dùng parse_info_field) — đây phục vụ productmaster_index display.
    """
    groups_data = []
    flat_attributes = []
    max_values = 0

    groups = list(attribute_groups_qs)
    for g in groups:
        g_entry = {'obj': g, 'subgroups': [], 'total_cols': 0}
        subs = list(g.subgroups.all())
        for s in subs:
            s_entry = {'obj': s, 'attributes': []}
            attrs = list(s.attributes.all())
            if not attrs:
                attr_entry = {'obj': None, 'name': '-', 'values': []}
                s_entry['attributes'].append(attr_entry)
                flat_attributes.append(attr_entry)
            else:
                for a in attrs:
                    info_field = getattr(a, 'info', None)
                    # parse attribute.info into list of values (for attribute cell content)
                    values = parse_info_field(info_field)

                    if len(values) > max_values:
                        max_values = len(values)

                    attr_entry = {
                        'obj': a,
                        'name': getattr(a, 'display_name', None) or getattr(a, 'name', '-'),
                        'values': values
                    }
                    s_entry['attributes'].append(attr_entry)
                    flat_attributes.append(attr_entry)
            g_entry['subgroups'].append(s_entry)

        # compute total cols
        total = 0
        for s in g_entry['subgroups']:
            total += max(1, len(s['attributes']))
        g_entry['total_cols'] = total if total > 0 else 1
        groups_data.append(g_entry)

    return groups_data, flat_attributes, max_values

def productmaster_index(request):
    """
    Hiển thị product master theo attribute.info (mỗi attribute có info json riêng).
    Giữ nguyên logic xử lý JSON như trước.
    """
    groups_qs = AttributeGroup.objects.prefetch_related('subgroups__attributes').all()
    groups_data, flat_attributes, max_values = build_groups_and_flat_attrs(groups_qs)

    # build body_rows from flat_attributes (each attr has 'values' parsed)
    if max_values == 0:
        max_values = 1

    body_rows = []
    for i in range(max_values):
        row_cells = []
        for attr in flat_attributes:
            if i < len(attr['values']):
                row_cells.append(attr['values'][i])
            else:
                row_cells.append('')
        body_rows.append(row_cells)

    context = {
        'groups_data': groups_data,
        'flat_attributes': flat_attributes,
        'body_rows': body_rows,
    }
    return render(request, 'productmaster/index.html', context)


def products_index(request):
    """
    Hiển thị danh sách products: header same as groups; mỗi product tạo rowspan theo số values nhiều nhất;
    các cell của product lấy từ product.info[attr.name] và parse bằng parse_info_field.
    """
    products = Product.objects.all().order_by('name')
    attribute_groups = AttributeGroup.objects.prefetch_related('subgroups__attributes').all().order_by('id')

    groups_data, flat_attributes, _ = build_groups_and_flat_attrs(attribute_groups)

    # Build products_data
    products_data = []
    for product in products:
        prod_info = getattr(product, 'info', None) or {}
        attr_values_lists = []
        for attr in flat_attributes:
            # attr may be dict placeholder or object
            attr_name = getattr(attr, 'name', None) or (attr.get('name') if isinstance(attr, dict) else None)

            # lookup in product.info (assuming keys are attr_name)
            cell_raw = None
            if isinstance(prod_info, dict) and attr_name:
                cell_raw = prod_info.get(attr_name)

            parsed_values = parse_info_field(cell_raw)
            attr_values_lists.append(parsed_values)

        # rows count
        max_vals = max((len(l) for l in attr_values_lists), default=0)
        if max_vals == 0:
            max_vals = 1

        rows = []
        for i in range(max_vals):
            row_cells = []
            for vals in attr_values_lists:
                if i < len(vals):
                    row_cells.append(vals[i])
                else:
                    row_cells.append('')
            rows.append(row_cells)

        products_data.append({
            'product': product,
            'rows': rows,
            'rowspan': max_vals
        })

    context = {
        'groups_data': groups_data,
        'flat_attributes': flat_attributes,
        'products_data': products_data,
    }
    return render(request, 'products/index.html', context)


def products_edit(request, product_id=None):
    """
    Tạo / Cập nhật product.
    Nếu attribute không được chọn -> lưu None (JSON null).
    """
    product = None
    if product_id:
        product = get_object_or_404(Product, id=product_id)

    all_attributes = Attribute.objects.all().order_by('name')

    if request.method == 'POST':
        name = request.POST.get('name')

        info_data = {}
        for attr in all_attributes:
            key = f'attr_{attr.name}'
            value = request.POST.get(key)
            if value is None or value == '':
                info_data[attr.name] = None
            else:
                info_data[attr.name] = value

        # Thêm/ghi tên sản phẩm trong info nếu bạn muốn giữ
        info_data['Product Name'] = name

        if product:
            product.name = name
            product.info = info_data
            product.save()
        else:
            product = Product.objects.create(name=name, info=info_data)

        return redirect('product:products_index')

    context = {
        'product': product,
        'all_attributes': all_attributes,
        'attribute_groups': [],  # giữ placeholder nếu cần
    }
    return render(request, 'products/edit.html', context)


def products_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    name = product.name
    product.delete()
    messages.success(request, f"Sản phẩm '{name}' đã được xóa thành công.")
    return redirect(reverse('product:products_index'))
