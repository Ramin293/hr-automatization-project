import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Locale, PersonaId, ThemeMode } from './types';

interface DeveloperState {
  persona: PersonaId;
  locale: Locale;
  theme: ThemeMode;
  scenario: string;
  dataMode: 'mock' | 'api';
  workflowMode: 'mock' | 'camunda';
  signatureMode: 'mock' | 'api';
  developerOpen: boolean;
  sidebarCollapsed: boolean;
  setPersona: (persona: PersonaId) => void;
  setLocale: (locale: Locale) => void;
  setTheme: (theme: ThemeMode) => void;
  setScenario: (scenario: string) => void;
  toggleDeveloper: () => void;
  toggleSidebar: () => void;
}

export const useDeveloperStore = create<DeveloperState>()(persist((set) => ({
  persona: 'secretary', locale: 'ru', theme: 'dark', scenario: 'normal', dataMode: 'mock', workflowMode: 'mock', signatureMode: 'mock', developerOpen: false, sidebarCollapsed: false,
  setPersona: (persona) => set({ persona }),
  setLocale: (locale) => set({ locale }),
  setTheme: (theme) => set({ theme }),
  setScenario: (scenario) => set({ scenario }),
  toggleDeveloper: () => set((state) => ({ developerOpen: !state.developerOpen })),
  toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed }))
}), { name: 'ertis-developer-settings' }));
