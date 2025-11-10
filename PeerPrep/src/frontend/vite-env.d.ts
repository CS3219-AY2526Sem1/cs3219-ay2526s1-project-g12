/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly VITE_API_URL: string
    readonly VITE_SIGNALING_SERVER_URL: string
    readonly VITE_ICE_SERVERS: string
    readonly VITE_WS_GATEWAY_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
