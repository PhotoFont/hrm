from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Human and Resource")

# กำหนดโฟลเดอร์สำหรับเก็บไฟล์ HTML Templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    # ส่งข้อมูลจำลองสำหรับแสดงชื่อองค์กรหรือผู้ใช้งานบนหน้าเว็บ
    context = {
        "request": request,
        "company_name": "บริษัท ตัวอย่าง จำกัด (องค์กรทดลอง)"
    }
    return templates.TemplateResponse(request, "index.html", context)