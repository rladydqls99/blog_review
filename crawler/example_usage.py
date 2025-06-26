"""
크롤러 사용 예시

새로운 크롤링 구조의 사용법을 보여주는 예시 파일입니다.
"""

import logging
from naver_blog_crawler import NaverBlogCrawler
from selenium_crawler import SeleniumCrawler


def naver_blog_example():
    """네이버 블로그 크롤링 예시"""
    print("=== 네이버 블로그 크롤링 예시 ===")

    # 컨텍스트 매니저를 사용한 안전한 크롤링
    with NaverBlogCrawler(headless=False) as crawler:
        url = "https://blog.naver.com/yjjuuuu/223868908998"
        result = crawler.get_blog_content(url)

        if "error" in result:
            print(f"크롤링 실패: {result['error']}")
        else:
            print(f"제목: {result['title']}")
            print(f"작성자: {result['author']}")
            print(f"작성일: {result['date']}")
            print(f"iframe 사용됨: {result['iframe_used']}")
            print(f"내용 길이: {len(result['content'])}자")
            print(f"내용 미리보기: {result['content'][:200]}...")


def basic_crawler_example():
    """기본 크롤러 사용 예시"""
    print("\n=== 기본 크롤러 사용 예시 ===")

    with SeleniumCrawler(headless=False) as crawler:
        # 일반 웹페이지 크롤링
        url = "https://www.naver.com"
        success = crawler.get_page(url)

        if success:
            # 타이틀 추출
            title_element = crawler.find_element_safe("tag name", "title")
            if title_element:
                title = crawler.extract_text(title_element)
                print(f"페이지 제목: {title}")

            # 검색창 찾기
            search_elements = crawler.find_elements_safe(
                "css selector", "input[type='text']"
            )
            print(f"검색 입력창 개수: {len(search_elements)}")
        else:
            print("페이지 로딩 실패")


def main():
    """메인 실행 함수"""
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        # 네이버 블로그 크롤링 실행
        naver_blog_example()

        # 기본 크롤러 실행
        basic_crawler_example()

    except Exception as e:
        print(f"실행 중 오류 발생: {str(e)}")


if __name__ == "__main__":
    main()
