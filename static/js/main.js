const blogReviewApp = (() => {
  const container = document.querySelector(".container");
  const searchInput = document.getElementById("searchInput");
  const searchButton = document.getElementById("searchButton");
  const resultText = document.getElementById("resultText");

  // textarea 자동 크기 조정 함수
  const autoResizeTextarea = (textarea) => {
    textarea.style.height = "auto";
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + "px";
  };

  const handleSearch = async () => {
    const searchQuery = searchInput.value.trim();

    if (!searchQuery) {
      alert("검색어를 입력해주세요.");
      return;
    }

    container.classList.add("loading");
    searchButton.disabled = true;
    searchInput.disabled = true;
    searchButton.innerHTML = `
      <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="3" opacity="0.5"/>
        <path d="M12 1v6m0 6v6m11-7h-6m-6 0H1" opacity="0.3"/>
      </svg>
    `;

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
      resultText.innerHTML = data;
      container.classList.add("success");
    } catch (error) {
      console.error("검색 중 오류 발생:", error);
      alert("검색 중 오류가 발생했습니다. 다시 시도해주세요.");
    } finally {
      container.classList.remove("loading");
      searchInput.disabled = false;
      searchInput.value = "";
      searchButton.disabled = false;
      searchButton.innerHTML = `
        <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16z"/>
          <path d="M21 21l-4.35-4.35"/>
        </svg>
      `;
    }
  };

  const bindEvent = () => {
    searchButton.addEventListener("click", handleSearch);

    // textarea 자동 크기 조정 이벤트
    searchInput.addEventListener("input", () => {
      autoResizeTextarea(searchInput);
    });

    searchInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSearch();
      }
    });

    // 초기 크기 설정
    autoResizeTextarea(searchInput);
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
