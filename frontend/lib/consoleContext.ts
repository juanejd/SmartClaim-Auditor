import { createContext, useContext } from "react";

interface ConsoleContextValue {
  refreshHistory: () => Promise<void>;
}

export const ConsoleContext = createContext<ConsoleContextValue>({
  refreshHistory: async () => {},
});

export function useConsole() {
  return useContext(ConsoleContext);
}
