/**
 * Custom hook for managing high contrast mode.
 */

import { useState, useEffect, useCallback } from 'react';

const STORAGE_KEY = 'high-contrast-mode';

/**
 * Custom hook for high contrast accessibility mode.
 */
export function useHighContrast(): [boolean, () => void] {
  const [highContrast, setHighContrast] = useState<boolean>(() => {
    // Check localStorage first
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored !== null) {
      return stored === 'true';
    }

    // Check system preference
    if (typeof window !== 'undefined' && window.matchMedia) {
      return window.matchMedia('(prefers-contrast: more)').matches;
    }

    return false;
  });

  // Persist preference to localStorage
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, String(highContrast));
  }, [highContrast]);

  // Listen for system preference changes
  useEffect(() => {
    if (typeof window === 'undefined' || !window.matchMedia) return;

    const mediaQuery = window.matchMedia('(prefers-contrast: more)');
    const handleChange = (e: MediaQueryListEvent) => {
      // Only update if user hasn't set a manual preference
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored === null) {
        setHighContrast(e.matches);
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  const toggleHighContrast = useCallback(() => {
    setHighContrast((prev) => !prev);
  }, []);

  return [highContrast, toggleHighContrast];
}
