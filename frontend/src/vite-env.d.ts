/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_API_TIMEOUT: string;
  readonly VITE_ENABLE_MOCK_MODE: string;
  readonly VITE_ENABLE_HIGH_CONTRAST: string;
  readonly VITE_SESSION_TIMEOUT_MINUTES: string;
  readonly VITE_ANALYTICS_ENABLED: string;
  readonly VITE_ANALYTICS_ENDPOINT: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
