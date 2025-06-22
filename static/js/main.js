const blogReviewApp = (() => {
  const searchInput = document.getElementById("searchInput");
  const searchButton = document.getElementById("searchButton");

  const handleSearch = async () => {
    const searchQuery = searchInput.value.trim();

    // if (!searchQuery) {
    //   alert("검색어를 입력해주세요.");
    //   return;
    // }

    try {
      const url = new URL(endPoint.search, window.location.origin);
      url.searchParams.append("query", searchQuery);

      const res = await fetch(url.toString(), {
        method: "GET",
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data = await res.json();
      console.log(data);

      // TODO: 검색 결과를 화면에 표시하는 로직 추가
    } catch (error) {
      console.error("검색 중 오류 발생:", error);
      alert("검색 중 오류가 발생했습니다. 다시 시도해주세요.");
    }
  };

  const bindEvent = () => {
    searchButton.addEventListener("click", handleSearch);
    searchInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        handleSearch();
      }
    });
  };

  const init = () => {
    bindEvent();
  };

  return {
    init,
  };
})();

blogReviewApp.init();

const endPoint = {
  search: "/api/blog/search",
};
