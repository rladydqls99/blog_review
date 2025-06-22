"""
네이버 블로그 검색 API 테스트

이 파일은 구현한 네이버 블로그 검색 기능을 테스트합니다.
FastAPI 서버를 실행한 후 API 엔드포인트를 호출하여 결과를 확인할 수 있습니다.
"""

import asyncio
import httpx


async def test_blog_search():
    """블로그 검색 API 테스트"""
    base_url = "http://localhost:8000"

    test_params = {"query": "대전 공주칼국수", "display": 5, "start": 1, "sort": "sim"}

    try:
        async with httpx.AsyncClient() as client:
            print("📡 네이버 블로그 검색 API 테스트 시작...")
            print(f"🔍 검색어: {test_params['query']}")
            print(f"📄 표시 개수: {test_params['display']}")
            print("-" * 50)

            response = await client.get(
                f"{base_url}/api/blog/search", params=test_params, timeout=30.0
            )

            if response.status_code == 200:
                result = response.json()

                print("✅ API 호출 성공!")
                print(f"📊 총 검색 결과: {result['total']}개")
                print(f"📋 현재 페이지 결과: {len(result['items'])}개")
                print("-" * 50)

                for i, item in enumerate(result["items"], 1):
                    print(f"[{i}] {item['title']}")
                    print(f"    📝 블로그: {item['blog_name']}")
                    print(f"    🔗 링크: {item['link']}")
                    print(f"    📅 작성일: {item['post_date']}")
                    description = item["description"][:100]
                    print(f"    💭 요약: {description}...")
                    print()

            else:
                print(f"❌ API 호출 실패: {response.status_code}")
                print(f"오류 내용: {response.text}")

    except httpx.ConnectError:
        print("❌ 서버 연결 실패!")
        print("💡 FastAPI 서버가 실행 중인지 확인해주세요:")
        print("   uvicorn app.main:app --reload")

    except Exception as e:
        print(f"❌ 예상치 못한 오류: {str(e)}")


async def main():
    """메인 테스트 함수"""
    print("🚀 네이버 블로그 검색 API 테스트 시작")
    print("=" * 60)

    await test_blog_search()

    print("=" * 60)
    print("🏁 테스트 완료")


if __name__ == "__main__":
    asyncio.run(main())
