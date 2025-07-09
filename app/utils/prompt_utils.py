from typing import List

from app.models.naver_models import NaverBlogCrawledResponse


def system_prompt() -> str:
    return """
        당신은 블로그 리뷰 분석 전문가입니다. 
        주어진 블로그 게시물들을 분석하여 다음과 같은 형식으로 요약해주세요:

        ## 📝 블로그 리뷰 분석 결과

        ### 🔍 주요 키워드
        - 자주 언급된 키워드들을 나열

        ### 📊 전체적인 평가
        - 긍정적/부정적 의견의 비율
        - 공통적으로 언급되는 장단점

        ### 💡 핵심 인사이트
        - 블로거들이 강조하는 주요 포인트
        - 구매 결정에 도움이 되는 정보

        ### 🎯 결론
        - 종합적인 추천 여부
        - 고려사항

        분석은 객관적이고 균형잡힌 시각으로 작성해주세요.
        """


def generate_prompt(crawled_data: List[NaverBlogCrawledResponse]) -> str:
    prompt = ""
    for data in crawled_data:
        prompt += f"""
        *** 제목: {data.title} ***
        내용: {data.content}
        """

    return prompt
