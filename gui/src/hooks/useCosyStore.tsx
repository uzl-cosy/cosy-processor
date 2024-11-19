import { create } from "zustand";
import { devtools } from "zustand/middleware";

type HealthInfo = {
  cpuLoad: number;
  memoryLoad: number;
};

type StatusInfo = {
  microphones: number[];
  loading: number;
  progress: number;
  recording: boolean;
};

interface CosyState {
  running: boolean;
  setRunning: (running: boolean) => void;
  healthInfo: HealthInfo;
  setHealthInfo: (healthInfo: HealthInfo) => void;
  statusInfo: StatusInfo;
  setStatusInfo: (statusInfo: StatusInfo) => void;
}

// Create a store for the state of the Cosy process
export const useCosyStore = create<CosyState>()(
  devtools((set) => ({
    running: false,
    setRunning: (running) => set({ running }),
    healthInfo: { cpuLoad: 0, memoryLoad: 0 },
    setHealthInfo: (healthInfo) => set({ healthInfo }),
    statusInfo: {
      microphones: [],
      loading: 0.0,
      progress: 0.0,
      recording: false,
    },
    setStatusInfo: (statusInfo) => set({ statusInfo }),
  }))
);
