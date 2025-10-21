import "@testing-library/jest-dom";

// Provide a minimal window.matchMedia mock commonly used by MUI and responsive hooks.
// Cast to any on assignment to satisfy TypeScript in test environment.
const mockMatchMedia = (query: string): MediaQueryList => ({
  matches: false,
  media: query,
  onchange: null,
  addListener: () => {}, // legacy
  removeListener: () => {}, // legacy
  addEventListener: () => {},
  removeEventListener: () => {},
  dispatchEvent: () => false,
});

(window as any).matchMedia = mockMatchMedia;

export {};
