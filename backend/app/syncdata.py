#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from app.db import SessionLocal
from app.models.core import User, Company, UserRoleEnum
from passlib.hash import bcrypt

INIT_DATA_PATH =  'initData.json'

def sync_data():
    with open(INIT_DATA_PATH, 'r') as f:
        data = json.load(f)
    db = SessionLocal()
    # Sync superuser
    su = data.get('superuser', {})
    user = db.query(User).filter_by(email=su['email']).first()
    if not user:
        user = User(
            email=su['email'],
            hashed_password=bcrypt.hash(su['password']),
            full_name=su.get('full_name'),
            is_active=True,
            is_superuser=True,
            is_staff=True,
            role=UserRoleEnum.SUPERADMIN,
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Superuser {su['email']} created.")
    else:
        print(f"Superuser {su.get('email')} already exists.")
    # Sync main company (APEC GROUP)
    company_data = su.get('company', {})
    main_company = db.query(Company).filter_by(name=company_data.get('name')).first()
    if not main_company:
        main_company = Company(
            name=company_data.get('name'),
            owner_id=user.id,
            info={k: v for k, v in company_data.items() if k not in ['name', 'companies']}
        )
        db.add(main_company)
        db.commit()
        db.refresh(main_company)
        print(f"Main company {main_company.name} created.")
    else:
        print(f"Main company {company_data.get('name')} already exists.")
    # Sync sub-companies
    companies = company_data.get('companies', [])
    for comp in companies:
        comp_obj = db.query(Company).filter_by(name=comp['name']).first()
        if not comp_obj:
            comp_obj = Company(
                name=comp['name'],
                owner_id=user.id,  # hoặc main_company.id nếu có quan hệ cha-con
                info={k: v for k, v in comp.items() if k != 'name'}
            )
            db.add(comp_obj)
            print(f"Sub-company {comp['name']} created.")
        else:
            # Update info nếu có thay đổi
            updated = False
            for k, v in comp.items():
                if k != 'name' and (not comp_obj.info or comp_obj.info.get(k) != v):
                    if not comp_obj.info:
                        comp_obj.info = {}
                    comp_obj.info[k] = v
                    updated = True
            if updated:
                db.add(comp_obj)
                print(f"Sub-company {comp['name']} updated info.")
            else:
                print(f"Sub-company {comp['name']} already exists.")
    db.commit()
    db.close()

if __name__ == "__main__":
    sync_data()
