from uuid import uuid4
from fastapi import APIRouter, HTTPException
from app.schemas.auth import RegisterRequest, LoginRequest
from app.db.mongo import get_db, next_sequence
from app.core.security import hash_password, verify_password, create_access_token
from app.utils.permissions import default_employee_permissions

router = APIRouter()


@router.post('/register')
def register(body: RegisterRequest):
    db = get_db()
    email = body.email.lower().strip()
    if db.users.find_one({"email": email}):
        raise HTTPException(status_code=409, detail="An account with this email already exists.")

    company_id = next_sequence("companies")
    company_uuid = str(uuid4())
    company_name = (body.companyName or f"{body.fullName.strip()}'s Organization").strip()
    db.companies.insert_one({
        "id": company_id,
        "uuid": company_uuid,
        "name": company_name,
        "countryCode": body.countryCode,
        "about": body.companyAbout,
        "website": body.companyWebsite,
        "industry": body.companyIndustry,
        "phone": body.companyPhone,
        "adminUserId": None,
    })

    user_id = next_sequence("users")
    user = {
        "id": user_id,
        "companyId": company_id,
        "email": email,
        "passwordHash": hash_password(body.password),
        "fullName": body.fullName.strip(),
        "role": "admin",
        "managerId": None,
        "companyRoleId": None,
    }
    db.users.insert_one(user)
    db.companies.update_one({"id": company_id}, {"$set": {"adminUserId": user_id}})

    role_id = next_sequence("company_roles")
    db.company_roles.update_one(
        {"companyId": company_id, "name": "Employee"},
        {"$setOnInsert": {
            "id": role_id,
            "companyId": company_id,
            "name": "Employee",
            "baseRole": "employee",
            "description": None,
            "permissions": default_employee_permissions(),
        }},
        upsert=True,
    )

    token = create_access_token(user_id, "admin", company_id)
    return {"token": token, "user": {"id": user_id, "name": user["fullName"], "email": email, "role": "admin", "companyId": company_id, "companyUuid": company_uuid}}


@router.post('/login')
def login(body: LoginRequest):
    db = get_db()
    email = body.email.lower().strip()
    user = db.users.find_one({"email": email})
    if not user or not verify_password(body.password, user["passwordHash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    company = db.companies.find_one({"id": user["companyId"]})
    if not company:
        raise HTTPException(status_code=500, detail="Company record not found for this user.")

    role_doc = db.company_roles.find_one({"id": user.get("companyRoleId"), "companyId": user["companyId"]}) if user.get("companyRoleId") else None
    token = create_access_token(user["id"], user["role"], user["companyId"])
    return {
        "token": token,
        "user": {
            "id": user["id"],
            "name": user["fullName"],
            "email": user["email"],
            "role": user["role"],
            "companyId": user["companyId"],
            "companyUuid": company["uuid"],
            "company": {
                "uuid": company["uuid"],
                "name": company.get("name"),
                "countryCode": company.get("countryCode"),
                "about": company.get("about"),
                "website": company.get("website"),
                "industry": company.get("industry"),
                "phone": company.get("phone"),
            },
            "companyRole": {
                "id": role_doc["id"], "name": role_doc["name"], "baseRole": role_doc["baseRole"], "permissions": role_doc.get("permissions", {})
            } if role_doc else None,
        },
    }
