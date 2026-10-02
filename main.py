import os
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, String, Integer, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session

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

# สร้างตารางอัตโนมัติหากยังไม่มี
Base.metadata.create_all(bind=engine)

# Dependency สำหรับจัดการ Database Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(request, "settings/company.html", {"active_menu": "dashboard"})

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