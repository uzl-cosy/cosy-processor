import { create } from "zustand";
import { devtools, persist } from "zustand/middleware";

interface ConfigState {
  startCommand: string;
  setStartCommand: (startCommand: string) => void;
  workingDirectory: string;
  setWorkingDirectory: (workingDirectory: string) => void;
  microphoneName: string;
  setMicrophoneName: (microphoneName: string) => void;
}

// Create a store for the configuration state
export const useConfigStore = create<ConfigState>()(
  devtools(
    persist(
      (set) => ({
        startCommand: "",
        setStartCommand: (startCommand) => set({ startCommand }),
        workingDirectory: "",
        setWorkingDirectory: (workingDirectory) => set({ workingDirectory }),
        microphoneName: "",
        setMicrophoneName: (microphoneName) => set({ microphoneName }),
      }),
      { name: "cosy-config" }
    )
  )
);
