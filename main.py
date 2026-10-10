import os
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, Text

app = FastAPI(title="Human and Resource")
templates = Jinja2Templates(directory="templates")

# กำหนดโฟลเดอร์สำหรับเก็บฐานข้อมูลถาวร (ป้องกันข้อมูลหายเวลา Redeploy)
DATA_DIR = "/app/data"
os.makedirs(DATA_DIR, exist_ok=True)

# ระบุ path เต็มของฐานข้อมูลให้ไปเก็บอยู่ในโฟลเดอร์ data บนเซิร์ฟเวอร์
DB_FILE = os.path.join(DATA_DIR, "hrm.db")
engine = create_engine(f"sqlite:///{DB_FILE}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# โครงสร้างตารางบริษัทในฐานข้อมูล
class CompanyModel(Base):
    __tablename__ = "companies"
    
    code = Column(String, primary_key=True, index=True)
    name_th = Column(String, nullable=False)
    name_en = Column(String)
    tax_id = Column(String)
    social_fund_id = Column(String)
    branch_id = Column(String)
    address_no = Column(String)
    moo = Column(String)
    soi = Column(String)
    road = Column(String)
    subdistrict = Column(String)
    district = Column(String)
    province = Column(String)
    postal_code = Column(String)
    phone = Column(String)
    email = Column(String)
    website = Column(String)
    signatory_name = Column(String)
    signatory_position = Column(String)
    emp_code_format = Column(String)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

# --- 2. เพิ่ม Model สำหรับ Location ---
class Location(Base):
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    company_code = Column(String, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    latitude = Column(String, nullable=True)
    longitude = Column(String, nullable=True)
    radius = Column(Integer, default=150)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

# สร้างตารางอัตโนมัติหากยังไม่มี
Base.metadata.create_all(bind=engine)

# Dependency สำหรับจัดการ Database Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def dashboard():
    return RedirectResponse(url="/settings/company", status_code=302)

@app.get("/settings/company", response_class=HTMLResponse)
async def company_settings(request: Request, db: Session = Depends(get_db)):
    companies = db.query(CompanyModel).order_by(CompanyModel.display_order).all()
    
    # เพิ่มข้อมูลตั้งต้นหากฐานข้อมูลยังว่างอยู่
    if not companies:
        default_comps = [
            CompanyModel(code="DMO", name_th="บริษัท ตัวอย่าง จำกัด", tax_id="0105500000001", is_active=True, display_order=1),
            CompanyModel(code="DMF", name_th="บริษัท ตัวอย่าง แมนนูแฟคเจอร์ริ่ง จำกัด", name_en="Demo Manufacturing Co., Ltd.", tax_id="0105500000002", is_active=True, display_order=2)
        ]
        db.add_all(default_comps)
        db.commit()
        companies = db.query(CompanyModel).all()

    return templates.TemplateResponse(request, "settings/company.html", {
        "active_menu": "company_settings",
        "companies": companies
    })

@app.post("/settings/company/add")
async def add_company(
    code: str = Form(...),
    name_th: str = Form(...),
    name_en: str = Form(None),
    tax_id: str = Form(None),
    social_fund_id: str = Form(None),
    branch_id: str = Form("0000"),
    address_no: str = Form(None),
    moo: str = Form(None),
    soi: str = Form(None),
    road: str = Form(None),
    subdistrict: str = Form(None),
    district: str = Form(None),
    province: str = Form(None),
    postal_code: str = Form(None),
    phone: str = Form(None),
    email: str = Form(None),
    website: str = Form(None),
    signatory_name: str = Form(None),
    signatory_position: str = Form(None),
    emp_code_format: str = Form("{COMPANY}-{NNNN}"),
    display_order: int = Form(0),
    is_active: bool = Form(False),
    db: Session = Depends(get_db)
):
    new_company = CompanyModel(
        code=code, name_th=name_th, name_en=name_en, tax_id=tax_id,
        social_fund_id=social_fund_id, branch_id=branch_id,
        address_no=address_no, moo=moo, soi=soi, road=road,
        subdistrict=subdistrict, district=district, province=province, postal_code=postal_code,
        phone=phone, email=email, website=website,
        signatory_name=signatory_name, signatory_position=signatory_position,
        emp_code_format=emp_code_format, display_order=display_order, is_active=is_active
    )
    db.add(new_company)
    db.commit()
    return RedirectResponse(url="/settings/company", status_code=303)

@app.post("/settings/company/update")
async def update_company(
    code: str = Form(...),
    name_th: str = Form(...),
    name_en: str = Form(None),
    tax_id: str = Form(None),
    social_fund_id: str = Form(None),
    branch_id: str = Form("0000"),
    address_no: str = Form(None),
    moo: str = Form(None),
    soi: str = Form(None),
    road: str = Form(None),
    subdistrict: str = Form(None),
    district: str = Form(None),
    province: str = Form(None),
    postal_code: str = Form(None),
    phone: str = Form(None),
    email: str = Form(None),
    website: str = Form(None),
    signatory_name: str = Form(None),
    signatory_position: str = Form(None),
    emp_code_format: str = Form("{COMPANY}-{NNNN}"),
    display_order: int = Form(0),
    is_active: bool = Form(False),
    db: Session = Depends(get_db)
):
    company = db.query(CompanyModel).filter(CompanyModel.code == code).first()
    if company:
        company.name_th = name_th
        company.name_en = name_en
        company.tax_id = tax_id
        company.social_fund_id = social_fund_id
        company.branch_id = branch_id
        company.address_no = address_no
        company.moo = moo
        company.soi = soi
        company.road = road
        company.subdistrict = subdistrict
        company.district = district
        company.province = province
        company.postal_code = postal_code
        company.phone = phone
        company.email = email
        company.website = website
        company.signatory_name = signatory_name
        company.signatory_position = signatory_position
        company.emp_code_format = emp_code_format
        company.display_order = display_order
        company.is_active = is_active
        db.commit()
    return RedirectResponse(url="/settings/company", status_code=303)

@app.get("/settings/company/delete/{code}")
async def delete_company(code: str, db: Session = Depends(get_db)):
    company = db.query(CompanyModel).filter(CompanyModel.code == code).first()
    if company:
        db.delete(company)
        db.commit()
    return RedirectResponse(url="/settings/company", status_code=303)

@app.get("/settings/locations", response_class=HTMLResponse)
async def list_locations(
    request: Request,
    db: Session = Depends(get_db)
):
    locations = (
        db.query(Location)
        .order_by(Location.display_order.asc())
        .all()
    )

    companies = (
        db.query(CompanyModel)
        .filter(CompanyModel.is_active == True)
        .order_by(CompanyModel.display_order.asc())
        .all()
    )

    return templates.TemplateResponse(
        request,
        "settings/locations.html",
        {
            "active_menu": "locations",
            "locations": locations,
            "companies": companies,
        }
    )

@app.post("/settings/locations/add")
async def add_location(
    company_code: str = Form(...),
    code: str = Form(...),
    name: str = Form(...),
    phone: str = Form(None),
    address: str = Form(None),
    latitude: str = Form(None),
    longitude: str = Form(None),
    radius: int = Form(50),
    display_order: int = Form(0),
    is_active: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):

    exists = (
        db.query(Location)
        .filter(Location.code == code)
        .first()
    )

    if exists:
        return RedirectResponse(
            url="/settings/locations",
            status_code=303
        )

    loc = Location(
        company_code=company_code,
        code=code,
        name=name,
        phone=phone,
        address=address,
        latitude=latitude,
        longitude=longitude,
        radius=radius,
        display_order=display_order,
        is_active=bool(is_active)
    )

    db.add(loc)
    db.commit()

    return RedirectResponse(
        url="/settings/locations",
        status_code=303
    )

@app.post("/settings/locations/update/{location_id}")
async def update_location(
    location_id: int,
    company_code: str = Form(...),
    code: str = Form(...),
    name: str = Form(...),
    address: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    display_order: int = Form(0),
    latitude: Optional[str] = Form(None),
    longitude: Optional[str] = Form(None),
    radius: int = Form(150),
    is_active: bool = Form(False),
    db: Session = Depends(get_db)
):
    location = db.query(Location).filter(Location.id == location_id).first()
    if location:
        location.company_code = company_code
        location.code = code
        location.name = name
        location.address = address
        location.phone = phone
        location.display_order = display_order
        location.latitude = latitude
        location.longitude = longitude
        location.radius = radius
        location.is_active = is_active
        db.commit()

    return RedirectResponse(url="/settings/locations", status_code=303)

@app.get("/settings/locations/delete/{location_id}")
async def delete_location(
    location_id: int,
    db: Session = Depends(get_db)
):
    location = (
        db.query(Location)
        .filter(Location.id == location_id)
        .first()
    )

    if location:
        db.delete(location)
        db.commit()

    return RedirectResponse(
        url="/settings/locations",
        status_code=303
    )

# --- เพิ่ม Model สำหรับ Department (ฝ่าย / แผนก) ---
class DepartmentModel(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    company_code = Column(String, index=True, nullable=False)
    parent_id = Column(Integer, nullable=True)  # สำหรับรองรับโครงสร้างหลายชั้น (สังกัดภายใน)
    cost_center = Column(String, nullable=True)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

# สร้างตารางอัตโนมัติ (ตารางใหม่จะถูกสร้างเพิ่มโดยไม่กระทบตารางเดิม)
Base.metadata.create_all(bind=engine)

@app.get("/settings/departments", response_class=HTMLResponse)
async def list_departments(
    request: Request,
    db: Session = Depends(get_db)
):
    departments = db.query(DepartmentModel).order_by(DepartmentModel.display_order.asc()).all()
    companies = db.query(CompanyModel).filter(CompanyModel.is_active == True).order_by(CompanyModel.display_order.asc()).all()
    
    return templates.TemplateResponse(
        request,
        "settings/departments.html",
        {
            "active_menu": "departments",
            "departments": departments,
            "companies": companies,
        }
    )

@app.post("/settings/departments/add")
async def add_department(
    company_code: str = Form(...),
    code: str = Form(...),
    name: str = Form(...),
    parent_id: Optional[int] = Form(None),
    cost_center: Optional[str] = Form(None),
    display_order: int = Form(0),
    is_active: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    exists = db.query(DepartmentModel).filter(DepartmentModel.code == code).first()
    if not exists:
        dept = DepartmentModel(
            company_code=company_code,
            code=code,
            name=name,
            parent_id=parent_id if parent_id else None,
            cost_center=cost_center,
            display_order=display_order,
            is_active=bool(is_active)
        )
        db.add(dept)
        db.commit()
    return RedirectResponse(url="/settings/departments", status_code=303)

@app.post("/settings/departments/update/{dept_id}")
async def update_department(
    dept_id: int,
    company_code: str = Form(...),
    code: str = Form(...),
    name: str = Form(...),
    parent_id: Optional[int] = Form(None),
    cost_center: Optional[str] = Form(None),
    display_order: int = Form(0),
    is_active: bool = Form(False),
    db: Session = Depends(get_db)
):
    dept = db.query(DepartmentModel).filter(DepartmentModel.id == dept_id).first()
    if dept:
        dept.company_code = company_code
        dept.code = code
        dept.name = name
        dept.parent_id = parent_id if parent_id else None
        dept.cost_center = cost_center
        dept.display_order = display_order
        dept.is_active = is_active
        db.commit()
    return RedirectResponse(url="/settings/departments", status_code=303)

@app.get("/settings/departments/delete/{dept_id}")
async def delete_department(
    dept_id: int,
    db: Session = Depends(get_db)
):
    dept = db.query(DepartmentModel).filter(DepartmentModel.id == dept_id).first()
    if dept:
        db.delete(dept)
        db.commit()
    return RedirectResponse(url="/settings/departments", status_code=303)

# --- เพิ่ม Model สำหรับ Position (ตำแหน่งงาน) ---
class PositionModel(Base):
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    department_id = Column(Integer, nullable=True)  # สังกัดแผนก
    level = Column(String, default="1")            # ระดับ
    display_order = Column(Integer, default=0)
    responsibility = Column(Text, nullable=True)     # หน้าที่ความรับผิดชอบ
    is_active = Column(Boolean, default=True)

# สร้างตารางอัตโนมัติ (ไม่กระทบตารางเดิม)
Base.metadata.create_all(bind=engine)

@app.get("/settings/positions", response_class=HTMLResponse)
async def list_positions(
    request: Request,
    db: Session = Depends(get_db)
):
    positions = db.query(PositionModel).order_by(PositionModel.display_order.asc()).all()
    departments = db.query(DepartmentModel).order_by(DepartmentModel.display_order.asc()).all()
    
    return templates.TemplateResponse(
        request,
        "settings/positions.html",
        {
            "active_menu": "positions",
            "positions": positions,
            "departments": departments,
        }
    )

@app.post("/settings/positions/add")
async def add_position(
    code: str = Form(...),
    name: str = Form(...),
    department_id: Optional[int] = Form(None),
    level: str = Form("1"),
    display_order: int = Form(0),
    responsibility: Optional[str] = Form(None),
    is_active: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    exists = db.query(PositionModel).filter(PositionModel.code == code).first()
    if not exists:
        pos = PositionModel(
            code=code,
            name=name,
            department_id=department_id if department_id else None,
            level=level,
            display_order=display_order,
            responsibility=responsibility,
            is_active=bool(is_active)
        )
        db.add(pos)
        db.commit()
    return RedirectResponse(url="/settings/positions", status_code=303)

@app.post("/settings/positions/update/{pos_id}")
async def update_position(
    pos_id: int,
    code: str = Form(...),
    name: str = Form(...),
    department_id: Optional[int] = Form(None),
    level: str = Form("1"),
    display_order: int = Form(0),
    responsibility: Optional[str] = Form(None),
    is_active: bool = Form(False),
    db: Session = Depends(get_db)
):
    pos = db.query(PositionModel).filter(PositionModel.id == pos_id).first()
    if pos:
        pos.code = code
        pos.name = name
        pos.department_id = department_id if department_id else None
        pos.level = level
        pos.display_order = display_order
        pos.responsibility = responsibility
        pos.is_active = is_active
        db.commit()
    return RedirectResponse(url="/settings/positions", status_code=303)

@app.get("/settings/positions/delete/{pos_id}")
async def delete_position(
    pos_id: int,
    db: Session = Depends(get_db)
):
    pos = db.query(PositionModel).filter(PositionModel.id == pos_id).first()
    if pos:
        db.delete(pos)
        db.commit()
    return RedirectResponse(url="/settings/positions", status_code=303)

# --- เพิ่ม Model สำหรับ Employee (ทะเบียนพนักงาน) ---
class EmployeeModel(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    emp_code = Column(String, unique=True, index=True, nullable=False) # รหัสพนักงาน เช่น 01-0001
    prefix = Column(String, nullable=True)     # คำนำหน้า
    first_name = Column(String, nullable=False) # ชื่อ
    last_name = Column(String, nullable=False)  # นามสกุล
    nickname = Column(String, nullable=True)    # ชื่อเล่น
    first_name_en = Column(String, nullable=True)
    last_name_en = Column(String, nullable=True)
    id_card = Column(String, nullable=True)     # เลขบัตรประชาชน
    birth_date = Column(String, nullable=True)  # วันเกิด
    gender = Column(String, nullable=True)      # เพศ
    marital_status = Column(String, nullable=True) # สถานภาพสมรส
    nationality = Column(String, default="ไทย") # สัญชาติ
    blood_type = Column(String, nullable=True)  # กรุ๊ปเลือด
    military_status = Column(String, nullable=True) # สถานะทางทหาร
    phone = Column(String, nullable=True)       # โทรศัพท์
    email = Column(String, nullable=True)       # อีเมล
    line_id = Column(String, nullable=True)     # LINE ID
    
    # ข้อมูลการจ้างงาน
    position_id = Column(Integer, nullable=True) # ตำแหน่ง
    department_id = Column(Integer, nullable=True) # แผนก
    start_date = Column(String, nullable=True)   # วันเริ่มงาน
    employment_status = Column(String, default="probation") # probation (ทดลองงาน), normal (ปกติ), resigned (พ้นสภาพ)

# สร้างตารางอัตโนมัติ (ไม่กระทบตารางเดิม)
Base.metadata.create_all(bind=engine)

@app.get("/employees", response_class=HTMLResponse)
async def list_employees(
    request: Request,
    db: Session = Depends(get_db)
):
    employees = db.query(EmployeeModel).all()
    departments = db.query(DepartmentModel).all()
    positions = db.query(PositionModel).all()
    
    # แปลงเป็น Dictionary เพื่อให้ HTML เรียกใช้งานง่ายและปลอดภัยจาก Error
    dept_dict = {d.id: d.name for d in departments}
    pos_dict = {p.id: p.name for p in positions}
    
    total_emp = len(employees)
    probation_emp = sum(1 for e in employees if e.employment_status == 'probation')
    normal_emp = sum(1 for e in employees if e.employment_status == 'normal')
    resigned_emp = sum(1 for e in employees if e.employment_status == 'resigned')
    
    return templates.TemplateResponse(
        request,
        "employees/index.html",
        {
            "active_menu": "employees",
            "employees": employees,
            "dept_dict": dept_dict,
            "pos_dict": pos_dict,
            "total_emp": total_emp,
            "probation_emp": probation_emp,
            "normal_emp": normal_emp,
            "resigned_emp": resigned_emp
        }
    )

@app.post("/employees/add")
async def add_employee(
    emp_code: Optional[str] = Form(None),
    prefix: Optional[str] = Form(None),
    first_name: str = Form(...),
    last_name: str = Form(...),
    nickname: Optional[str] = Form(None),
    first_name_en: Optional[str] = Form(None),
    last_name_en: Optional[str] = Form(None),
    id_card: Optional[str] = Form(None),
    birth_date: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),
    marital_status: Optional[str] = Form(None),
    nationality: Optional[str] = Form("ไทย"),
    blood_type: Optional[str] = Form(None),
    military_status: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    line_id: Optional[str] = Form(None),
    position_id: Optional[int] = Form(None),
    department_id: Optional[int] = Form(None),
    start_date: Optional[str] = Form(None),
    employment_status: Optional[str] = Form("probation"),
    db: Session = Depends(get_db)
):
    # ถ้าไม่ได้ใส่รหัสพนักงานมา ให้สร้างอัตโนมัติ
    if not emp_code or emp_code.strip() == "":
        count = db.query(EmployeeModel).count()
        emp_code = f"01-{str(count + 1).zfill(4)}"
        
    emp = EmployeeModel(
        emp_code=emp_code,
        prefix=prefix,
        first_name=first_name,
        last_name=last_name,
        nickname=nickname,
        first_name_en=first_name_en,
        last_name_en=last_name_en,
        id_card=id_card,
        birth_date=birth_date,
        gender=gender,
        marital_status=marital_status,
        nationality=nationality,
        blood_type=blood_type,
        military_status=military_status,
        phone=phone,
        email=email,
        line_id=line_id,
        position_id=position_id,
        department_id=department_id,
        start_date=start_date,
        employment_status=employment_status
    )
    db.add(emp)
    db.commit()
    return RedirectResponse(url="/employees", status_code=303)

@app.get("/employees/delete/{emp_id}")
async def delete_employee(
    emp_id: int,
    db: Session = Depends(get_db)
):
    emp = db.query(EmployeeModel).filter(EmployeeModel.id == emp_id).first()
    if emp:
        db.delete(emp)
        db.commit()
    return RedirectResponse(url="/employees", status_code=303)


# @app.get("/version")
# async def version():
#     return {
#     "version": "2026-10-09-location-fix5"
#     }