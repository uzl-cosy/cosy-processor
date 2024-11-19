export interface IElectronAPI {
  startCosy: (command: string, cwd: string) => void;
  stopCosy: () => void;
  onCosyStdout: (callback: (data: string) => void) => void;
  onCosyStderr: (callback: (data: string) => void) => void;
  onCosyExit: (callback: (data: number) => void) => void;
}

declare global {
  interface Window {
    electronAPI: IElectronAPI;
  }
}
