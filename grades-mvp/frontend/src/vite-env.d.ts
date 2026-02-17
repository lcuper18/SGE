// Global type declarations for Electron API exposed via preload
export {}

declare global {
  interface Window {
    electron: {
      keytar: {
        setPassword: (account: string, token: string) => Promise<{ success: boolean; error?: string }>
        getPassword: (account: string) => Promise<{ success: boolean; token?: string; error?: string }>
        deletePassword: (account: string) => Promise<{ success: boolean; error?: string }>
      }
      env: {
        platform: 'darwin' | 'win32' | 'linux'
        isProduction: boolean
      }
    }
  }
}
