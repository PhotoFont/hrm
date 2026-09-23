from fastapi import FastAPI, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI(title="PeopleOne Clone - HRM System")

# เปิดใช้งาน Session สำหรับระบบ Login
app.add_middleware(SessionMiddleware, secret_key="peopleone-secret-key-change-it")

# ฐานข้อมูลจำลอง (สามารถปรับเปลี่ยนหรือเชื่อมต่อ PostgreSQL/SQLite ภายหลังได้)
DATABASE = {
    "employees": [
        {"id": 1, "code": "EMP001", "name": "สมชาย ใจดี", "department": "IT & Infrastructure", "position": "Senior Systems Admin", "salary": 55000, "status": "ทำงานอยู่"},
        {"id": 2, "code": "EMP002", "name": "สมหญิง รักงาน", "department": "Human Resources", "position": "HR Manager", "salary": 45000, "status": "ทำงานอยู่"},
        {"id": 3, "code": "EMP003", "name": "กิตติ ล้วนศิริ", "department": "Development", "position": "Full Stack Developer", "salary": 50000, "status": "ทำงานอยู่"}
    ],
    "leaves": [
        {"id": 1, "code": "EMP001", "name": "สมชาย ใจดี", "type": "ลาป่วย", "start": "2026-06-10", "end": "2026-06-10", "status": "อนุมัติแล้ว"},
        {"id": 2, "code": "EMP003", "name": "กิตติ ล้วนศิริ", "type": "ลากิจธุระอันจำเป็น", "start": "2026-06-15", "end": "2026-06-16", "status": "รออนุมัติ"}
    ]
}

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request, error: str = None):
    error_html = f'<div class="mb-4 p-3 bg-red-50 text-red-600 border border-red-200 rounded-xl text-sm font-medium">{error}</div>' if error else ''
    return f"""
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
        <title>Login - PeopleOne</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>body {{ font-family: 'Plus Jakarta Sans', sans-serif; }}</style>
    </head>
    <body class="bg-slate-900 flex items-center justify-center h-screen">
        <div class="bg-white p-8 rounded-3xl shadow-2xl w-full max-w-md border border-slate-100">
            <div class="text-center mb-8">
                <div class="inline-flex items-center justify-center bg-blue-600 text-white font-bold text-2xl w-14 h-14 rounded-2xl shadow-lg shadow-blue-500/30 mb-3">P</div>
                <h1 class="text-2xl font-extrabold text-slate-900">PeopleOne</h1>
                <p class="text-sm text-slate-500 mt-1">แพลตฟอร์มบริหารงานบุคคลครบวงจร</p>
            </div>
            {error_html}
            <form action="/login" method="POST" class="space-y-5">
                <div>
                    <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">ชื่อผู้ใช้งาน (Username)</label>
                    <input type="text" name="username" required class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 text-sm focus:bg-white focus:ring-2 focus:ring-blue-600 focus:outline-none transition" placeholder="admin">
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">รหัสผ่าน (Password)</label>
                    <input type="password" name="password" required class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 text-sm focus:bg-white focus:ring-2 focus:ring-blue-600 focus:outline-none transition" placeholder="12345678">
                </div>
                <button type="submit" class="w-full bg-blue-600 text-white py-3 rounded-xl font-bold text-sm hover:bg-blue-700 shadow-lg shadow-blue-600/30 transition">เข้าสู่ระบบ</button>
            </form>
            <div class="mt-8 text-center text-xs text-slate-400 font-medium">
                ลืมรหัสผ่าน กรุณาติดต่อผู้ดูแลระบบขององค์กร
            </div>
        </div>
    </body>
    </html>
    """

@app.post("/login")
def login_action(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == "admin" and password == "12345678":
        request.session["user"] = username
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse(url="/login?error=ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้อง", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    total_emp = len(DATABASE["employees"])
    total_pending_leave = len([l for l in DATABASE["leaves"] if l["status"] == "รออนุมัติ"])
    total_salary = sum([e["salary"] for e in DATABASE["employees"]])

    emp_rows = "".join([f"""
        <tr class="hover:bg-slate-50/80 transition">
            <td class="py-4 px-6 font-semibold text-slate-900">{e['code']}</td>
            <td class="py-4 px-6 text-slate-800 font-medium">{e['name']}</td>
            <td class="py-4 px-6 text-slate-600">{e['department']}</td>
            <td class="py-4 px-6 text-slate-600">{e['position']}</td>
            <td class="py-4 px-6 text-slate-800 font-bold">{e['salary']:,} ฿</td>
            <td class="py-4 px-6"><span class="px-3 py-1 bg-emerald-50 text-emerald-600 border border-emerald-200/60 rounded-full text-xs font-bold">{e['status']}</span></td>
        </tr>
    """ for e in DATABASE["employees"]])

    leave_rows = "".join([f"""
        <tr class="hover:bg-slate-50/80 transition">
            <td class="py-4 px-6 font-semibold text-slate-900">{l['name']}</td>
            <td class="py-4 px-6 text-slate-800 font-medium">{l['type']}</td>
            <td class="py-4 px-6 text-slate-600 text-sm">{l['start']} ถึง {l['end']}</td>
            <td class="py-4 px-6">
                <span class="px-3 py-1 {'bg-amber-50 text-amber-600 border-amber-200/60' if l['status'] == 'รออนุมัติ' else 'bg-emerald-50 text-emerald-600 border-emerald-200/60'} border rounded-full text-xs font-bold">
                    {l['status']}
                </span>
            </td>
        </tr>
    """ for l in DATABASE["leaves"]])

    return f"""
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
        <title>Dashboard - PeopleOne HRM</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>body {{ font-family: 'Plus Jakarta Sans', sans-serif; }}</style>
    </head>
    <body class="bg-slate-50 text-slate-800">
        <div class="flex h-screen overflow-hidden">
            <!-- Sidebar -->
            <div class="w-64 bg-slate-900 text-white flex flex-col border-r border-slate-800">
                <div class="p-6 border-b border-slate-800 flex items-center space-x-3">
                    <div class="bg-blue-600 text-white font-bold w-10 h-10 rounded-xl flex items-center justify-center shadow-md shadow-blue-600/30">P</div>
                    <div>
                        <h2 class="font-bold text-base leading-tight">PeopleOne</h2>
                        <span class="text-xs text-slate-400 font-medium">HR Management</span>
                    </div>
                </div>
                <nav class="flex-1 p-4 space-y-1.5">
                    <a href="/dashboard" class="flex items-center px-4 py-3 bg-blue-600 rounded-xl text-white font-semibold text-sm shadow-lg shadow-blue-600/20">📊 แดชบอร์ดภาพรวม</a>
                    <a href="/logout" class="flex items-center px-4 py-3 text-red-400 hover:bg-slate-800/60 rounded-xl text-sm font-semibold transition mt-6">🚪 ออกจากระบบ</a>
                </nav>
            </div>

            <!-- Main Content Area -->
            <div class="flex-1 flex flex-col overflow-y-auto">
                <header class="bg-white border-b border-slate-200 px-8 py-5 flex justify-between items-center shadow-xs">
                    <h1 class="text-xl font-extrabold text-slate-900">แดชบอร์ดบริหารงานบุคคล</h1>
                    <div class="flex items-center space-x-3">
                        <div class="text-right">
                            <span class="text-xs text-slate-400 block font-medium">ผู้ใช้งานระบบ</span>
                            <span class="text-sm font-bold text-slate-800">{user} (Admin)</span>
                        </div>
                    </div>
                </header>

                <main class="p-8 space-y-8">
                    <!-- Stats Grid -->
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div class="bg-white p-6 rounded-2xl shadow-xs border border-slate-200/80">
                            <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">พนักงานทั้งหมด</p>
                            <p class="text-3xl font-extrabold text-blue-600 mt-2">{total_emp} <span class="text-sm font-normal text-slate-500">คน</span></p>
                        </div>
                        <div class="bg-white p-6 rounded-2xl shadow-xs border border-slate-200/80">
                            <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">คำขอลาที่รออนุมัติ</p>
                            <p class="text-3xl font-extrabold text-amber-500 mt-2">{total_pending_leave} <span class="text-sm font-normal text-slate-500">รายการ</span></p>
                        </div>
                        <div class="bg-white p-6 rounded-2xl shadow-xs border border-slate-200/80">
                            <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">งบประมาณเงินเดือนรวม</p>
                            <p class="text-3xl font-extrabold text-emerald-600 mt-2">{total_salary:,.0f} <span class="text-sm font-normal text-slate-500">บาท</span></p>
                        </div>
                    </div>

                    <!-- Employees Table -->
                    <div class="bg-white rounded-2xl shadow-xs border border-slate-200/80 overflow-hidden">
                        <div class="px-6 py-5 border-b border-slate-200 flex justify-between items-center">
                            <h2 class="font-bold text-slate-900 text-lg">📋 รายชื่อบุคลากรในองค์กร</h2>
                        </div>
                        <div class="overflow-x-auto">
                            <table class="w-full text-left border-collapse text-sm">
                                <thead>
                                    <tr class="bg-slate-50/75 text-slate-400 font-bold uppercase text-xs tracking-wider border-b border-slate-200">
                                        <th class="py-3 px-6">รหัสพนักงาน</th>
                                        <th class="py-3 px-6">ชื่อ-นามสกุล</th>
                                        <th class="py-3 px-6">แผนก</th>
                                        <th class="py-3 px-6">ตำแหน่ง</th>
                                        <th class="py-3 px-6">เงินเดือน</th>
                                        <th class="py-3 px-6">สถานะ</th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y divide-slate-100">
                                    {emp_rows}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <!-- Leave Requests Table -->
                    <div class="bg-white rounded-2xl shadow-xs border border-slate-200/80 overflow-hidden">
                        <div class="px-6 py-5 border-b border-slate-200">
                            <h2 class="font-bold text-slate-900 text-lg">🏖️ ประวัติและคำขออนุมัติการลา</h2>
                        </div>
                        <div class="overflow-x-auto">
                            <table class="w-full text-left border-collapse text-sm">
                                <thead>
                                    <tr class="bg-slate-50/75 text-slate-400 font-bold uppercase text-xs tracking-wider border-b border-slate-200">
                                        <th class="py-3 px-6">พนักงาน</th>
                                        <th class="py-3 px-6">ประเภทการลา</th>
                                        <th class="py-3 px-6">ช่วงวันที่</th>
                                        <th class="py-3 px-6">สถานะ</th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y divide-slate-100">
                                    {leave_rows}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </main>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/")
def index():
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)