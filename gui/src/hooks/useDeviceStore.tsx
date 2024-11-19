import { create } from "zustand";
import { devtools } from "zustand/middleware";

interface DeviceState {
  microphoneConnected: boolean;
  setMicrophoneConnected: (microphoneConnected: boolean) => void;
}

// Create a store for the device state
export const useDeviceStore = create<DeviceState>()(
  devtools((set) => ({
    microphoneConnected: false,
    setMicrophoneConnected: (microphoneConnected) =>
      set({ microphoneConnected }),
  }))
);
