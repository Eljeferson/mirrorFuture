import {
  Component,
  ChangeDetectionStrategy,
  input,
  output,
  signal,
  computed,
  inject,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  MonteCarloCurves,
  InverseEngineeringPrescription,
  TrajectoryPercentilePoint,
} from '../../core/models/mirror-future.model';
import { MirrorFutureService } from '../../core/services/mirror-future.service';

type MetricKey = 'thesis_progress' | 'fatigue' | 'burnout_risk' | 'relational_capital';

interface MetricMeta {
  key: MetricKey;
  label: string;
  unit: string;
  minVal: number;
  maxVal: number;
  targetLine?: number;
  targetLabel?: string;
  dangerLine?: number;
  dangerLabel?: string;
  badgeClass: string;
  colorP90: string;
  colorP50: string;
  colorP10: string;
  fillGradient: string;
  description: string;
}

@Component({
  selector: 'app-monte-carlo-chart',
  standalone: true,
  imports: [CommonModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="w-full flex flex-col gap-6 font-sans">
      
      <!-- HEADER & METRIC CONTROLS -->
      <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl backdrop-blur-md">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="w-2.5 h-2.5 rounded-full bg-amber-400"></span>
            <span class="text-xs font-mono font-bold tracking-wider uppercase text-amber-400">
              LIFE SIMULATION • 1,000 POSSIBLE PROJECTIONS
            </span>
          </div>
          <h2 class="text-xl md:text-2xl font-black text-white tracking-tight">
            Evolution of Habits & Goals at 180 Days
          </h2>
          <p class="text-xs text-slate-300 mt-0.5 max-w-prose leading-relaxed">
            Comparative projections: Optimal Scenario (Mirror Future Plan), Probable Scenario (Current pace), and Risk Scenario (Habit neglect).
          </p>
        </div>

        <!-- Metric Selector / Quad View Toggle -->
        <div class="flex flex-wrap items-center gap-1.5 p-1 rounded-xl bg-slate-950/80 border border-slate-800">
          @for (m of availableMetrics; track m.key) {
            <button
              type="button"
              (click)="activeMetricKey.set(m.key); viewMode.set('single')"
              [class]="viewMode() === 'single' && activeMetricKey() === m.key 
                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-sm' 
                : 'text-slate-300 hover:text-white'"
              class="px-3 py-1.5 text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5"
            >
              <span>{{ m.label }}</span>
            </button>
          }

          <button
            type="button"
            (click)="viewMode.set('quad')"
            [class]="viewMode() === 'quad'
              ? 'bg-blue-500/20 text-blue-300 border border-blue-500/40 shadow-sm' 
              : 'text-slate-300 hover:text-white'"
              class="px-3 py-1.5 text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5"
          >
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
            </svg>
            <span>4D View</span>
          </button>
        </div>
      </div>

      <!-- MAIN CHART CONTAINER -->
      @if (viewMode() === 'single') {
        @let cur = currentMetricMeta();
        @let curvePoints = getPointsForMetric(cur.key);
        
        <div class="relative p-6 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-2xl backdrop-blur-md flex flex-col gap-4">
          <!-- Chart Top Info Bar -->
          <div class="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800/80">
            <div>
              <div class="flex items-center gap-2">
                <span class="text-sm font-bold text-white">{{ cur.label }}</span>
                <span class="text-xs px-2 py-0.5 rounded font-mono" [ngClass]="cur.badgeClass">{{ cur.unit }}</span>
              </div>
              <p class="text-xs text-slate-300 mt-0.5 max-w-prose leading-relaxed">{{ cur.description }}</p>
            </div>

            <!-- Hover Telemetry Capsule -->
            <div class="flex items-center gap-4 bg-slate-950/70 px-4 py-2 rounded-xl border border-slate-800 font-mono text-xs">
              <span class="text-slate-300">Day <strong class="text-white">{{ hoveredDay() }}</strong></span>
              
              <div class="flex items-center gap-1.5 text-amber-400">
                <span class="w-2 h-2 rounded-full bg-[#F59E0B]"></span>
                <span>Optimal: <strong>{{ hoveredValues()?.p90 }}</strong></span>
              </div>

              <div class="flex items-center gap-1.5 text-blue-400">
                <span class="w-2 h-2 rounded-full bg-[#3B82F6]"></span>
                <span>Probable: <strong>{{ hoveredValues()?.p50 }}</strong></span>
              </div>

              <div class="flex items-center gap-1.5 text-red-400">
                <span class="w-2 h-2 rounded-full bg-[#EF4444]"></span>
                <span>Risk: <strong>{{ hoveredValues()?.p10 }}</strong></span>
              </div>
            </div>
          </div>

          <!-- SVG Visualizer -->
          <div class="relative w-full h-[360px] md:h-[420px] select-none" (mousemove)="onChartMouseMove($event)" (mouseleave)="onChartMouseLeave()">
            <svg class="w-full h-full overflow-visible" viewBox="0 0 1000 400" preserveAspectRatio="none">
              <defs>
                <linearGradient id="bandGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="#F59E0B" stop-opacity="0.22" />
                  <stop offset="50%" stop-color="#3B82F6" stop-opacity="0.12" />
                  <stop offset="100%" stop-color="#EF4444" stop-opacity="0.05" />
                </linearGradient>

                <linearGradient id="gridLineFade" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stop-color="#334155" stop-opacity="0.1" />
                  <stop offset="100%" stop-color="#334155" stop-opacity="0.4" />
                </linearGradient>
              </defs>

              <!-- Horizontal Grid Lines -->
              @for (yVal of getYAxisGrid(cur); track $index) {
                @let yPos = mapValToSvgY(yVal, cur);
                <g>
                  <line x1="50" [attr.y1]="yPos" x2="980" [attr.y2]="yPos" stroke="#1e293b" stroke-width="1" stroke-dasharray="4 4" />
                  <text x="40" [attr.y]="yPos + 4" fill="#94a3b8" font-size="12" font-family="monospace" text-anchor="end">
                    {{ yVal }}
                  </text>
                </g>
              }

              <!-- Vertical Day Markers (Day 0, 30, 60, 90, 120, 150, 180) -->
              @for (dayMark of [0, 30, 60, 90, 120, 150, 180]; track dayMark) {
                @let xPos = mapDayToSvgX(dayMark);
                <g>
                  <line [attr.x1]="xPos" y1="20" [attr.x2]="xPos" y2="360" stroke="#1e293b" stroke-width="1" />
                  <text [attr.x]="xPos" y="380" fill="#94a3b8" font-size="12" font-family="monospace" text-anchor="middle">
                    D{{ dayMark }}
                  </text>
                </g>
              }

              <!-- Critical Threshold Line (e.g. 350 thesis units or 0.70 burnout risk) -->
              @if (cur.targetLine !== undefined) {
                @let targetY = mapValToSvgY(cur.targetLine, cur);
                <g>
                  <line x1="50" [attr.y1]="targetY" x2="980" [attr.y2]="targetY" stroke="#10b981" stroke-width="1.5" stroke-dasharray="6 3" />
                  <text x="975" [attr.y]="targetY - 6" fill="#10b981" font-size="12" font-family="monospace" text-anchor="end" font-weight="bold">
                    {{ cur.targetLabel }}: {{ cur.targetLine }}
                  </text>
                </g>
              }

              @if (cur.dangerLine !== undefined) {
                @let dangerY = mapValToSvgY(cur.dangerLine, cur);
                <g>
                  <line x1="50" [attr.y1]="dangerY" x2="980" [attr.y2]="dangerY" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="6 3" />
                  <text x="975" [attr.y]="dangerY - 6" fill="#ef4444" font-size="12" font-family="monospace" text-anchor="end" font-weight="bold">
                    {{ cur.dangerLabel }}: {{ cur.dangerLine }}
                  </text>
                </g>
              }

              <!-- Milestone Vertical Callouts: Day 48 Inflection & Day 120 Milestone -->
              @let x48 = mapDayToSvgX(48);
              <line [attr.x1]="x48" y1="20" [attr.x2]="x48" y2="360" stroke="#f59e0b" stroke-width="1" stroke-dasharray="2 3" opacity="0.6" />
              <text [attr.x]="x48 + 4" y="35" fill="#f59e0b" font-size="12" font-family="monospace" opacity="0.9">
                D48: Key Inflection
              </text>

              @let x120 = mapDayToSvgX(120);
              <line [attr.x1]="x120" y1="20" [attr.x2]="x120" y2="360" stroke="#38bdf8" stroke-width="1" stroke-dasharray="2 3" opacity="0.6" />
              <text [attr.x]="x120 + 4" y="35" fill="#38bdf8" font-size="12" font-family="monospace" opacity="0.9">
                D120: Target Milestone
              </text>

              <!-- SHADED CONFIDENCE BAND (Between P10 and P90) -->
              <path [attr.d]="computeBandSvgPath(curvePoints, cur)" fill="url(#bandGradient)" />

              <!-- P10 Line: Red Branch / Lower Bound (#EF4444) -->
              <path [attr.d]="computeLineSvgPath(curvePoints, cur, 'p10')" fill="none" stroke="#EF4444" stroke-width="2.5" stroke-dasharray="5 3" />

              <!-- P50 Line: Baseline Median (#3B82F6) -->
              <path [attr.d]="computeLineSvgPath(curvePoints, cur, 'p50')" fill="none" stroke="#3B82F6" stroke-width="3" />

              <!-- P90 Line: Golden Optimal Branch (#F59E0B) -->
              <path [attr.d]="computeLineSvgPath(curvePoints, cur, 'p90')" fill="none" stroke="#F59E0B" stroke-width="3" stroke-dasharray="7 2" />

              <!-- ACTIVE HOVER SCRUBBER VERTICAL CROSSHAIR -->
              @let hoverX = mapDayToSvgX(hoveredDay());
              <g>
                <line [attr.x1]="hoverX" y1="20" [attr.x2]="hoverX" y2="360" stroke="#ffffff" stroke-width="1.5" opacity="0.75" />
                
                @if (hoveredValues(); as hv) {
                  <!-- P90 Dot -->
                  <circle [attr.cx]="hoverX" [attr.cy]="mapValToSvgY(hv.p90, cur)" r="5" fill="#F59E0B" stroke="#ffffff" stroke-width="1.5" />
                  <!-- P50 Dot -->
                  <circle [attr.cx]="hoverX" [attr.cy]="mapValToSvgY(hv.p50, cur)" r="5" fill="#3B82F6" stroke="#ffffff" stroke-width="1.5" />
                  <!-- P10 Dot -->
                  <circle [attr.cx]="hoverX" [attr.cy]="mapValToSvgY(hv.p10, cur)" r="5" fill="#EF4444" stroke="#ffffff" stroke-width="1.5" />
                }
              </g>
            </svg>
          </div>

          <!-- Bottom Legend for Curves -->
          <div class="flex flex-wrap items-center justify-between gap-4 pt-3 border-t border-slate-800 text-xs">
            <div class="flex flex-wrap items-center gap-4">
              <div class="flex items-center gap-2">
                <span class="w-4 h-0.5 bg-[#F59E0B] border-t-2 border-dashed border-[#F59E0B]"></span>
                <span class="text-slate-300"><strong class="text-amber-400">Optimal Scenario:</strong> Following recommended plan</span>
              </div>
              <div class="flex items-center gap-2">
                <span class="w-4 h-1 bg-[#3B82F6] rounded"></span>
                <span class="text-slate-300"><strong class="text-blue-400">Probable Scenario:</strong> At current pace</span>
              </div>
              <div class="flex items-center gap-2">
                <span class="w-4 h-0.5 bg-[#EF4444] border-t-2 border-dotted border-[#EF4444]"></span>
                <span class="text-slate-300"><strong class="text-red-400">Risk Scenario:</strong> If rest & habits are neglected</span>
              </div>
            </div>

            <div class="text-slate-300 text-xs italic">
              Hover over the chart to inspect trajectories day by day
            </div>
          </div>
        </div>
      } @else {
        <!-- QUAD VIEW: 4 SIMULTANEOUS CURVES -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          @for (m of availableMetrics; track m.key) {
            @let pts = getPointsForMetric(m.key);
            <div class="p-4 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-lg flex flex-col gap-2">
              <div class="flex items-center justify-between pb-2 border-b border-slate-800">
                <span class="text-sm font-bold text-white">{{ m.label }}</span>
                <span class="text-xs px-2 py-0.5 rounded font-mono" [ngClass]="m.badgeClass">{{ m.unit }}</span>
              </div>

              <div class="w-full h-44 relative">
                <svg class="w-full h-full overflow-visible" viewBox="0 0 500 200" preserveAspectRatio="none">
                  <!-- Band -->
                  <path [attr.d]="computeBandSvgPath(pts, m, 500, 200)" fill="#3b82f6" fill-opacity="0.12" />
                  <!-- Lines -->
                  <path [attr.d]="computeLineSvgPath(pts, m, 'p10', 500, 200)" fill="none" stroke="#EF4444" stroke-width="1.8" stroke-dasharray="3 2" />
                  <path [attr.d]="computeLineSvgPath(pts, m, 'p50', 500, 200)" fill="none" stroke="#3B82F6" stroke-width="2.2" />
                  <path [attr.d]="computeLineSvgPath(pts, m, 'p90', 500, 200)" fill="none" stroke="#F59E0B" stroke-width="2" stroke-dasharray="4 2" />
                </svg>
              </div>

              <div class="flex items-center justify-between text-xs font-mono text-slate-300 pt-1 border-t border-slate-800/60">
                <span>D0: {{ pts[0].p50 }}</span>
                <span>D90: {{ pts[90].p50 }}</span>
                <span>D180: {{ pts[179].p50 }}</span>
              </div>
            </div>
          }
        </div>
      }

      <!-- CAUSAL DIAGNOSIS & KEY LEVERS -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        <!-- LLAMA CAUSAL DIAGNOSIS CARD (7 Cols) -->
        <div class="lg:col-span-7 p-6 rounded-2xl bg-gradient-to-br from-slate-900/95 via-slate-900/90 to-purple-950/20 border border-purple-900/40 shadow-xl backdrop-blur-md flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between gap-3 mb-3">
              <div class="flex items-center gap-2">
                <div class="w-7 h-7 rounded-lg bg-purple-500/20 border border-purple-500/30 flex items-center justify-center text-purple-400">
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <h3 class="text-sm font-black text-purple-300 tracking-wider uppercase font-mono">
                  PERSONALIZED CAUSAL DIAGNOSIS
                </h3>
              </div>
              <span class="text-xs px-2.5 py-0.5 rounded-full bg-purple-950/70 border border-purple-500/30 text-purple-300 font-mono">
                Data Analytics
              </span>
            </div>

            <div class="p-4 rounded-xl bg-slate-950/70 border border-slate-800 text-xs text-slate-200 max-w-prose leading-relaxed font-sans whitespace-pre-line">
              {{ diagnosis() || 'Generating causal analysis and habit projections...' }}
            </div>
          </div>

          <!-- Timeline Risk Alert Box -->
          <div class="mt-4 p-3.5 rounded-xl bg-amber-950/30 border border-amber-500/30 flex items-center gap-3">
            <div class="text-amber-400 shrink-0">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div class="text-xs">
              <strong class="text-amber-300 block mb-0.5">Habit Inflection Point (Days 48 - 52)</strong>
              <span class="text-slate-300 max-w-prose leading-relaxed block">
                The difference between achieving your goal sustainably or reaching exhaustion depends on respecting your daily work cap and sleep targets.
              </span>
            </div>
          </div>
        </div>

        <!-- STRATEGIC LEVERS OF PRESCRIPTION (5 Cols) -->
        <div class="lg:col-span-5 p-6 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl backdrop-blur-md flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between gap-2 mb-3">
              <h3 class="text-sm font-black text-amber-400 tracking-wider uppercase font-mono">
                KEY LEVERS FOR YOUR GOAL
              </h3>
              <span class="text-xs text-slate-300 font-mono">Recommended Plan</span>
            </div>

            <!-- Key Prescription Metrics -->
            @if (prescription(); as p) {
              <div class="grid grid-cols-3 gap-2 mb-4 font-mono text-center">
                <div class="p-2.5 rounded-xl bg-slate-950/70 border border-slate-800">
                  <span class="text-xs text-slate-300 block uppercase font-medium">Work Cap</span>
                  <span class="text-sm font-bold text-amber-400">{{ p.optimal_daily_work_cap_hours }}h</span>
                  <span class="text-xs text-slate-400 block">/day max</span>
                </div>

                <div class="p-2.5 rounded-xl bg-slate-950/70 border border-slate-800">
                  <span class="text-xs text-slate-300 block uppercase font-medium">Project Goal</span>
                  <span class="text-sm font-bold text-blue-400">{{ p.optimal_daily_thesis_hours }}h</span>
                  <span class="text-xs text-slate-400 block">focus</span>
                </div>

                <div class="p-2.5 rounded-xl bg-slate-950/70 border border-slate-800">
                  <span class="text-xs text-slate-300 block uppercase font-medium">Sleep Target</span>
                  <span class="text-sm font-bold text-emerald-400">{{ p.minimum_sleep_target_hours }}h</span>
                  <span class="text-xs text-slate-400 block">minimum</span>
                </div>
              </div>

              <!-- Success Probabilities -->
              <div class="space-y-2 mb-4 font-mono text-xs">
                <div class="flex items-center justify-between p-2 rounded-lg bg-emerald-950/20 border border-emerald-500/20 text-emerald-300">
                  <span>Success Probability at Day 120:</span>
                  <strong class="font-bold">{{ (p.thesis_completion_probability_at_day_120 * 100).toFixed(1) }}%</strong>
                </div>

                <div class="flex items-center justify-between p-2 rounded-lg bg-emerald-950/30 border border-emerald-500/30 text-emerald-300">
                  <span>Success Probability at Day 180:</span>
                  <strong class="font-bold">{{ (p.thesis_completion_probability_at_day_180 * 100).toFixed(1) }}%</strong>
                </div>

                <div class="flex items-center justify-between p-2 rounded-lg bg-red-950/20 border border-red-500/20 text-red-300">
                  <span>Burnout Risk at Day 180:</span>
                  <strong class="font-bold">{{ (p.burnout_probability_p90_at_day_180 * 100).toFixed(1) }}%</strong>
                </div>
              </div>

              <!-- Strategic Levers Bullet List -->
              <div class="space-y-2">
                <span class="text-xs font-bold text-slate-300 uppercase tracking-wider block font-mono">
                  Recommended Actions:
                </span>
                @for (lever of p.strategic_levers; track $index) {
                  <div class="flex items-start gap-2 text-xs text-slate-200 bg-slate-950/40 p-2.5 rounded-xl border border-slate-800/80 max-w-prose leading-relaxed">
                    <span class="text-amber-400 font-bold">&bull;</span>
                    <span class="leading-relaxed">{{ lever }}</span>
                  </div>
                }
              </div>
            }
          </div>

          <!-- Actuator Actions -->
          <div class="mt-4 pt-3 border-t border-slate-800 flex items-center gap-2">
            <button
              type="button"
              (click)="downloadIcsCalendar()"
              class="flex-1 py-2 px-3 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs flex items-center justify-center gap-2 transition shadow-lg shadow-amber-500/20 cursor-pointer"
            >
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span>Export Mirror Future .ICS Schedule</span>
            </button>
          </div>
        </div>

      </div>

    </div>
  `,
})
export class MonteCarloChartComponent {
  readonly mirrorFutureService = inject(MirrorFutureService);
  // Backward compatibility alias
  readonly drJefService = this.mirrorFutureService;

  // Inputs
  curves = input<MonteCarloCurves | null>(null);
  prescription = input<InverseEngineeringPrescription | null>(null);
  diagnosis = input<string>('');

  // State
  activeMetricKey = signal<MetricKey>('thesis_progress');
  viewMode = signal<'single' | 'quad'>('single');
  hoveredDay = signal<number>(90);

  readonly availableMetrics: MetricMeta[] = [
    {
      key: 'thesis_progress',
      label: 'Project & Thesis Progress',
      unit: 'Net Units',
      minVal: 0,
      maxVal: 400,
      targetLine: 350,
      targetLabel: 'Completion Target',
      badgeClass: 'bg-amber-500/20 text-amber-300 border border-amber-500/30',
      colorP90: '#F59E0B',
      colorP50: '#3B82F6',
      colorP10: '#EF4444',
      fillGradient: 'bandGradient',
      description: 'Cumulative progress across projects and milestones with sustainable cognitive focus.',
    },
    {
      key: 'fatigue',
      label: 'Cumulative Fatigue',
      unit: 'Scale 0 - 100',
      minVal: 0,
      maxVal: 100,
      dangerLine: 65,
      dangerLabel: 'Critical Threshold',
      badgeClass: 'bg-red-500/20 text-red-300 border border-red-500/30',
      colorP90: '#EF4444',
      colorP50: '#3B82F6',
      colorP10: '#10B981',
      fillGradient: 'bandGradient',
      description: 'Daily accumulated exhaustion factoring in restorative sleep recovery.',
    },
    {
      key: 'burnout_risk',
      label: 'Burnout Risk',
      unit: 'Probability 0.0 - 1.0',
      minVal: 0.0,
      maxVal: 1.0,
      dangerLine: 0.70,
      dangerLabel: 'Severe Warning',
      badgeClass: 'bg-rose-500/20 text-rose-300 border border-rose-500/30',
      colorP90: '#EF4444',
      colorP50: '#3B82F6',
      colorP10: '#10B981',
      fillGradient: 'bandGradient',
      description: 'Projected probability of severe physical or cognitive burnout based on schedule and sleep.',
    },
    {
      key: 'relational_capital',
      label: 'Relational Capital',
      unit: 'Score 0 - 100',
      minVal: 0,
      maxVal: 100,
      targetLine: 60,
      targetLabel: 'Safe Zone',
      badgeClass: 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30',
      colorP90: '#10B981',
      colorP50: '#38BDF8',
      colorP10: '#EF4444',
      fillGradient: 'bandGradient',
      description: 'Health of key personal and professional relationships, preventing social isolation.',
    },
  ];

  readonly currentMetricMeta = computed(() => {
    return this.availableMetrics.find(m => m.key === this.activeMetricKey()) || this.availableMetrics[0];
  });

  readonly hoveredValues = computed<TrajectoryPercentilePoint | null>(() => {
    const pts = this.getPointsForMetric(this.activeMetricKey());
    const day = this.hoveredDay();
    return pts[day] || pts[pts.length - 1] || null;
  });

  getPointsForMetric(key: MetricKey): TrajectoryPercentilePoint[] {
    const c = this.curves();
    if (!c) return [];
    return c[key] || [];
  }

  // =========================================================================
  // SVG Math Mapping Helpers
  // =========================================================================

  mapDayToSvgX(day: number, svgWidth: number = 1000): number {
    const paddingLeft = 60;
    const paddingRight = 40;
    const usableWidth = svgWidth - paddingLeft - paddingRight;
    return paddingLeft + (day / 179) * usableWidth;
  }

  mapValToSvgY(val: number, meta: MetricMeta, svgHeight: number = 400): number {
    const paddingTop = 30;
    const paddingBottom = 50;
    const usableHeight = svgHeight - paddingTop - paddingBottom;
    const clamped = Math.max(meta.minVal, Math.min(meta.maxVal, val));
    const normalized = (clamped - meta.minVal) / (meta.maxVal - meta.minVal);
    return svgHeight - paddingBottom - normalized * usableHeight;
  }

  computeLineSvgPath(
    points: TrajectoryPercentilePoint[],
    meta: MetricMeta,
    branch: 'p10' | 'p50' | 'p90',
    svgWidth: number = 1000,
    svgHeight: number = 400
  ): string {
    if (!points || points.length === 0) return '';
    let d = '';
    points.forEach((pt, i) => {
      const x = this.mapDayToSvgX(pt.day, svgWidth);
      const y = this.mapValToSvgY(pt[branch], meta, svgHeight);
      d += i === 0 ? `M ${x.toFixed(1)} ${y.toFixed(1)}` : ` L ${x.toFixed(1)} ${y.toFixed(1)}`;
    });
    return d;
  }

  computeBandSvgPath(
    points: TrajectoryPercentilePoint[],
    meta: MetricMeta,
    svgWidth: number = 1000,
    svgHeight: number = 400
  ): string {
    if (!points || points.length === 0) return '';
    // Forward along P90, backward along P10
    let d = '';
    points.forEach((pt, i) => {
      const x = this.mapDayToSvgX(pt.day, svgWidth);
      const y = this.mapValToSvgY(pt.p90, meta, svgHeight);
      d += i === 0 ? `M ${x.toFixed(1)} ${y.toFixed(1)}` : ` L ${x.toFixed(1)} ${y.toFixed(1)}`;
    });

    for (let i = points.length - 1; i >= 0; i--) {
      const pt = points[i];
      const x = this.mapDayToSvgX(pt.day, svgWidth);
      const y = this.mapValToSvgY(pt.p10, meta, svgHeight);
      d += ` L ${x.toFixed(1)} ${y.toFixed(1)}`;
    }
    d += ' Z';
    return d;
  }

  getYAxisGrid(meta: MetricMeta): number[] {
    const step = (meta.maxVal - meta.minVal) / 4;
    return [
      meta.minVal,
      Number((meta.minVal + step).toFixed(2)),
      Number((meta.minVal + step * 2).toFixed(2)),
      Number((meta.minVal + step * 3).toFixed(2)),
      meta.maxVal,
    ];
  }

  // =========================================================================
  // Mouse Hover Interactions
  // =========================================================================

  onChartMouseMove(event: MouseEvent): void {
    const target = event.currentTarget as HTMLElement;
    const rect = target.getBoundingClientRect();
    const mouseX = event.clientX - rect.left;
    const paddingLeft = (60 / 1000) * rect.width;
    const paddingRight = (40 / 1000) * rect.width;
    const usableWidth = rect.width - paddingLeft - paddingRight;

    const ratio = Math.max(0, Math.min(1, (mouseX - paddingLeft) / usableWidth));
    const day = Math.round(ratio * 179);
    this.hoveredDay.set(day);
    this.mirrorFutureService.selectDay(day);
  }

  onChartMouseLeave(): void {
    this.hoveredDay.set(90);
  }

  downloadIcsCalendar(): void {
    const p = this.prescription();
    const workCap = p?.optimal_daily_work_cap_hours ?? 6.5;
    const thesisH = p?.optimal_daily_thesis_hours ?? 2.5;

    // Use direct API download link
    const url = `http://localhost:8000/api/causal/actuators/download-calendar.ics?work_cap_hours=${workCap}&thesis_hours=${thesisH}&days=14`;
    window.open(url, '_blank');
  }
}
