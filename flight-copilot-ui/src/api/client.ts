const BASE_URL = import.meta.env.VITE_API_URL as string;

const getRequest = async <T>(route: string, query: string): Promise<T> => {
  const url = new URL(route, BASE_URL);
  url.searchParams.set('q', query);

  const response = await fetch(url.toString(), {
    headers: { 'Content-Type': 'application/json' },
  });

  if (!response.ok) throw new Error(`HTTP ${response.status}`);

  return (await response.json()) as T;
};

const postRequest = async <T>(route: string, payload: any): Promise<T> => {
  const res = await fetch(BASE_URL + route, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.detail || 'Post request failed');
  }

  return res.json();
};

export const api = {
  get: getRequest,
  post: postRequest,
};
