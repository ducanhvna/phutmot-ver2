import xmlrpc.client

# Thông tin kết nối
url = "https://admin.hinosoft.com"
db = "goldsun"
username = "admin"
password = "admin"

# Kết nối đến server Odoo
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})

if uid:

    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
    
    # Lấy tất cả các fields của model 'event.registration.answer'
    fields = models.execute_kw(
        db, uid, password,
        'event.registration.answer', 'fields_get',
        [],
        {'attributes': ['string', 'type', 'help', 'id']}
    )
    print("\nTất cả các fields của event.registration.answer:")
    for field_name, field_info in fields.items():
        print(f"Field: {field_name}")
        print(f"  Type: {field_info['type']}")
        print(f"  String: {field_info['string']}")
        print(f"  Help: {field_info.get('help', 'No help available')}")
        print()

    # Lấy tất cả các fields của model 'event.registration'
    reg_fields = models.execute_kw(
        db, uid, password,
        'event.registration', 'fields_get',
        [],
        {'attributes': ['string', 'type', 'help', 'id']}
    )
    print("\nTất cả các fields của event.registration:")
    for field_name, field_info in reg_fields.items():
        print(f"Field: {field_name}")
        print(f"  Type: {field_info['type']}")
        print(f"  String: {field_info['string']}")
        print(f"  Help: {field_info.get('help', 'No help available')}")
        print()

    # Lấy id của model event.registration.answer
    model_id = models.execute_kw(
        db, uid, password,
        'ir.model', 'search_read',
        [[('model', '=', 'event.registration.answer')]],
        {'fields': ['id'], 'limit': 1}
    )
    model_id = model_id[0]['id'] if model_id else None

    for field_name, field_info in fields.items():
        print(f"Field: {field_name}")
        print(f"  Type: {field_info['type']}")
        print(f"  String: {field_info['string']}")
        print(f"  Help: {field_info.get('help', 'No help available')}")
        # Lấy id của field từ ir.model.fields
        field_id = None
        if model_id:
            field_search = models.execute_kw(
                db, uid, password,
                'ir.model.fields', 'search_read',
                [[('model_id', '=', model_id), ('name', '=', field_name)]],
                {'fields': ['id', 'relation'], 'limit': 1}
            )
            if field_search:
                field_id = field_search[0]['id']
        print(f"  Field ID: {field_id}")
        # Nếu là many2one thì lấy model liên kết
        if field_info['type'] == 'many2one' and field_search:
            relation_model = field_search[0].get('relation')
            print(f"  Related Model: {relation_model}")
        print()

    # Lấy tất cả các giá trị của event.registration có id = 30
    registration_vals = models.execute_kw(
        db, uid, password,
        'event.registration', 'read',
        [ [30] ],  # id = 30
        {'fields': []}  # Để trống sẽ lấy tất cả các trường
    )
    print("\nGiá trị của event.registration có id = 30:")
    for reg in registration_vals:
        for k, v in reg.items():
            print(f"{k}: {v}")
        print()

    # Lấy tất cả các giá trị của event.event có id = 7
    event_vals = models.execute_kw(
        db, uid, password,
        'event.event', 'read',
        [[7]],  # id = 7
        {'fields': []}  # Để trống sẽ lấy tất cả các trường
    )
    print("\nGiá trị của event.event có id = 7:")
    for event in event_vals:
        for k, v in event.items():
            print(f"{k}: {v}")
        print()

    # In chi tiết thông tin của các event.question có id là specific_question_ids
    # Lấy specific_question_ids từ event_vals ở trên (giả sử trường là 'question_ids')
    specific_question_ids = []
    if event_vals and isinstance(event_vals, list):
        event_obj = event_vals[0]
        # Thử lấy các trường có thể chứa id câu hỏi
        if 'question_ids' in event_obj:
            # Odoo trả về dạng [(6, 0, [id1, id2,...])] hoặc [id1, id2,...]
            qids = event_obj['question_ids']
            if isinstance(qids, list):
                # Nếu là list các id
                if all(isinstance(i, int) for i in qids):
                    specific_question_ids = qids
                # Nếu là list các tuple (Odoo kiểu old)
                elif qids and isinstance(qids[0], (tuple, list)):
                    for tup in qids:
                        if isinstance(tup, (tuple, list)) and len(tup) == 3 and isinstance(tup[2], list):
                            specific_question_ids.extend(tup[2])
        # Nếu có trường khác chứa id câu hỏi thì bổ sung xử lý ở đây

    if specific_question_ids:
        question_vals = models.execute_kw(
            db, uid, password,
            'event.question', 'read',
            [specific_question_ids],
            {'fields': []}  # Lấy tất cả các trường
        )
        print(f"\nChi tiết các event.question có id = {specific_question_ids}:")
        for q in question_vals:
            for k, v in q.items():
                print(f"{k}: {v}")
            print()
    else:
        print("\nKhông tìm thấy specific_question_ids trong event.event!")
    
else:
    print("Authentication failed!")

# Script đăng ký tham gia event với id=7
if uid and specific_question_ids:
    # Lấy thông tin các câu hỏi (bao gồm cả loại câu hỏi)
    question_vals = models.execute_kw(
        db, uid, password,
        'event.question', 'read',
        [specific_question_ids],
        {'fields': ['id', 'title', 'question_type']}
    )

    # Thông tin đăng ký
    registration_data = {
        'name': 'Nguyen duc Anh',
        'email': 'ducanhvna@outlook.com',
        'phone': '0123456789',
        'pet': 'Bi',
    }

    # Tạo event.registration
    registration_vals = {
        'event_id': 7,
        'name': registration_data['name'],
        'email': registration_data['email'],
        'phone': registration_data['phone'],
    }
    reg_id = models.execute_kw(
        db, uid, password,
        'event.registration', 'create',
        [registration_vals]
    )
    print(f"\nĐã tạo event.registration với id = {reg_id}")

    # Chỉ sử dụng field value_text_box cho câu trả lời
    for q in question_vals:
        qid = q['id']
        title = q.get('title', '').strip().lower()
        answer = None
        for key, val in registration_data.items():
            if key in title:
                answer = val
                break
        if answer is None:
            continue

        answer_vals = {
            'registration_id': reg_id,
            'question_id': qid,
            'value_text_box': answer,
        }
        ans_id = models.execute_kw(
            db, uid, password,
            'event.registration.answer', 'create',
            [answer_vals]
        )
        print(f"Đã tạo event.registration.answer cho question_id={qid} với id = {ans_id}")

