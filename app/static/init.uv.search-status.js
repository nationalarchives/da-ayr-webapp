const setHidden = (el, hidden) => {
  if (el) {
    el.hidden = hidden;
  }
};

const hideSearchError = () => {
  setHidden(document.getElementById("uv-search-error"), true);
};

const showSearchError = () => {
  setHidden(document.getElementById("uv-search-results"), true);
  setHidden(document.getElementById("uv-search-no-results"), true);
  setHidden(document.getElementById("uv-search-error"), false);
};

const setNavLinkState = (link, enabled) => {
  if (!link) {
    return;
  }
  if (enabled) {
    link.setAttribute("href", "#");
    link.classList.remove("uv-search-nav--disabled");
  } else {
    link.removeAttribute("href");
    link.classList.add("uv-search-nav--disabled");
  }
};

const getSearchStatusElements = () => ({
  resultsEl: document.getElementById("uv-search-results"),
  noResultsEl: document.getElementById("uv-search-no-results"),
  countEl: document.getElementById("uv-search-count"),
  prevLink: document.getElementById("uv-search-prev"),
  nextLink: document.getElementById("uv-search-next"),
});

const showNoSearchYet = ({ resultsEl, noResultsEl, countEl }) => {
  setHidden(resultsEl, true);
  setHidden(noResultsEl, true);
  if (countEl) {
    countEl.textContent = "";
  }
};

const showNoSearchResults = ({ resultsEl, noResultsEl }) => {
  setHidden(resultsEl, true);
  setHidden(noResultsEl, false);
};

const showSearchResults = (
  { resultsEl, noResultsEl, countEl, prevLink, nextLink },
  searchState,
) => {
  setHidden(noResultsEl, true);
  setHidden(resultsEl, false);
  if (countEl) {
    countEl.textContent = `${searchState.currentIndex + 1} of ${searchState.hits.length}`;
  }
  setNavLinkState(prevLink, searchState.currentIndex > 0);
  setNavLinkState(
    nextLink,
    searchState.currentIndex < searchState.hits.length - 1,
  );
};

const updateSearchStatus = (searchState) => {
  const elements = getSearchStatusElements();
  if (!searchState.searched) {
    showNoSearchYet(elements);
    return;
  }
  if (searchState.hits.length === 0) {
    showNoSearchResults(elements);
    return;
  }
  showSearchResults(elements, searchState);
};

window.UvSearchStatus = {
  update: updateSearchStatus,
  hideError: hideSearchError,
  showError: showSearchError,
};
