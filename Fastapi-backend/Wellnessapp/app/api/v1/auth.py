from fastapi import APIRouter, Request
import requests
from dotenv import load_dotenv
import os

router = APIRouter()

# Load environment variables
load_dotenv()

# Get kakao credentials from environment variables
kakao_restapi_key = os.getenv("KAKAO_RESTAPI_KEY")
kakao_redirect_url = os.getenv("KAKAO_REDIRECT_URL")

@router.post("/code/kakao")
async def get_kakao_token(request: Request):
    data = await request.json()
    authorization_code = data.get("code")

    # 카카오로 액세스 토큰 요청
    token_url = "https://kauth.kakao.com/oauth/token"
    params = {
        "grant_type": "authorization_code",
        "client_id": kakao_restapi_key,  # 카카오 REST API 키
        "redirect_uri": kakao_redirect_url,  # FastAPI 리디렉션 URI
        "code": authorization_code
    }

    response = requests.post(token_url, data=params)
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data["access_token"]
        return {"access_token": access_token}
    else:
        return {"error": "Failed to get access token", "details": response.json()}