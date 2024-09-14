from fastapi import APIRouter, HTTPException, Request
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
    try:
        data = await request.json()
        authorization_code = data.get("code")

        if not authorization_code:
            raise HTTPException(status_code=400, detail="Authorization code is missing")

        # 로그 추가: 인가 코드 출력
        print(f"Authorization Code: {authorization_code}")

        token_url = "https://kauth.kakao.com/oauth/token"
        params = {
            "grant_type": "authorization_code",
            "client_id": kakao_restapi_key,
            "redirect_uri": kakao_redirect_url,
            "code": authorization_code
        }

        response = requests.post(token_url, data=params)

        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            if not access_token:
                raise HTTPException(status_code=500, detail="Failed to retrieve access token")
            return {"access_token": access_token}
        else:
            error_details = response.json()
            raise HTTPException(status_code=response.status_code, detail=f"Failed to get access token: {error_details}")

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


