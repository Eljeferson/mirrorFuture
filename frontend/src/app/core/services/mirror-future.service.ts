import { Injectable, signal } from '@angular/core';
import {
  MonteCarloCurves,
  InverseEngineeringPrescription,
  SocialTwinPrediction,
  TrajectoryPercentileBranch,
  MultiTwinSimulationResult,
  MonteCarloAnalysisOutput
} from '../models/mirror-future.model';

@Injectable({
  providedIn: 'root'
})
export class MirrorFutureService {
  // Shared reactive global state across all feature views
  readonly curves = signal<MonteCarloCurves | null>(null);
  readonly prescription = signal<InverseEngineeringPrescription | null>(null);
  readonly diagnosis = signal<string>('');
  readonly simulatedContacts = signal<SocialTwinPrediction[]>([]);
  
  readonly selectedContact = signal<SocialTwinPrediction | null>(null);
  readonly selectedBranch = signal<TrajectoryPercentileBranch | 'all'>('all');
  readonly selectedDay = signal<number>(90);
  readonly visualRestMode = signal<boolean>(false);
  
  // Reactive language system: English ('EN') default
  readonly language = signal<'EN' | 'ES'>(this.getInitialLanguage());

  private getInitialLanguage(): 'EN' | 'ES' {
    if (typeof window !== 'undefined' && window.localStorage) {
      const saved = localStorage.getItem('mf_language');
      if (saved === 'ES') return 'ES';
      if (saved === 'EN') return 'EN';
    }
    return 'EN';
  }

  setLanguage(lang: 'EN' | 'ES'): void {
    this.language.set(lang);
    if (typeof window !== 'undefined' && window.localStorage) {
      try {
        localStorage.setItem('mf_language', lang);
      } catch {}
    }
  }

  toggleLanguage(): void {
    this.setLanguage(this.language() === 'EN' ? 'ES' : 'EN');
  }

  toggleVisualRestMode(): void {
    this.visualRestMode.update(v => !v);
  }

  setMonteCarloOutput(output: MonteCarloAnalysisOutput): void {
    this.curves.set(output.curves);
    this.prescription.set(output.prescription);
    this.diagnosis.set(output.llama_causal_diagnosis);
  }

  setSocialTwinResult(result: MultiTwinSimulationResult): void {
    this.simulatedContacts.set(result.simulated_contacts || []);
  }

  selectContact(contact: SocialTwinPrediction | null): void {
    this.selectedContact.set(contact);
  }

  selectBranch(branch: TrajectoryPercentileBranch | 'all'): void {
    this.selectedBranch.set(branch);
  }

  selectDay(day: number): void {
    this.selectedDay.set(day);
  }
}

// Backwards compatibility alias
export { MirrorFutureService as DrJefService };
