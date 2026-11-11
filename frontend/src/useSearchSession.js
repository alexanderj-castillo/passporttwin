import { useEffect, useState } from "react";

export default function useSearchSession(key, defaults) {
  const storageKey = `passporttwin:search:${key}`;
  const [state, setState] = useState(() => {
    try {
      return { ...defaults, ...JSON.parse(sessionStorage.getItem(storageKey)) };
    } catch {
      return defaults;
    }
  });

  useEffect(() => {
    try {
      sessionStorage.setItem(storageKey, JSON.stringify(state));
    } catch {
      // Keep the search usable when the browser blocks storage.
    }
  }, [state, storageKey]);

  return [state, setState];
}
