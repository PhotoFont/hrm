FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
# อัปเดต pip ให้เป็นเวอร์ชันล่าสุดก่อนติดตั้งแพ็กเกจ
RUN pip install --no-cache-dir --upgrade pip
# ติดตั้ง dependencies
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]