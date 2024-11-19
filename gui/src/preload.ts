// See the Electron documentation for details on how to use preload scripts:
// https://www.electronjs.org/docs/latest/tutorial/process-model#preload-scripts

import { contextBridge, ipcRenderer } from "electron";

contextBridge.exposeInMainWorld("electronAPI", {
  startCosy: (command: string, cwd: string) =>
    ipcRenderer.send("start-cosy", command, cwd),
  stopCosy: () => ipcRenderer.send("stop-cosy"),
  onCosyStdout: (callback: (data: string) => void) =>
    ipcRenderer.on("cosy-stdout", (event, data) => callback(data)),
  onCosyStderr: (callback: (data: string) => void) =>
    ipcRenderer.on("cosy-stderr", (event, data) => callback(data)),
  onCosyExit: (callback: (data: number) => void) =>
    ipcRenderer.on("cosy-exit", (event, data) => callback(data)),
});
