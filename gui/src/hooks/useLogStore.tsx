import { create } from "zustand";
import { devtools } from "zustand/middleware";

type LogEntry = {
  type: "stdout" | "stderr" | "exit";
  data: string;
};

interface LogState {
  log: LogEntry[];
  addLog: (entry: LogEntry) => void;
}

// Create a store for the log
export const useLogStore = create<LogState>()(
  devtools((set) => ({
    log: [],
    addLog: (entry: LogEntry) =>
      set((state: LogState) => ({ log: [...state.log, entry] })),
  }))
);
