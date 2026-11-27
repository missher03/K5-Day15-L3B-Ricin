export function debounce(fn, waitMs = 300) {
  let timer = null;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), waitMs);
  };
}

let latestRequest = 0;

export async function onSearchInput(query, render) {
  const requestId = ++latestRequest;
  if (query.trim().length < 2) return render([]);
  const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
  const items = await res.json();
  if (requestId !== latestRequest) return;
  render(items);
}

export const searchHandler = debounce(onSearchInput, 300);
