import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MirrorFutureApiService } from '../../core/services/mirror-future-api.service';
import { MirrorFutureService } from '../../core/services/mirror-future.service';
import {
  MonteCarloAnalysisOutput,
  DailyScheduleInput,
  WhatsAppSendResult
} from '../../core/models/mirror-future.model';

@Component({
  selector: 'app-actuators-control-panel',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="space-y-8 max-w-7xl mx-auto p-4 md:p-6">
      <!-- Header Banner -->
      <div class="relative overflow-hidden rounded-2xl bg-gradient-to-r from-amber-950/80 via-slate-900 to-slate-950 border border-amber-500/20 p-6 md:p-8 backdrop-blur-xl shadow-2xl">
        <div class="absolute -top-24 -right-24 w-80 h-80 bg-amber-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
          <div>
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-semibold uppercase tracking-wider mb-3">
              <span class="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span>
              Stochastic Oracle • Production Actuators
            </div>
            <h1 class="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
              Actuator Controls & Monte Carlo Simulation
            </h1>
            <p class="text-slate-400 mt-2 text-sm md:text-base max-w-3xl">
              Adjust your real daily routine parameters, run 1,000 simulation paths across 180 days with NumPy and Llama 3.3 70B, and automatically sync prescriptions with Google Calendar and WhatsApp.
            </p>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <!-- LEFT COLUMN (Col 1-5): Time Controls and Golden Action Button -->
        <div class="lg:col-span-5 space-y-6">
          <div class="rounded-2xl bg-slate-900/80 border border-slate-800 p-6 backdrop-blur-xl shadow-xl space-y-6">
            <div class="flex items-center justify-between border-b border-slate-800 pb-3">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 font-bold text-lg">
                  ⚙️
                </div>
                <div>
                  <h2 class="text-base font-bold text-white">Daily Input Parameters</h2>
                  <p class="text-xs text-slate-400">Hourly breakdown across 24 hrs</p>
                </div>
              </div>
              <span class="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                Total: {{ totalHoursPlanned.toFixed(1) }} / 24h
              </span>
            </div>

            <!-- Slider: Work Hours -->
            <div class="space-y-2">
              <div class="flex justify-between items-center text-xs">
                <span class="font-medium text-slate-300 flex items-center gap-1.5">
                  <span class="w-2.5 h-2.5 rounded-full bg-sky-400"></span> Employment / Remote Work Hours
                </span>
                <span class="font-mono text-sky-400 font-bold text-sm">{{ workHours }} hrs/day</span>
              </div>
              <input
                type="range"
                min="1.0"
                max="14.0"
                step="0.5"
                [(ngModel)]="workHours"
                class="w-full accent-sky-400 h-2 bg-slate-950 rounded-lg cursor-pointer" />
            </div>

            <!-- Slider: Thesis / Project Hours -->
            <div class="space-y-2">
              <div class="flex justify-between items-center text-xs">
                <span class="font-medium text-slate-300 flex items-center gap-1.5">
                  <span class="w-2.5 h-2.5 rounded-full bg-emerald-400"></span> Project / Research Hours
                </span>
                <span class="font-mono text-emerald-400 font-bold text-sm">{{ thesisHours }} hrs/day</span>
              </div>
              <input
                type="range"
                min="0.5"
                max="10.0"
                step="0.5"
                [(ngModel)]="thesisHours"
                class="w-full accent-emerald-400 h-2 bg-slate-950 rounded-lg cursor-pointer" />
            </div>

            <!-- Slider: Sleep Hours -->
            <div class="space-y-2">
              <div class="flex justify-between items-center text-xs">
                <span class="font-medium text-slate-300 flex items-center gap-1.5">
                  <span class="w-2.5 h-2.5 rounded-full bg-indigo-400"></span> Actual Sleep Hours
                </span>
                <span class="font-mono text-indigo-400 font-bold text-sm">{{ sleepHours }} hrs/day</span>
              </div>
              <input
                type="range"
                min="4.0"
                max="11.0"
                step="0.5"
                [(ngModel)]="sleepHours"
                class="w-full accent-indigo-400 h-2 bg-slate-950 rounded-lg cursor-pointer" />
            </div>

            <!-- Slider: Social / Leisure Hours -->
            <div class="space-y-2">
              <div class="flex justify-between items-center text-xs">
                <span class="font-medium text-slate-300 flex items-center gap-1.5">
                  <span class="w-2.5 h-2.5 rounded-full bg-pink-400"></span> Social / Family / Leisure Hours
                </span>
                <span class="font-mono text-pink-400 font-bold text-sm">{{ socialHours }} hrs/day</span>
              </div>
              <input
                type="range"
                min="0.0"
                max="8.0"
                step="0.5"
                [(ngModel)]="socialHours"
                class="w-full accent-pink-400 h-2 bg-slate-950 rounded-lg cursor-pointer" />
            </div>

            <!-- Horizon Days for ICS Export -->
            <div class="pt-2 border-t border-slate-800 flex items-center justify-between text-xs">
              <span class="text-slate-400">Horizon Days (.ICS Subscription):</span>
              <select
                [(ngModel)]="horizonDays"
                class="px-2.5 py-1 rounded-lg bg-slate-950 border border-slate-700 text-white font-mono text-xs focus:outline-none focus:border-amber-500">
                <option [value]="7">7 days</option>
                <option [value]="14">14 days (2 weeks)</option>
                <option [value]="30">30 days (1 month)</option>
                <option [value]="60">60 days (2 months)</option>
              </select>
            </div>

            <!-- GOLDEN ACTION BUTTON -->
            <button
              (click)="executeOracleSimulation()"
              [disabled]="isSimulatingMonteCarlo"
              class="w-full py-4 px-6 rounded-2xl bg-gradient-to-r from-amber-400 via-yellow-400 to-amber-500 hover:from-amber-300 hover:via-yellow-300 hover:to-amber-400 active:scale-[0.98] text-slate-950 font-black text-xs sm:text-sm tracking-wide uppercase shadow-xl shadow-amber-500/25 ring-2 ring-amber-400/50 transition-all flex items-center justify-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed">
              @if (isSimulatingMonteCarlo) {
                <svg class="animate-spin h-5 w-5 text-slate-950" viewBox="0 0 24 24" fill="none">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                </svg>
                <span>CALCULATING 1,000 PATHS WITH NUMPY & LLAMA...</span>
              } @else {
                <span class="text-base">⚡</span>
                <span>RUN MIRROR FUTURE ORACLE (MONTE CARLO + INVERSE ENGINEERING)</span>
              }
            </button>

            @if (simulationError) {
              <div class="p-3 rounded-lg bg-red-950/60 border border-red-500/40 text-red-300 text-xs">
                {{ simulationError }}
              </div>
            }
          </div>

          <!-- PHYSICAL PRODUCTION ACTUATORS -->
          <div class="rounded-2xl bg-slate-900/80 border border-slate-800 p-6 backdrop-blur-xl shadow-xl space-y-5">
            <div class="flex items-center justify-between border-b border-slate-800 pb-3">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-teal-500/10 border border-teal-500/20 flex items-center justify-center text-teal-400 font-bold">
                  🚀
                </div>
                <div>
                  <h3 class="text-base font-bold text-white">Physical Production Actuators</h3>
                  <p class="text-xs text-slate-400">RFC 5545 export and WhatsApp Cloud API</p>
                </div>
              </div>
            </div>

            <!-- Button 1: Download Real Calendar .ics -->
            <div>
              <button
                (click)="downloadRealCalendarIcs()"
                [disabled]="isDownloadingIcs"
                class="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-teal-600 to-cyan-600 hover:from-teal-500 hover:to-cyan-500 active:bg-teal-700 text-white font-bold text-xs shadow-lg shadow-teal-950/50 transition-all flex items-center justify-center gap-2 disabled:opacity-40">
                @if (isDownloadingIcs) {
                  <span>Generating RFC 5545...</span>
                } @else {
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                  </svg>
                  <span>DOWNLOAD OPTIMAL SCHEDULE (.ICS)</span>
                }
              </button>
              <p class="text-[11px] text-slate-400 mt-1.5 text-center">
                Compatible with Google Calendar, Apple Calendar, and Microsoft Outlook.
              </p>
            </div>

            <!-- Button 2: Send Prescription to WhatsApp -->
            <div class="pt-3 border-t border-slate-800 space-y-3">
              <h4 class="text-xs font-bold uppercase tracking-wider text-slate-300">
                Send Causal Prescription to WhatsApp
              </h4>
              <div>
                <label class="block text-[11px] text-slate-400 mb-1">Recipient Phone Number (E.164 format with country code)</label>
                <input
                  type="text"
                  [(ngModel)]="recipientPhone"
                  placeholder="+573001234567"
                  class="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-700 text-white placeholder-slate-500 text-xs font-mono focus:outline-none focus:border-emerald-500" />
              </div>
              <div>
                <label class="block text-[11px] text-slate-400 mb-1">Causal Prescription Message</label>
                <textarea
                  [(ngModel)]="prescriptionMessage"
                  rows="3"
                  class="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-700 text-white placeholder-slate-500 text-xs focus:outline-none focus:border-emerald-500 resize-none font-mono"></textarea>
              </div>

              <button
                (click)="sendPrescriptionToWhatsApp()"
                [disabled]="!recipientPhone || isSendingWhatsApp"
                class="w-full py-2.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 active:bg-emerald-700 text-white font-bold text-xs shadow-md transition-all flex items-center justify-center gap-2 disabled:opacity-40">
                @if (isSendingWhatsApp) {
                  <span>Transmitting to WhatsApp Cloud API...</span>
                } @else {
                  <span>SEND PRESCRIPTION TO WHATSAPP</span>
                }
              </button>

              @if (whatsAppSendResult) {
                <div class="p-3 rounded-lg text-xs"
                     [ngClass]="whatsAppSendResult.success ? 'bg-emerald-950/60 border border-emerald-500/40 text-emerald-300' : 'bg-red-950/60 border border-red-500/40 text-red-300'">
                  <div class="font-bold">
                    {{ whatsAppSendResult.success ? '✓ Message Sent Successfully' : '✗ Delivery Failed' }}
                  </div>
                  @if (whatsAppSendResult.message_id) {
                    <div class="text-[10px] font-mono mt-0.5">ID: {{ whatsAppSendResult.message_id }}</div>
                  }
                  @if (whatsAppSendResult.error_message) {
                    <div class="text-[10px] mt-0.5">{{ whatsAppSendResult.error_message }}</div>
                  }
                </div>
              }
            </div>
          </div>
        </div>

        <!-- RIGHT COLUMN (Col 6-12): Monte Carlo Results, Curves & Diagnostics -->
        <div class="lg:col-span-7 space-y-6">
          @if (simulationResult) {
            <!-- Probability Cards & Inverse Engineering -->
            <div class="rounded-2xl bg-slate-900/90 border border-amber-500/30 p-6 backdrop-blur-xl shadow-2xl space-y-6">
              <div class="flex items-center justify-between border-b border-slate-800 pb-3">
                <div class="flex items-center gap-2">
                  <span class="w-3 h-3 rounded-full bg-amber-400"></span>
                  <h3 class="font-bold text-white text-base">
                    Inverse Engineering Prescription (NumPy + Llama 3.3 70B)
                  </h3>
                </div>
                <span class="text-xs font-mono text-amber-400 px-2 py-0.5 rounded bg-amber-950 border border-amber-800">
                  1,000 Paths
                </span>
              </div>

              <!-- 3 Probabilities Gauges -->
              <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <!-- Thesis 120 days -->
                <div class="bg-slate-950/80 p-4 rounded-xl border border-slate-800">
                  <span class="text-xs text-slate-400 block mb-1">Thesis Success Prob. (Day 120)</span>
                  <div class="text-2xl font-black text-emerald-400 font-mono">
                    {{ (simulationResult.prescription.thesis_completion_probability_at_day_120 * 100).toFixed(0) }}%
                  </div>
                  <div class="w-full bg-slate-800 h-1.5 rounded-full mt-2 overflow-hidden">
                    <div class="h-full bg-emerald-500 rounded-full"
                         [style.width.%]="simulationResult.prescription.thesis_completion_probability_at_day_120 * 100"></div>
                  </div>
                </div>

                <!-- Thesis 180 days -->
                <div class="bg-slate-950/80 p-4 rounded-xl border border-slate-800">
                  <span class="text-xs text-slate-400 block mb-1">Thesis Success Prob. (Day 180)</span>
                  <div class="text-2xl font-black text-cyan-400 font-mono">
                    {{ (simulationResult.prescription.thesis_completion_probability_at_day_180 * 100).toFixed(0) }}%
                  </div>
                  <div class="w-full bg-slate-800 h-1.5 rounded-full mt-2 overflow-hidden">
                    <div class="h-full bg-cyan-500 rounded-full"
                         [style.width.%]="simulationResult.prescription.thesis_completion_probability_at_day_180 * 100"></div>
                  </div>
                </div>

                <!-- Burnout P90 -->
                <div class="bg-slate-950/80 p-4 rounded-xl border"
                     [ngClass]="simulationResult.prescription.burnout_probability_p90_at_day_180 > 0.3 ? 'border-rose-500/40' : 'border-slate-800'">
                  <span class="text-xs text-slate-400 block mb-1">Burnout Risk (P90)</span>
                  <div class="text-2xl font-black font-mono"
                       [ngClass]="simulationResult.prescription.burnout_probability_p90_at_day_180 > 0.3 ? 'text-rose-400' : 'text-emerald-400'">
                    {{ (simulationResult.prescription.burnout_probability_p90_at_day_180 * 100).toFixed(0) }}%
                  </div>
                  <div class="w-full bg-slate-800 h-1.5 rounded-full mt-2 overflow-hidden">
                    <div class="h-full rounded-full"
                         [ngClass]="simulationResult.prescription.burnout_probability_p90_at_day_180 > 0.3 ? 'bg-rose-500' : 'bg-emerald-500'"
                         [style.width.%]="simulationResult.prescription.burnout_probability_p90_at_day_180 * 100"></div>
                  </div>
                </div>
              </div>

              <!-- Top Optimal Caps Calculated -->
              <div class="grid grid-cols-3 gap-3 p-3 rounded-xl bg-amber-950/20 border border-amber-500/20 text-center text-xs">
                <div>
                  <span class="text-slate-400 block">Optimal Work Cap:</span>
                  <strong class="text-amber-400 font-mono text-sm">
                    {{ simulationResult.prescription.optimal_daily_work_cap_hours }} hrs/day
                  </strong>
                </div>
                <div>
                  <span class="text-slate-400 block">Optimal Thesis Hours:</span>
                  <strong class="text-emerald-400 font-mono text-sm">
                    {{ simulationResult.prescription.optimal_daily_thesis_hours }} hrs/day
                  </strong>
                </div>
                <div>
                  <span class="text-slate-400 block">Minimum Sleep Target:</span>
                  <strong class="text-indigo-400 font-mono text-sm">
                    {{ simulationResult.prescription.minimum_sleep_target_hours }} hrs/night
                  </strong>
                </div>
              </div>

              <!-- Causal Diagnosis Meta Llama 3.3 70B -->
              <div class="space-y-2">
                <h4 class="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                  <span class="text-amber-400">🤖</span>
                  Causal Diagnosis — Meta Llama 3.3 (70B Reasoning)
                </h4>
                <div class="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-200 leading-relaxed whitespace-pre-wrap font-sans">
                  {{ simulationResult.llama_causal_diagnosis }}
                </div>
              </div>

              <!-- Strategic Levers -->
              @if (simulationResult.prescription.strategic_levers && simulationResult.prescription.strategic_levers.length > 0) {
                <div>
                  <h4 class="text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
                    Identified Strategic Levers:
                  </h4>
                  <div class="flex flex-wrap gap-2">
                    @for (lever of simulationResult.prescription.strategic_levers; track $index) {
                      <div class="px-3 py-1 rounded-lg bg-slate-950 border border-amber-500/30 text-amber-300 text-xs flex items-center gap-1.5">
                        <span>✦</span> {{ lever }}
                      </div>
                    }
                  </div>
                </div>
              }

              <!-- Trajectory Curves (SVG) -->
              <div class="space-y-3 pt-3 border-t border-slate-800">
                <div class="flex items-center justify-between">
                  <h4 class="text-xs font-bold uppercase tracking-wider text-slate-300">
                    Stochastic Trajectories over 180 Days (P10, P50, P90 Percentiles)
                  </h4>
                  <div class="flex items-center gap-3 text-[11px]">
                    <span class="flex items-center gap-1 text-emerald-400"><span class="w-2 h-2 rounded-full bg-emerald-400"></span> Thesis</span>
                    <span class="flex items-center gap-1 text-rose-400"><span class="w-2 h-2 rounded-full bg-rose-400"></span> Burnout</span>
                    <span class="flex items-center gap-1 text-amber-400"><span class="w-2 h-2 rounded-full bg-amber-400"></span> Fatigue</span>
                  </div>
                </div>

                <!-- SVG Mini-Chart -->
                <div class="w-full h-44 bg-slate-950 rounded-xl border border-slate-800 p-2 relative overflow-hidden flex items-end">
                  <svg class="w-full h-full" viewBox="0 0 180 100" preserveAspectRatio="none">
                    <!-- Grid horizontal lines -->
                    <line x1="0" y1="20" x2="180" y2="20" stroke="rgba(255,255,255,0.05)" stroke-width="0.5"/>
                    <line x1="0" y1="50" x2="180" y2="50" stroke="rgba(255,255,255,0.05)" stroke-width="0.5"/>
                    <line x1="0" y1="80" x2="180" y2="80" stroke="rgba(255,255,255,0.05)" stroke-width="0.5"/>

                    <!-- Thesis curve (green) -->
                    <polyline
                      fill="none"
                      stroke="#10b981"
                      stroke-width="2"
                      [attr.points]="getPolylinePoints(simulationResult.curves.thesis_progress, 1.0)" />

                    <!-- Burnout curve (red) -->
                    <polyline
                      fill="none"
                      stroke="#f43f5e"
                      stroke-width="1.8"
                      stroke-dasharray="2,2"
                      [attr.points]="getPolylinePoints(simulationResult.curves.burnout_risk, 1.0)" />

                    <!-- Fatigue curve (amber) -->
                    <polyline
                      fill="none"
                      stroke="#f59e0b"
                      stroke-width="1.5"
                      [attr.points]="getPolylinePoints(simulationResult.curves.fatigue, 100.0)" />
                  </svg>
                </div>
                <div class="flex justify-between text-[10px] text-slate-500 font-mono">
                  <span>Day 0</span>
                  <span>Day 60</span>
                  <span>Day 120</span>
                  <span>Day 180</span>
                </div>
              </div>
            </div>
          } @else {
            <!-- Empty Placeholder -->
            <div class="rounded-2xl bg-slate-900/40 border border-slate-800 border-dashed p-12 text-center text-slate-500 space-y-4">
              <div class="text-4xl">🔮</div>
              <h3 class="text-lg font-bold text-slate-300">Oracle on Standby</h3>
              <p class="text-xs max-w-md mx-auto text-slate-400">
                Adjust your target hours in the left panel and click the golden button to run a 1,000-trajectory Monte Carlo simulation with inverse engineering diagnosis.
              </p>
            </div>
          }
        </div>
      </div>
    </div>
  `
})
export class ActuatorsControlPanelComponent {
  private readonly apiService = inject(MirrorFutureApiService);
  readonly mirrorFutureService = inject(MirrorFutureService);
  // Backward compatibility alias
  readonly drJefService = this.mirrorFutureService;

  // Input hours
  workHours: number = 6.5;
  thesisHours: number = 2.5;
  sleepHours: number = 7.5;
  socialHours: number = 1.5;
  horizonDays: number = 14;

  // States
  isSimulatingMonteCarlo = false;
  isDownloadingIcs = false;
  isSendingWhatsApp = false;
  simulationError: string | null = null;

  // Results
  simulationResult: MonteCarloAnalysisOutput | null = null;
  whatsAppSendResult: WhatsAppSendResult | null = null;

  // WhatsApp actuation form
  recipientPhone: string = '+573001234567';
  prescriptionMessage: string = 'MIRROR FUTURE - Optimal Causal Prescription: Max work 6.5h/day, Thesis 2.5h/day, Min sleep 7.5h/night to target 98% completion without burnout.';

  get totalHoursPlanned(): number {
    return Number(this.workHours) + Number(this.thesisHours) + Number(this.sleepHours) + Number(this.socialHours);
  }

  executeOracleSimulation(): void {
    this.isSimulatingMonteCarlo = true;
    this.simulationError = null;

    const schedule: DailyScheduleInput[] = Array.from({ length: 180 }, (_, day) => {
      const isWeekend = (day % 7) === 5 || (day % 7) === 6;
      return {
        day_index: day,
        work_hours: isWeekend ? Math.max(0, Number(this.workHours) * 0.25) : Number(this.workHours),
        thesis_hours: isWeekend ? Math.min(10, Number(this.thesisHours) + 1.5) : Number(this.thesisHours),
        sleep_hours: isWeekend ? Math.min(10, Number(this.sleepHours) + 1.0) : Number(this.sleepHours),
        social_hours: isWeekend ? Math.min(8, Number(this.socialHours) + 2.0) : Number(this.socialHours),
        is_weekend: isWeekend
      };
    });

    this.apiService.simulateMonteCarlo(schedule, {
      num_trajectories: 1000,
      num_days: 180,
      thesis_total_units_required: 350.0
    }).subscribe({
      next: (output) => {
        this.simulationResult = output;
        this.mirrorFutureService.setMonteCarloOutput(output);
        this.isSimulatingMonteCarlo = false;

        // Auto-update WhatsApp prescription text with optimal parameters
        if (output.prescription) {
          this.prescriptionMessage = `MIRROR FUTURE - Causal Prescription:\nOptimal daily work cap: ${output.prescription.optimal_daily_work_cap_hours}h/day\nThesis: ${output.prescription.optimal_daily_thesis_hours}h/day\nMin sleep: ${output.prescription.minimum_sleep_target_hours}h/night\nThesis success probability (180d): ${(output.prescription.thesis_completion_probability_at_day_180 * 100).toFixed(0)}%\nBurnout risk P90: ${(output.prescription.burnout_probability_p90_at_day_180 * 100).toFixed(0)}%`;
        }
      },
      error: (err) => {
        this.simulationError = err?.error?.detail || err?.message || 'Error in stochastic simulation.';
        this.isSimulatingMonteCarlo = false;
      }
    });
  }

  downloadRealCalendarIcs(): void {
    this.isDownloadingIcs = true;
    const workCap = this.simulationResult?.prescription?.optimal_daily_work_cap_hours ?? Number(this.workHours);
    const thesis = this.simulationResult?.prescription?.optimal_daily_thesis_hours ?? Number(this.thesisHours);

    this.apiService.downloadCalendarIcs(workCap, thesis, this.horizonDays).subscribe({
      next: (blob) => {
        this.apiService.triggerIcsDownload(blob, `mirror_future_optimal_schedule_${this.horizonDays}d.ics`);
        this.isDownloadingIcs = false;
      },
      error: (err) => {
        console.error('Error downloading .ics', err);
        this.isDownloadingIcs = false;
      }
    });
  }

  sendPrescriptionToWhatsApp(): void {
    if (!this.recipientPhone || !this.prescriptionMessage) return;

    this.isSendingWhatsApp = true;
    this.whatsAppSendResult = null;

    this.apiService.sendWhatsAppAlert({
      recipient_phone: this.recipientPhone,
      message_text: this.prescriptionMessage
    }).subscribe({
      next: (res) => {
        this.whatsAppSendResult = res;
        this.isSendingWhatsApp = false;
      },
      error: (err) => {
        this.whatsAppSendResult = {
          success: false,
          status_code: 500,
          recipient_phone: this.recipientPhone,
          error_message: err?.error?.detail || err?.message || 'Error transmitting message',
          timestamp: new Date().toISOString()
        };
        this.isSendingWhatsApp = false;
      }
    });
  }

  getPolylinePoints(points: any[], maxVal: number = 1.0): string {
    if (!points || points.length === 0) return '';
    return points.map(pt => {
      const x = Math.min(180, Math.max(0, pt.day));
      // Normalize y to 0..100, where 0 is at top and 100 at bottom in SVG
      const normalizedY = Math.min(100, Math.max(0, (pt.p50 / maxVal) * 100));
      const y = 100 - normalizedY;
      return `${x},${y.toFixed(1)}`;
    }).join(' ');
  }
}
