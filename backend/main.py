import google.generativeai as genai
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
from fastapi.middleware.cors import CORSMiddleware

from config import Settings, get_settings

# 在应用启动前，先配置API并列出可用模型
settings = get_settings()
genai.configure(api_key=settings.GEMINI_API_KEY)

print("Available Models:")
for m in genai.list_models():
    print(f"Model: {m.name}, Supported: {m.supported_generation_methods}")
print("---")


app = FastAPI(
    title="Gemini Chat API",
    description="A simple API to chat with Google Gemini Pro.",
    version="0.1.0",
)

# --- CORS 配置 ---
# 允许所有来源的访问，注意这在生产环境中存在安全风险
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有 HTTP 头
)

# --- Pydantic 模型定义 ---
# 定义单条聊天消息的结构
class ChatMessage(BaseModel):
    role: str  # "user" or "model"
    content: str

# 定义聊天请求的结构
class ChatRequest(BaseModel):
    history: List[ChatMessage]
    message: str

# 定义聊天响应的结构
class ChatResponse(BaseModel):
    reply: str

# --- API 端点 ---
@app.get("/")
def read_root():
    return {"message": "Welcome to the Gemini Chat API!"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_gemini(
    request: ChatRequest, 
    settings: Settings = Depends(get_settings)
):
    try:
        # 1. 配置 Gemini API
        genai.configure(api_key=settings.GEMINI_API_KEY)

        # 2. 选择模型
        model = genai.GenerativeModel('gemini-2.5-flash')

        # 3. 格式化对话历史以符合 SDK 要求
        # SDK 要求历史记录是 [user, model, user, model,...] 的交替顺序
        # 格式为 {'role': 'user'/'model', 'parts': [text]}
        formatted_history = []
        for msg in request.history:
            formatted_history.append({
                "role": msg.role,
                "parts": [msg.content]
            })

        # 4. 将当前用户消息添加到历史记录中
        formatted_history.append({
            "role": "user",
            "parts": [request.message]
        })

        # 5. 调用 Gemini API
        # 我们直接使用 generate_content 并传入完整的历史记录
        # 这体现了我们的无状态设计
        response = model.generate_content(formatted_history)

        # 6. 返回模型的回复
        return ChatResponse(reply=response.text)

    except Exception as e:
        # 捕获任何可能的 API 错误或配置错误
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing your request.")
