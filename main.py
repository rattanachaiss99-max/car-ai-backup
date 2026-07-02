import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
import base64
# 🎯 นำเข้าตัวช่วยแปลภาษาอัจฉริยะ
from deep_translator import GoogleTranslator 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

POLLINATIONS_API_KEY = ""

class RenderInput(BaseModel):
    prompt: str
    image_base64: str

@app.post("/api/generate-car")
async def generate_car(payload: RenderInput):
    try:
        print(f"📥 [Backend] ข้อความจาก Vue วิ่งมาถึง Python แล้ว!: '{payload.prompt}'")
        
        # 🎯 อัปเดตพิเศษ: ดักจับถ้าผู้ใช้พิมพ์ภาษาไทยมา สั่งแปลเป็นอังกฤษให้ AI ทันที!
        try:
            english_prompt = GoogleTranslator(source='auto', target='en').translate(payload.prompt)
            print(f"🔤 [Translator] แปลงภาษาให้ AI เข้าใจเรียบร้อย: '{english_prompt}'")
        except Exception as translate_err:
            print(f"⚠️ แปลภาษาขัดข้อง ใช้ข้อความเดิม: {str(translate_err)}")
            english_prompt = payload.prompt

        # ผสม Prompt ให้รูปภาพรถยนต์คมชัดระดับสตูดิโอ
        enhanced_prompt = f"{english_prompt}, professional studio car photography, ultra-realistic, highly detailed, 8k"
        
        # 🎯 กลับมาใช้โครงสร้าง URL ที่ส่ง Prompt ต่อท้ายลิงก์ (แบบที่ Pollinations ชอบ)
        api_url = f"https://gen.pollinations.ai/image/{requests.utils.quote(enhanced_prompt)}"
        
        # สเปกพารามิเตอร์คุมภาพ และแนบคีย์ลิขสิทธิ์แท้ของคุณ
        params = {
            "model": "flux",  
            "width": 1024,
            "height": 512,
            "seed": 42,
            "nologo": "true",
            "key": POLLINATIONS_API_KEY
        }
        
        # ยิงขอดึงภาพจริงจากคลาวด์
        response = requests.get(api_url, params=params)
        
        if response.status_code == 200:
            encoded_image = base64.b64encode(response.content).decode('utf-8')
            ai_final_base64 = f"data:image/png;base64,{encoded_image}"
            
            print("🎉 [Backend] ท่อพรีเมียมวาดภาพสำเร็จ! ส่งผลลัพธ์กลับหน้าบ้าน Vue 3")
            return {"success": True, "ai_image_url": ai_final_base64}
        else:
            raise Exception(f"เซิร์ฟเวอร์ปฏิเสธด้วย Code: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"🚨 เกิดข้อผิดพลาดฝั่ง Python: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    import os
    # ดักจับพอร์ตที่ Render ส่งมา ถ้าไม่มีให้ใช้ 3000 เป็นค่าดีฟอลต์ในเครื่อง
    port = int(os.environ.get("PORT", 3000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
