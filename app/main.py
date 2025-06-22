from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.routers import blog_router

app = FastAPI(
    title="Blog Review API",
    description="네이버 블로그 검색을 통한 리뷰 분석 API",
    version="1.0.0",
)

# 라우터 등록
app.include_router(blog_router.router)

# 정적 파일 서빙을 위한 설정
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def get_index():
    return FileResponse("static/index.html")
