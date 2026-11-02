import {

  Component,

  ChangeDetectionStrategy,

  inject,

  signal,

  computed,

  OnInit,

  OnDestroy,

  Output,

  EventEmitter,

} from '@angular/core';

import { Router } from '@angular/router';

import { CommonModule } from '@angular/common';

import { FormsModule } from '@angular/forms';

import { DrJefApiService } from '../../core/services/dr-jef-api.service';

import { DrJefService } from '../../core/services/dr-jef.service';

import {

  HolisticFutureRequest,

  HolisticFutureResponse,

  HorizonSnapshot,

  LiveWebSource,

  DiscoveryQuestionsRequest,

  DiscoveryQuestionsResponse,

  DiscoveryInterviewMessage,

  DiscoveryInterviewRequest,

  DiscoveryInterviewResponse,

  SyncDossierRequest,

  SyncDossierResponse,

  GoalFeasibilityItem,

  GoalsVerificationReport,

  CareerLifeEvent,

  CareerTransitionNode,

  CareerAutocompletionResult,

} from '../../core/models/dr-jef.model';

import { DrJefCausalGraph3dComponent } from '../multiverse-3d/dr-jef-causal-graph-3d.component';

import { MonteCarloChartComponent } from '../multiverse-3d/monte-carlo-chart.component';



@Component({

  selector: 'app-future-self-oracle-v4',

  standalone: true,

  imports: [

    CommonModule,

    FormsModule,

    DrJefCausalGraph3dComponent,

    MonteCarloChartComponent,

  ],

  changeDetection: ChangeDetectionStrategy.OnPush,

  styles: [`

    @keyframes cinematicPan {

      0% { transform: scale(1.0) translate(0%, 0%); }

      50% { transform: scale(1.08) translate(-1.5%, -1%); }

      100% { transform: scale(1.04) translate(1%, 0.5%); }

    }

    .animate-cinematic-pan {

      animation: cinematicPan 16s ease-in-out infinite alternate;

    }

    @keyframes audioBar1 {

      0%, 100% { height: 4px; }

      50% { height: 14px; }

    }

    @keyframes audioBar2 {

      0%, 100% { height: 12px; }

      50% { height: 4px; }

    }

    @keyframes audioBar3 {

      0%, 100% { height: 7px; }

      50% { height: 16px; }

    }

    .animate-audio-bar-1 { animation: audioBar1 0.8s ease-in-out infinite; }

    .animate-audio-bar-2 { animation: audioBar2 0.6s ease-in-out infinite; }

    .animate-audio-bar-3 { animation: audioBar3 0.9s ease-in-out infinite; }

  
    @keyframes slideInRight {
      0% { transform: translateX(100%); }
      100% { transform: translateX(0); }
    }
    .animate-slide-in {
      animation: slideInRight 0.25s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }

  `],

  template: `

    <div class="min-h-screen bg-[#EAEAEB] text-zinc-900 p-3 sm:p-6 lg:p-8 font-sans selection:bg-[#FF5500] selection:text-white">

      <!-- ======================================================== -->
      <!-- PLANTILLA REUTILIZABLE DE PARÁMETROS (FORMULARIO / DRAWER) -->
      <!-- ======================================================== -->
      <ng-template #parametersFormTemplate>
        <div class="space-y-4">
            <!-- Autocompletado con archivo -->

            <div class="p-3.5 rounded-2xl bg-[#F5F5F7] border border-black/10 space-y-2">

              <div class="flex items-center justify-between">

                <span class="text-xs font-bold text-zinc-700">{{ drJefService.language() === 'EN' ? 'Autocomplete with File' : 'Autocompletar con Archivo' }}</span>

                <span class="text-[10px] text-zinc-500 font-mono">.ics / .txt</span>

              </div>

              <label class="flex flex-col items-center justify-center border border-dashed border-black/20 hover:border-[#FF5500] rounded-xl p-3 cursor-pointer bg-white transition group">

                <span class="text-xs font-medium text-zinc-600 group-hover:text-black">

                  {{ uploadedFileName() ? uploadedFileName() : (drJefService.language() === 'EN' ? 'Upload Google Calendar (.ics) or Chat (.txt)' : 'Subir Google Calendar (.ics) o Chat (.txt)') }}

                </span>

                <span class="text-[10px] text-zinc-400 mt-0.5">{{ drJefService.language() === 'EN' ? 'Secure & automatic parsing' : 'Parseo seguro y automático' }}</span>

                <input type="file" (change)="onFileAutofill($event)" accept=".ics,.txt,.zip" class="hidden" />

              </label>



              @if (chatAnalysisBadge()) {

                <div class="p-2.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-medium flex items-center gap-2">

                  <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shrink-0"></span>

                  <span class="leading-tight">{{ chatAnalysisBadge() }}</span>

                </div>

              }

            </div>



            <!-- Carga de Foto Actual (Rasgos Físicos Llama 3.2 Vision) -->

            <div class="p-3.5 rounded-2xl bg-[#F5F5F7] border border-black/10 space-y-2">

              <div class="flex items-center justify-between">

                <span class="text-xs font-bold text-zinc-700 flex items-center gap-1.5">

                  <span>📸</span> {{ drJefService.language() === 'EN' ? 'Reference Photo' : 'Foto de Referencia' }}

                </span>

                <span class="text-[10px] text-zinc-500 font-mono">{{ drJefService.language() === 'EN' ? 'Optional' : 'Opcional' }}</span>

              </div>



              @if (userPhotoPreview()) {

                <div class="flex items-center gap-3 p-2 bg-white rounded-xl border border-black/10">

                  <img

                    [src]="userPhotoPreview()"

                    [alt]="drJefService.language() === 'EN' ? 'Current reference photo' : 'Foto de referencia actual'"

                    class="w-12 h-12 rounded-lg object-cover border border-black/10 shrink-0 shadow-xs"

                  />

                  <div class="flex-1 min-w-0">

                    <span class="text-xs font-bold text-zinc-900 block truncate flex items-center gap-1">

                      <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>

                      {{ drJefService.language() === 'EN' ? 'Features linked' : 'Rasgos vinculados' }}

                    </span>

                    <span class="text-[10px] text-zinc-500 block truncate">{{ drJefService.language() === 'EN' ? 'Llama 3.2 Vision active' : 'Llama 3.2 Vision activo' }}</span>

                  </div>

                  <button

                    type="button"

                    (click)="removeUserPhoto()"

                    class="text-xs text-red-500 hover:text-red-700 px-2 py-1 font-semibold cursor-pointer rounded-lg hover:bg-red-50 transition"

                    [title]="drJefService.language() === 'EN' ? 'Remove current photo' : 'Quitar foto actual'"

                  >

                    ✕ {{ drJefService.language() === 'EN' ? 'Remove' : 'Quitar' }}

                  </button>

                </div>

              } @else {

                <label class="flex flex-col items-center justify-center border border-dashed border-black/20 hover:border-[#FF5500] rounded-xl p-3 cursor-pointer bg-white transition group text-center">

                  <span class="text-xs font-medium text-zinc-600 group-hover:text-black">

                    {{ drJefService.language() === 'EN' ? '📸 Upload my current photo (Optional to customize your future portrait)' : '📸 Subir mi foto actual (Opcional para personalizar tu retrato futuro)' }}

                  </span>

                  <span class="text-[10px] text-zinc-400 mt-0.5">

                    {{ drJefService.language() === 'EN' ? 'Llama 3.2 Vision will adapt future images to your physical features' : 'Llama 3.2 Vision adaptará las imágenes del futuro a tus rasgos físicos' }}

                  </span>

                  <input

                    type="file"

                    (change)="onPhotoUpload($event)"

                    accept="image/*"

                    class="hidden"

                  />

                </label>

              }

            </div>



            <!-- 1. SELECTOR PRINCIPAL: ¿CUÁL DESCRIBE MEJOR TU REALIDAD ACTUAL? -->

            <div class="p-3.5 rounded-2xl bg-black text-white space-y-2.5 shadow-md">

              <div class="flex items-center justify-between">

                <label class="text-xs font-bold font-mono uppercase tracking-wider text-[#FF5500] flex items-center gap-1.5">

                  <span>⚡</span>

                  <span>{{ drJefService.language() === 'EN' ? 'Current Reality Profile' : '¿Cuál describe mejor tu realidad actual?' }}</span>

                </label>

                <span class="text-[10px] text-zinc-400 font-mono">{{ drJefService.language() === 'EN' ? 'Active Filter' : 'Filtro Activo' }}</span>

              </div>

              <select
                [(ngModel)]="realitySeed.life_profile_type"
                (ngModelChange)="onProfileTypeChange()"
                class="w-full bg-zinc-900 border border-white/20 rounded-xl px-2.5 py-2 text-xs text-white focus:outline-none focus:border-[#FF5500] font-medium cursor-pointer"
              >
                <option value="DAY_TO_DAY_WORKER">
                  🚕 {{ drJefService.language() === 'EN' ? 'Driver / Taxi / Urban mobility • Day-to-day worker' : 'Conductor / Taxista / Movilidad • Comercio día a día • Independiente' }}
                </option>
                <option value="RURAL_FIELD_PRODUCER">
                  🚜 {{ drJefService.language() === 'EN' ? 'Rural producer / Farms (poultry, swine, livestock) • Agriculture' : 'Trabajo del campo / Granjas (aves, cerdos, cuyes) • Ganadería • Agricultura' }}
                </option>
                <option value="BUSINESS_OWNER">
                  🏪 {{ drJefService.language() === 'EN' ? 'Business owner / Store / Entrepreneur / SME' : 'Dueño de negocio / Tienda / Bodega / Emprendedor / PYME' }}
                </option>
                <option value="SKILLED_TRADE">
                  🔧 {{ drJefService.language() === 'EN' ? 'Skilled trade / Mechanical workshop / Electrician / Operator' : 'Tengo un oficio técnico / Taller mecánico / Electricista / Manual' }}
                </option>
                <option value="TITLED_PROFESSIONAL">
                  🎓 {{ drJefService.language() === 'EN' ? 'Titled / Chartered professional / Salaried employee' : 'Profesional titulado / Colegiado / Trabajador con sueldo fijo' }}
                </option>
                <option value="UNIVERSITY_OR_TECH_STUDENT">
                  📚 {{ drJefService.language() === 'EN' ? 'University or technical student / Near graduation' : 'Estudiante universitario o técnico / Por egresar' }}
                </option>
              </select>
            </div>

            <!-- FICHA DE IDENTIDAD & OCUPACIÓN SINCRONIZADA (Nombre, Edad, Ocupación y Ubicación) -->
            <div class="p-3.5 rounded-2xl bg-white border border-black/10 space-y-3 shadow-xs">
              <div class="flex items-center justify-between">
                <span class="text-xs font-bold font-mono uppercase tracking-wider text-zinc-800 flex items-center gap-1.5">
                  <span>👤</span>
                  <span>{{ drJefService.language() === 'EN' ? 'Personal Identity & Exact Occupation' : 'Identidad Personal & Ocupación Exacta' }}</span>
                </span>
                <span class="text-[10px] text-emerald-600 font-mono font-bold flex items-center gap-1 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-md">
                  <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                  {{ drJefService.language() === 'EN' ? 'Live Synced' : 'Sincronizado en Vivo' }}
                </span>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                <div>
                  <label class="text-[11px] font-semibold text-zinc-700 block mb-1">
                    {{ drJefService.language() === 'EN' ? 'Full Name' : 'Nombre y Apellido' }}
                  </label>
                  <input
                    type="text"
                    [(ngModel)]="realitySeed.full_name"
                    (ngModelChange)="onGoalFieldChanged()"
                    [placeholder]="drJefService.language() === 'EN' ? 'e.g. Carlos Quispe' : 'ej. Carlos Quispe'"
                    class="w-full bg-[#F5F5F7] border border-black/15 rounded-xl px-2.5 py-2 text-xs text-zinc-900 focus:outline-none focus:border-[#FF5500] font-medium"
                  />
                </div>

                <div>
                  <label class="text-[11px] font-semibold text-zinc-700 block mb-1">
                    {{ drJefService.language() === 'EN' ? 'Age (Years)' : 'Edad (Años)' }}
                  </label>
                  <input
                    type="number"
                    [(ngModel)]="realitySeed.age"
                    (ngModelChange)="onGoalFieldChanged()"
                    [placeholder]="drJefService.language() === 'EN' ? 'e.g. 28' : 'ej. 28'"
                    min="15"
                    max="90"
                    class="w-full bg-[#F5F5F7] border border-black/15 rounded-xl px-2.5 py-2 text-xs text-zinc-900 focus:outline-none focus:border-[#FF5500] font-medium font-mono"
                  />
                </div>
              </div>

              <div>
                <label class="text-[11px] font-semibold text-zinc-700 block mb-1">
                  {{ drJefService.language() === 'EN' ? 'Exact Occupation / Trade / Business' : 'Ocupación / Rubro / Actividad Exacta' }}
                </label>
                <input
                  type="text"
                  [(ngModel)]="realitySeed.occupation"
                  (ngModelChange)="onGoalFieldChanged()"
                  [placeholder]="drJefService.language() === 'EN' ? 'e.g. Taxi driver, Chicken farm, Grocery shop...' : 'ej. Taxista en ruta, Granja de pollos/huevos, Tienda de abarrotes...'"
                  class="w-full bg-[#F5F5F7] border border-black/15 rounded-xl px-2.5 py-2 text-xs text-zinc-900 focus:outline-none focus:border-[#FF5500] font-medium"
                />
              </div>
            </div>




            <!-- 2. TOGGLE: MODO ESPEJO PURO VS EVALUAR META -->

            <div class="p-3.5 rounded-2xl bg-[#F5F5F7] border border-black/10 space-y-2">

              <div class="flex items-center justify-between">

                <span class="text-xs font-bold text-zinc-800 font-mono uppercase tracking-wider flex items-center gap-1.5">

                  <span>🪞</span>

                  <span>{{ drJefService.language() === 'EN' ? 'Projection Lens' : 'Modo de Proyección' }}</span>

                </span>

                <span class="text-[10px] text-zinc-500 font-mono">

                  {{ realitySeed.goal_mode ? (drJefService.language() === 'EN' ? 'Target Mode' : 'Con Meta') : (drJefService.language() === 'EN' ? 'Pure Mirror' : 'Espejo Puro') }}

                </span>

              </div>

              <div class="grid grid-cols-2 gap-1.5 p-1 bg-white rounded-xl border border-black/10">

                <button

                  type="button"

                  (click)="setGoalMode(false)"

                  [class]="!realitySeed.goal_mode ? 'bg-black text-white shadow-xs font-bold' : 'text-zinc-600 hover:text-black font-medium'"

                  class="px-2 py-2 rounded-lg text-[11px] text-center transition-all cursor-pointer flex items-center justify-center gap-1">

                  <span>🪞</span>

                  <span>{{ drJefService.language() === 'EN' ? 'Pure Mirror' : 'Espejo Puro' }}</span>

                </button>

                <button

                  type="button"

                  (click)="setGoalMode(true)"

                  [class]="realitySeed.goal_mode ? 'bg-[#FF5500] text-white shadow-xs font-bold' : 'text-zinc-600 hover:text-black font-medium'"

                  class="px-2 py-2 rounded-lg text-[11px] text-center transition-all cursor-pointer flex items-center justify-center gap-1">

                  <span>🎯</span>

                  <span>{{ drJefService.language() === 'EN' ? 'With Goal' : 'Con Meta' }}</span>

                </button>

              </div>

              <p class="text-[10px] text-zinc-500 leading-tight">

                @if (!realitySeed.goal_mode) {

                  {{ drJefService.language() === 'EN' ? 'Projects how you will look physically, bodily health, and wallet pressure simply continuing life as it is today.' : 'Muestra cómo se verá tu cuerpo, si tu dinero te alcanzará o se ajustará más, y tu ritmo de vida siguiendo como vives hoy.' }}

                } @else {

                  {{ drJefService.language() === 'EN' ? 'Assesses your timeline and success probability for a specific 1-year target.' : 'Evalúa qué requisitos exige el mercado y tu probabilidad real para cumplir una meta específica a 1 año.' }}

                }

              </p>

            </div>



            <!-- 3. UBICACIÓN GEOGRÁFICA REAL -->

            <div class="space-y-3">

              <div class="grid grid-cols-2 gap-2">

                <div>

                  <label class="text-xs font-semibold text-zinc-700 block mb-1">{{ drJefService.language() === 'EN' ? 'Country' : 'País' }}</label>

                  <select

                    [(ngModel)]="realitySeed.location.country"

                    (ngModelChange)="onCountryChange()"

                    class="w-full bg-[#F5F5F7] border border-black/15 rounded-xl px-2.5 py-2 text-xs text-zinc-900 focus:outline-none focus:border-[#FF5500] font-medium cursor-pointer"

                  >

                    <option value="" disabled [selected]="!realitySeed.location.country">{{ drJefService.language() === 'EN' ? 'Select a country...' : 'Selecciona un país...' }}</option>

                    <option value="Colombia">Colombia</option>

                    <option value="Perú">{{ drJefService.language() === 'EN' ? 'Peru' : 'Perú' }}</option>

                    <option value="México">{{ drJefService.language() === 'EN' ? 'Mexico' : 'México' }}</option>

                    <option value="Argentina">Argentina</option>

                    <option value="Chile">Chile</option>

                    <option value="España">{{ drJefService.language() === 'EN' ? 'Spain' : 'España' }}</option>

                    <option value="Estados Unidos">{{ drJefService.language() === 'EN' ? 'United States' : 'Estados Unidos' }}</option>

                  </select>

                </div>



                <div>

                  <label class="text-xs font-semibold text-zinc-700 block mb-1">{{ drJefService.language() === 'EN' ? 'Exact City' : 'Ciudad Exacta' }}</label>

                  <input

                    type="text"

                    [(ngModel)]="realitySeed.location.city"

                    [placeholder]="drJefService.language() === 'EN' ? 'e.g. Bogota, Lima, CDMX...' : 'ej. Huancayo, Arequipa, Bogotá...'"

                    class="w-full bg-[#F5F5F7] border border-black/15 rounded-xl px-2.5 py-2 text-xs text-zinc-900 focus:outline-none focus:border-[#FF5500]"

                  />

                </div>

              </div>

            </div>



            <!-- 4. CAMPOS ACTIVADOS DINÁMICAMENTE POR PERFIL -->



            <!-- CASO A: VIVO DEL DÍA A DÍA / COMERCIO / INDEPENDIENTE -->

            @if (realitySeed.life_profile_type === 'DAY_TO_DAY_WORKER') {

              <div class="p-3.5 rounded-2xl bg-[#F5F5F7] border border-black/10 space-y-2.5">

                <div class="flex items-center justify-between">

                  <span class="text-xs font-bold text-zinc-800 font-mono uppercase tracking-wider flex items-center gap-1.5">

                    <span>🛒</span> {{ drJefService.language() === 'EN' ? 'Commerce & Day-to-day' : 'Comercio & Día a Día' }}

                  </span>

                  <span class="text-[10px] text-amber-700 font-mono font-bold">{{ drJefService.language() === 'EN' ? 'Daily Cashflow' : 'Caja Diaria' }}</span>

                </div>



                <div>

                  <label class="text-[11px] text-zinc-600 block mb-1 font-medium">{{ drJefService.language() === 'EN' ? 'Line or Daily Activity' : 'Rubro o Actividad Diaria' }}</label>

                  <input

                    type="text"

                    [(ngModel)]="realitySeed.occupation"

                    [placeholder]="drJefService.language() === 'EN' ? 'e.g. Grocery store, taxi, hardware, sales...' : 'ej. Puesto de abarrotes, mototaxi, ferretería, venta ambulatoria...'"

                    class="w-full bg-white border border-black/15 rounded-xl px-3 py-1.5 text-xs text-zinc-900 focus:outline-none focus:border-[#FF5500]"

                  />

                </div>



                <div class="grid grid-cols-2 gap-2 text-xs">

                  <div>

                    <label class="text-[11px] text-zinc-600 block mb-1 font-medium">{{ drJefService.language() === 'EN' ? 'Normal Day Income (' + getCurrencySymbol() + ')' : 'Ingreso Día Normal (' + getCurrencySymbol() + ')' }}</label>

                    <input

                      type="number"

                      min="0"

                      [(ngModel)]="realitySeed.daily_income_avg"

                      placeholder="ej. 60"

                      class="w-full bg-white border border-black/15 rounded-xl px-2.5 py-1.5 font-mono text-zinc-900 font-bold focus:border-[#FF5500]"

                    />

                  </div>

                  <div>

                    <label class="text-[11px] text-zinc-600 block mb-1 font-medium">{{ drJefService.language() === 'EN' ? 'Days Worked / Week' : 'Días Laborados / Sem' }}</label>

                    <input

                      type="number"

                      min="1"

                      max="7"

                      [(ngModel)]="realitySeed.work_days_per_week"

                      class="w-full bg-white border border-black/15 rounded-xl px-2.5 py-1.5 font-mono text-zinc-900 font-bold focus:border-[#FF5500]"

                    />

                  </div>

                </div>



                <div class="grid grid-cols-2 gap-2 text-xs">

                  <div>

                    <label class="text-[11px] text-zinc-600 block mb-1 font-medium">{{ drJefService.language() === 'EN' ? 'Daily Family Expense (' + getCurrencySymbol() + ')' : 'Gasto Diario Familiar (' + getCurrencySymbol() + ')' }}</label>

                    <input

                      type="number"

                      min="0"

                      [(ngModel)]="realitySeed.daily_expense_avg"

                      placeholder="ej. 40"

                      class="w-full bg-white border border-black/15 rounded-xl px-2.5 py-1.5 font-mono text-zinc-900 font-bold focus:border-[#FF5500]"

                    />

                  </div>

                  <div>

                    <label class="text-[11px] text-zinc-600 block mb-1 font-medium">{{ drJefService.language() === 'EN' ? 'Daily Physical Wear' : 'Desgaste Físico Diario' }}</label>

                    <select

                      [(ngModel)]="realitySeed.physical_labor_intensity"

                      class="w-full bg-white border border-black/15 rounded-xl px-2 py-1.5 text-xs text-zinc-900 focus:outline-none focus:border-[#FF5500] font-medium cursor-pointer"

                    >

                      <option value="HIGH">{{ drJefService.language() === 'EN' ? 'High (Standing, lifting, sun/outdoors)' : 'Alto (De pie, carga, sol/calle)' }}</option>

                      <option value="MEDIUM">{{ drJefService.language() === 'EN' ? 'Medium (Shop / counter customer service)' : 'Medio (Atención en local / mostrador)' }}</option>

                      <option value="LOW">{{ drJefService.language() === 'EN' ? 'Low (Sedentary)' : 'Bajo (Sedentario)' }}</option>

                    </select>

                  </div>

                </div>



                <div class="grid grid-cols-2 gap-2 text-xs">

                  <div>

                    <label class="text-[11px] text-zinc-600 block mb-0.5 font-medium">{{ drJefService.language() === 'EN' ? 'Current Savings (' + getCurrencySymbol() + ')' : 'Ahorro Guardado (' + getCurrencySymbol() + ')' }}</label>

                    <input

                      type="number"

                      [(ngModel)]="realitySeed.finances.current_savings"

                      class="w-full bg-white border border-black/15 rounded-xl px-2.5 py-1.5 font-mono text-emerald-600 font-bold focus:border-[#FF5500]"

                    />

                  </div>

                  <div>

                    <label class="text-[11px] text-zinc-600 block mb-0.5 font-medium">{{ drJefService.language() === 'EN' ? 'Current Debt (' + getCurrencySymbol() + ')' : 'Deuda Actual (' + getCurrencySymbol() + ')' }}</label>

                    <input

                      type="number"

                      [(ngModel)]="realitySeed.finances.current_debt"

                      class="w-full bg-white border border-black/15 rounded-xl px-2.5 py-1.5 font-mono text-red-600 font-bold focus:border-[#FF5500]"

                    />

                  </div>

                </div>

                <div class="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <label class="text-[11px] text-zinc-600 block mb-0.5 font-medium">{{ drJefService.language() === 'EN' ? 'Current Savings (' + getCurrencySymbol() + ')' : 'Ahorro Guardado (' + getCurrencySymbol() + ')' }}</label>
                    <input
                      type="number"
                      min="0"
                      [(ngModel)]="realitySeed.finances.current_savings"
                      class="w-full bg-white border border-black/15 rounded-xl px-2.5 py-1.5 font-mono text-emerald-600 font-bold focus:border-[#FF5500]"
                    />
                  </div>
                  <div>
                    <label class="text-[11px] text-zinc-600 block mb-0.5 font-medium">{{ drJefService.language() === 'EN' ? 'Current Debt (' + getCurrencySymbol() + ')' : 'Deuda Actual (' + getCurrencySymbol() + ')' }}</label>
                    <input
                      type="number"
                      min="0"
                      [(ngModel)]="realitySeed.finances.current_debt"
                      class="w-full bg-white border border-black/15 rounded-xl px-2.5 py-1.5 font-mono text-red-600 font-bold focus:border-[#FF5500]"
                    />
                  </div>
                </div>

              </div>

            }



            <!-- CASO B: TRABAJO DEL CAMPO / AGRICULTURA / PRODUCCIÓN -->

            @if (realitySeed.life_profile_type === 'RURAL_FIELD_PRODUCER') {

              <div class="p-3.5 rounded-2xl bg-[#F5F5F7] border border-black/10 space-y-2.5">

                <div class="flex items-center justify-between">

                  <span class="text-xs font-bold text-zinc-800 font-mono uppercase tracking-wider flex items-center gap-1.5">

                    <span>🌱</span> {{ drJefService.language() === 'EN' ? 'Farming & Rural Production' : 'Campo & Producción Rural' }}

                  </span>

                  <span class="text-[10px] text-emerald-700 font-mono font-bold">{{ drJefService.language() === 'EN' ? 'Season / Harvest' : 'Campaña / Cosecha' }}</span>

                </div>



                <div>

                  <label class="text-[11px] text-zinc-600 block mb-1 font-medium">{{ drJefService.language() === 'EN' ? 'What do you cultivate, raise, or produce?' : '¿Qué cultivas, crías o produces?' }}</label>

                  <input

                    type="text"

                    [(ngModel)]="realitySeed.rural_product"

                    [placeholder]="drJefService.language() === 'EN' ? 'e.g. Potatoes, specialty coffee, cattle, trout...' : 'ej. Papa huayro, café especial, ganado vacuno, truchas...'"

                    class="w-full bg-white border border-black/15 rounded-xl px-3 py-1.5 text-xs text-zinc-900 focus:outline-none focus:border-[#FF5500]"

                  />

                </div>



                <div class="grid grid-cols-2 gap-2 text-xs">

                  <div>

                    <label class="text-[11px] text-zinc-600 block mb-1 font-medium">{{ drJefService.language() === 'EN' ? 'Est. Season Income (' + getCurrencySymbol() + ')' : 'Ingreso Est. Campaña (' + getCurrencySymbol() + ')' }}</label>

                    <input

                      type="number"

                      min="0"

                      [(ngModel)]="realitySeed.campaign_income_est"

                      placeholder="ej. 8000"

                      class="w-full bg-white border border-black/15 rounded-xl px-2.5 py-1.5 font-mono text-zinc-900 font-bold focus:border-[#FF5500]"

                    />

                  </div>

                  <div>

                    <label class="text-[11px] text-zinc-600 block mb-1 font-medium">{{ drJefService.language() === 'EN' ? 'Monthly Input Costs (' + getCurrencySymbol() + ')' : 'Gasto Mensual Insumos (' + getCurrencySymbol() + ')' }}</label>

                    <input

                      type="number"

                      min="0"

                      [(ngModel)]="realitySeed.finances.monthly_expenses"

                      class="w-full bg-white border border-black/15 rounded-xl px-2.5 py-1.5 font-mono text-zinc-900 font-bold focus:border-[#FF5500]"

                    />

                  </div>

                </div>



                <div class="grid grid-cols-2 gap-2 text-xs">

                  <div>

                    <label class="text-[11px] text-zinc-600 block mb-1 font-medium">{{ drJefService.language() === 'EN' ? 'Physical Labor Effort' : 'Esfuerzo Físico Faena' }}</label>

                    <select

                      [(ngModel)]="realitySeed.physical_labor_intensity"

                      class="w-full bg-white border border-black/15 rounded-xl px-2 py-1.5 text-xs text-zinc-900 focus:outline-none focus:border-[#FF5500] font-medium cursor-pointer"

                    >

                      <option value="HIGH">{{ drJefService.language() === 'EN' ? 'High (Intense shifts in field/dirt)' : 'Alto (Jornada dura en campo/tierra)' }}</option>

                      <option value="MEDIUM">{{ drJefService.language() === 'EN' ? 'Medium (Supervision & moderate shift)' : 'Medio (Supervisión y faena moderada)' }}</option>

                    </select>

                  </div>

                  <div>

                    <label class="text-[11px] text-zinc-600 block mb-1 font-medium">{{ drJefService.language() === 'EN' ? 'Agricultural / Bank Debt (' + getCurrencySymbol() + ')' : 'Deuda Agraria / Bancaria (' + getCurrencySymbol() + ')' }}</label>

                    <input

                      type="number"

                      min="0"

                      [(ngModel)]="realitySeed.finances.current_debt"

                      class="w-full bg-white border border-black/15 rounded-xl px-2.5 py-1.5 font-mono text-red-600 font-bold focus:border-[#FF5500]"

                    />

                  </div>

                </div>

              </div>

            }



            <!-- CASO C: OFICIO TÉCNICO / MANUAL / OPERATIVO -->

            @if (realitySeed.life_profile_type === 'SKILLED_TRADE') {

              <div class="p-3.5 rounded-2xl bg-[#F5F5F7] border border-black/10 space-y-2.5">

                <div class="flex items-center justify-between">

                  <span class="text-xs font-bold text-zinc-800 font-mono uppercase tracking-wider flex items-center gap-1.5">

                    <span>🔧</span> {{ drJefService.language() === 'EN' ? 'Technical & Operations Trade' : 'Oficio Técnico & Operativo' }}

                  </span>

                  <span class="text-[10px] text-blue-700 font-mono font-bold">{{ drJefService.language() === 'EN' ? 'Piecework / Workshop' : 'Destajo / Taller' }}</span>

                </div>



                <div>

                  <label class="text-[11px] text-zinc-600 block mb-1 font-medium">{{ drJefService.language() === 'EN' ? 'Exact Trade' : 'Oficio Exacto' }}</label>

                  <input

                    type="text"

                    [(ngModel)]="realitySeed.career_or_degree"

                    [placeholder]="drJefService.language() === 'EN' ? 'e.g. Mechanic, electrician, carpenter, driver, chef...' : 'ej. Mecánico automotriz, electricista, carpintero, chofer, cocinero...'"

                    class="w-full bg-white border border-black/15 rounded-xl px-3 py-1.5 text-xs text-zinc-900 focus:outline-none focus:border-[#FF5500]"

                  />

                </div>



                <div class="grid grid-cols-2 gap-2 text-xs">

                  <div>

                    <label class="text-[11px] text-zinc-600 block mb-1 font-medium">{{ drJefService.language() === 'EN' ? 'Modality' : 'Modalidad' }}</label>

                    <select

                      [(ngModel)]="realitySeed.trade_modality"

                      class="w-full bg-white border border-black/15 rounded-xl px-2 py-1.5 text-xs text-zinc-900 focus:outline-none focus:border-[#FF5500] font-medium cursor-pointer"

                    >

                      <option value="INDEPENDENT">{{ drJefService.language() === 'EN' ? 'Self-employed / Piecework' : 'Por cuenta propia / Destajo' }}</option>

                      <option value="EMPLOYED">{{ drJefService.language() === 'EN' ? 'Contracted / Fixed shop' : 'Contratado / Taller fijo' }}</option>

                    </select>

                  </div>

                  <div>

                    <label class="text-[11px] text-zinc-600 block mb-1 font-medium">{{ drJefService.language() === 'EN' ? 'Physical Wear' : 'Desgaste Físico' }}</label>

                    <select

                      [(ngModel)]="realitySeed.physical_labor_intensity"

                      class="w-full bg-white border border-black/15 rounded-xl px-2 py-1.5 text-xs text-zinc-900 focus:outline-none focus:border-[#FF5500] font-medium cursor-pointer"

                    >

                      <option value="HIGH">{{ drJefService.language() === 'EN' ? 'High (Strength, awkward postures)' : 'Alto (Fuerza, posturas forzadas)' }}</option>

                      <option value="MEDIUM">{{ drJefService.language() === 'EN' ? 'Medium (Mixed technical operation)' : 'Medio (Operación técnica mixta)' }}</option>

                      <option value="LOW">{{ drJefService.language() === 'EN' ? 'Low (Driving / Monitoring)' : 'Bajo (Conducción / Control)' }}</option>

                    </select>

                  </div>

                </div>



                <div class="grid grid-cols-2 gap-2 text-xs">

                  <div>

                    <label class="text-[11px] text-zinc-600 block mb-0.5 font-medium">{{ drJefService.language() === 'EN' ? 'Avg. Monthly Income (' + getCurrencySymbol() + ')' : 'Ingreso Mes Prom. (' + getCurrencySymbol() + ')' }}</label>

                    <input

                      type="number"

                      [(ngModel)]="realitySeed.finances.monthly_income"

                      class="w-full bg-white border border-black/15 rounded-xl px-2.5 py-1.5 font-mono text-zinc-900 font-bold focus:border-[#FF5500]"

                    />

                  </div>

                  <div>

                    <label class="text-[11px] text-zinc-600 block mb-0.5 font-medium">{{ drJefService.language() === 'EN' ? 'Total Monthly Expenses (' + getCurrencySymbol() + ')' : 'Gasto Mes Total (' + getCurrencySymbol() + ')' }}</label>

                    <input

                      type="number"

                      [(ngModel)]="realitySeed.finances.monthly_expenses"

                      class="w-full bg-white border border-black/15 rounded-xl px-2.5 py-1.5 font-mono text-zinc-900 font-bold focus:border-[#FF5500]"

                    />

                  </div>

                </div>

                <div class="grid grid-cols-2 gap-2 text-xs">

                  <div>

                    <label class="text-[11px] text-zinc-600 block mb-0.5 font-medium">{{ drJefService.language() === 'EN' ? 'Current Savings (' + getCurrencySymbol() + ')' : 'Ahorro Actual (' + getCurrencySymbol() + ')' }}</label>

                    <input

                      type="number"

                      min="0"

                      [(ngModel)]="realitySeed.finances.current_savings"

                      class="w-full bg-white border border-black/15 rounded-xl px-2.5 py-1.5 font-mono text-emerald-600 font-bold focus:border-[#FF5500]"

                    />

                  </div>

                  <div>

                    <label class="text-[11px] text-zinc-600 block mb-0.5 font-medium">{{ drJefService.language() === 'EN' ? 'Current Debt (' + getCurrencySymbol() + ')' : 'Deuda Actual (' + getCurrencySymbol() + ')' }}</label>

                    <input

                      type="number"

                      min="0"

                      [(ngModel)]="realitySeed.finances.current_debt"

                      class="w-full bg-white border border-black/15 rounded-xl px-2.5 py-1.5 font-mono text-red-600 font-bold focus:border-[#FF5500]"

                    />

                  </div>

                </div>

              </div>

            }



            <!-- CASO D: PROFESIONAL TITULADO / SUELDO FIJO -->

            @if (realitySeed.life_profile_type === 'TITLED_PROFESSIONAL') {

              <div class="p-3.5 rounded-2xl bg-[#F5F5F7] border border-black/10 space-y-2.5">

                <div class="flex items-center justify-between">

                  <span class="text-xs font-bold text-zinc-800 font-mono uppercase tracking-wider flex items-center gap-1.5">

                    <span>💼</span> {{ drJefService.language() === 'EN' ? 'Professional Career' : 'Carrera Profesional' }}

                  </span>

                  <span class="text-[10px] text-zinc-600 font-mono font-bold">{{ drJefService.language() === 'EN' ? 'Payroll / Contract' : 'Planilla / Contrato' }}</span>

                </div>



                <div>

                  <label class="text-[11px] text-zinc-600 block mb-1 font-medium">{{ drJefService.language() === 'EN' ? 'Exact Profession or Role' : 'Profesión o Cargo Exacto' }}</label>

                  <input

                    type="text"

                    [(ngModel)]="realitySeed.career_or_degree"

                    [placeholder]="drJefService.language() === 'EN' ? 'e.g. Senior Accountant, Civil Engineer, Teacher...' : 'ej. Contador Senior, Ingeniero Civil, Docente...'"

                    class="w-full bg-white border border-black/15 rounded-xl px-3 py-1.5 text-xs text-zinc-900 focus:outline-none focus:border-[#FF5500]"

                  />

                </div>



                <div class="grid grid-cols-2 gap-2 text-xs">

                  <div>

                    <label class="text-[11px] text-zinc-600 block mb-1 font-medium">{{ drJefService.language() === 'EN' ? 'Contract Type' : 'Tipo Contrato' }}</label>

                    <select

                      [(ngModel)]="realitySeed.contract_type"

                      class="w-full bg-white border border-black/15 rounded-xl px-2 py-1.5 text-xs text-zinc-900 focus:outline-none focus:border-[#FF5500] font-medium cursor-pointer"

                    >

                      <option value="PERMANENT">{{ drJefService.language() === 'EN' ? 'Permanent / Full-time' : 'Estable / Planilla' }}</option>

                      <option value="TEMPORARY">{{ drJefService.language() === 'EN' ? 'Temporary / Contractor' : 'Temporal / Locación' }}</option>

                    </select>

                  </div>

                  <div>

                    <label class="text-[11px] text-zinc-600 block mb-1 font-medium">{{ drJefService.language() === 'EN' ? 'Years of Experience' : 'Años Experiencia' }}</label>

                    <input

                      type="number"

                      min="0"

                      step="0.5"

                      [(ngModel)]="realitySeed.years_of_experience"

                      class="w-full bg-white border border-black/15 rounded-xl px-2.5 py-1.5 font-mono text-zinc-900 font-bold focus:border-[#FF5500]"

                    />

                  </div>

                </div>



                <div class="grid grid-cols-2 gap-2 text-xs">

                  <div>

                    <label class="text-[11px] text-zinc-600 block mb-0.5 font-medium">{{ drJefService.language() === 'EN' ? 'Net Salary (' + getCurrencySymbol() + '/mo)' : 'Sueldo Neto (' + getCurrencySymbol() + '/m)' }}</label>

                    <input

                      type="number"

                      [(ngModel)]="realitySeed.finances.monthly_income"

                      class="w-full bg-white border border-black/15 rounded-xl px-2.5 py-1.5 font-mono text-zinc-900 font-bold focus:border-[#FF5500]"

                    />

                  </div>

                  <div>

                    <label class="text-[11px] text-zinc-600 block mb-0.5 font-medium">{{ drJefService.language() === 'EN' ? 'Monthly Expenses (' + getCurrencySymbol() + '/mo)' : 'Gasto Mes (' + getCurrencySymbol() + '/m)' }}</label>

                    <input

                      type="number"

                      [(ngModel)]="realitySeed.finances.monthly_expenses"

                      class="w-full bg-white border border-black/15 rounded-xl px-2.5 py-1.5 font-mono text-zinc-900 font-bold focus:border-[#FF5500]"

                    />

                  </div>

                </div>

                <div class="grid grid-cols-2 gap-2 text-xs">

                  <div>

                    <label class="text-[11px] text-zinc-600 block mb-0.5 font-medium">{{ drJefService.language() === 'EN' ? 'Current Savings (' + getCurrencySymbol() + ')' : 'Ahorro Actual (' + getCurrencySymbol() + ')' }}</label>

                    <input

                      type="number"

                      min="0"

                      [(ngModel)]="realitySeed.finances.current_savings"

                      class="w-full bg-white border border-black/15 rounded-xl px-2.5 py-1.5 font-mono text-emerald-600 font-bold focus:border-[#FF5500]"

                    />

                  </div>

                  <div>

                    <label class="text-[11px] text-zinc-600 block mb-0.5 font-medium">{{ drJefService.language() === 'EN' ? 'Current Debt (' + getCurrencySymbol() + ')' : 'Deuda Actual (' + getCurrencySymbol() + ')' }}</label>

                    <input

                      type="number"

                      min="0"

                      [(ngModel)]="realitySeed.finances.current_debt"

                      class="w-full bg-white border border-black/15 rounded-xl px-2.5 py-1.5 font-mono text-red-600 font-bold focus:border-[#FF5500]"

                    />

                  </div>

                </div>

              </div>

            }



            <!-- CASO E: ESTUDIANTE UNIVERSITARIO O TÉCNICO -->

            @if (realitySeed.life_profile_type === 'UNIVERSITY_OR_TECH_STUDENT') {

              <div class="p-3.5 rounded-2xl bg-[#F5F5F7] border border-black/10 space-y-2.5">

                <div class="flex items-center justify-between">

                  <span class="text-xs font-bold text-zinc-800 font-mono uppercase tracking-wider flex items-center gap-1.5">

                    <span>🎓</span> {{ drJefService.language() === 'EN' ? 'Academic Transition & Thesis' : 'Transición Académica & Tesis' }}

                  </span>

                  <span class="text-[10px] text-[#FF5500] font-mono font-bold">{{ drJefService.language() === 'EN' ? 'Phase Transition' : 'Cambio de Fase' }}</span>

                </div>



                <div>

                  <label class="text-[11px] text-zinc-600 block mb-1 font-medium">{{ drJefService.language() === 'EN' ? 'Degree or Major' : 'Carrera o Grado' }}</label>

                  <input

                    type="text"

                    [(ngModel)]="realitySeed.career_or_degree"

                    [placeholder]="drJefService.language() === 'EN' ? 'e.g. Systems Engineering, Business Admin...' : 'ej. Ingeniería de Sistemas, Administración...'"

                    class="w-full bg-white border border-black/15 rounded-xl px-3 py-1.5 text-xs text-zinc-900 focus:outline-none focus:border-[#FF5500]"

                  />

                </div>



                <div>

                  <label class="text-[11px] text-zinc-600 block mb-1 font-medium">{{ drJefService.language() === 'EN' ? 'University or College' : 'Universidad o Instituto' }}</label>

                  <input

                    type="text"

                    [(ngModel)]="realitySeed.university_or_institution"

                    [placeholder]="drJefService.language() === 'EN' ? 'e.g. State University, College...' : 'ej. UNCP, Univ. Continental, SENATI...'"

                    class="w-full bg-white border border-black/15 rounded-xl px-3 py-1.5 text-xs text-zinc-900 focus:outline-none focus:border-[#FF5500]"

                  />

                </div>



                <div class="grid grid-cols-2 gap-2 text-xs">

                  <div>

                    <label class="text-[11px] text-zinc-600 block mb-1 font-medium">{{ drJefService.language() === 'EN' ? 'Stage of Life' : 'Etapa de Vida' }}</label>

                    <select

                      [(ngModel)]="realitySeed.life_stage"

                      class="w-full bg-white border border-black/15 rounded-xl px-2 py-1.5 text-xs text-zinc-900 focus:outline-none focus:border-[#FF5500] font-medium cursor-pointer"

                    >

                      <option value="FINISHING_UNIVERSITY">{{ drJefService.language() === 'EN' ? 'Finishing Degree / Thesis candidate' : 'Terminando U / Tesista' }}</option>

                      <option value="WORKING_AND_FINISHING_UNI">{{ drJefService.language() === 'EN' ? 'Working & Finishing Degree' : 'Trabajando y terminando U' }}</option>

                      <option value="RECENT_GRADUATE">{{ drJefService.language() === 'EN' ? 'Recent Graduate' : 'Egresado reciente' }}</option>

                      <option value="STUDENT_MID_CAREER">{{ drJefService.language() === 'EN' ? 'Mid-degree Student' : 'Estudiante a mitad de carrera' }}</option>

                    </select>

                  </div>

                  <div>

                    <label class="text-[11px] text-zinc-600 block mb-1 font-medium">{{ drJefService.language() === 'EN' ? 'Months to Graduation' : 'Meses para Egresar' }}</label>

                    <input

                      type="number"

                      min="0"

                      max="72"

                      [(ngModel)]="realitySeed.months_to_graduation"

                      class="w-full bg-white border border-black/15 rounded-xl px-2.5 py-1.5 font-mono text-zinc-900 font-bold focus:border-[#FF5500]"

                    />

                  </div>

                </div>



                <div class="grid grid-cols-2 gap-2 text-xs">

                  <div>

                    <label class="text-[11px] text-zinc-600 block mb-0.5 font-medium">{{ drJefService.language() === 'EN' ? 'Income / Support (' + getCurrencySymbol() + '/mo)' : 'Ingreso / Apoyo (' + getCurrencySymbol() + '/m)' }}</label>

                    <input

                      type="number"

                      [(ngModel)]="realitySeed.finances.monthly_income"

                      class="w-full bg-white border border-black/15 rounded-xl px-2.5 py-1.5 font-mono text-zinc-900 font-bold focus:border-[#FF5500]"

                    />

                  </div>

                  <div>

                    <label class="text-[11px] text-zinc-600 block mb-0.5 font-medium">{{ drJefService.language() === 'EN' ? 'Monthly Expenses (' + getCurrencySymbol() + '/mo)' : 'Gasto Mes (' + getCurrencySymbol() + '/m)' }}</label>

                    <input

                      type="number"

                      [(ngModel)]="realitySeed.finances.monthly_expenses"

                      class="w-full bg-white border border-black/15 rounded-xl px-2.5 py-1.5 font-mono text-zinc-900 font-bold focus:border-[#FF5500]"

                    />

                  </div>

                </div>

                <div class="grid grid-cols-2 gap-2 text-xs">

                  <div>

                    <label class="text-[11px] text-zinc-600 block mb-0.5 font-medium">{{ drJefService.language() === 'EN' ? 'Current Savings (' + getCurrencySymbol() + ')' : 'Ahorro Actual (' + getCurrencySymbol() + ')' }}</label>

                    <input

                      type="number"

                      min="0"

                      [(ngModel)]="realitySeed.finances.current_savings"

                      class="w-full bg-white border border-black/15 rounded-xl px-2.5 py-1.5 font-mono text-emerald-600 font-bold focus:border-[#FF5500]"

                    />

                  </div>

                  <div>

                    <label class="text-[11px] text-zinc-600 block mb-0.5 font-medium">{{ drJefService.language() === 'EN' ? 'Current Debt (' + getCurrencySymbol() + ')' : 'Deuda Actual (' + getCurrencySymbol() + ')' }}</label>

                    <input

                      type="number"

                      min="0"

                      [(ngModel)]="realitySeed.finances.current_debt"

                      class="w-full bg-white border border-black/15 rounded-xl px-2.5 py-1.5 font-mono text-red-600 font-bold focus:border-[#FF5500]"

                    />

                  </div>

                </div>

              </div>

            }



            <!-- CASO F: DUEÑO DE NEGOCIO / EMPRENDEDOR / PYME -->

            @if (realitySeed.life_profile_type === 'BUSINESS_OWNER') {

              <div class="p-3.5 rounded-2xl bg-[#F5F5F7] border border-black/10 space-y-2.5">

                <div class="flex items-center justify-between">

                  <span class="text-xs font-bold text-zinc-800 font-mono uppercase tracking-wider flex items-center gap-1.5">

                    <span>🏢</span> {{ drJefService.language() === 'EN' ? 'Own Business & SME' : 'Negocio Propio & PYME' }}

                  </span>

                  <span class="text-[10px] text-purple-700 font-mono font-bold">{{ drJefService.language() === 'EN' ? 'Commercial / SME' : 'Comercial / PYME' }}</span>

                </div>



                <div>

                  <label class="text-[11px] text-zinc-600 block mb-1 font-medium">{{ drJefService.language() === 'EN' ? 'Business Line or Type' : 'Giro o Tipo de Negocio' }}</label>

                  <input

                    type="text"

                    [(ngModel)]="realitySeed.business_type"

                    [placeholder]="drJefService.language() === 'EN' ? 'e.g. Restaurant, hardware store, tailoring shop, pharmacy...' : 'ej. Restaurante, ferretería, taller de confección, farmacia...'"

                    class="w-full bg-white border border-black/15 rounded-xl px-3 py-1.5 text-xs text-zinc-900 focus:outline-none focus:border-[#FF5500]"

                  />

                </div>



                <div class="grid grid-cols-2 gap-2 text-xs">

                  <div>

                    <label class="text-[11px] text-zinc-600 block mb-1 font-medium">{{ drJefService.language() === 'EN' ? 'Net Monthly Sales ($)' : 'Ventas Netas Mes ($)' }}</label>

                    <input

                      type="number"

                      min="0"

                      [(ngModel)]="realitySeed.monthly_sales_net"

                      class="w-full bg-white border border-black/15 rounded-xl px-2.5 py-1.5 font-mono text-zinc-900 font-bold focus:border-[#FF5500]"

                    />

                  </div>

                  <div>

                    <label class="text-[11px] text-zinc-600 block mb-1 font-medium">{{ drJefService.language() === 'EN' ? 'Total Fixed Costs ($)' : 'Costos Fijos Totales ($)' }}</label>

                    <input

                      type="number"

                      min="0"

                      [(ngModel)]="realitySeed.finances.monthly_expenses"

                      class="w-full bg-white border border-black/15 rounded-xl px-2.5 py-1.5 font-mono text-zinc-900 font-bold focus:border-[#FF5500]"

                    />

                  </div>

                </div>



                <div class="grid grid-cols-2 gap-2 text-xs">

                  <div>

                    <label class="text-[11px] text-zinc-600 block mb-0.5 font-medium">{{ drJefService.language() === 'EN' ? 'Working Capital (' + getCurrencySymbol() + ')' : 'Capital Trabajo (' + getCurrencySymbol() + ')' }}</label>

                    <input

                      type="number"

                      [(ngModel)]="realitySeed.finances.current_savings"

                      class="w-full bg-white border border-black/15 rounded-xl px-2.5 py-1.5 font-mono text-emerald-600 font-bold focus:border-[#FF5500]"

                    />

                  </div>

                  <div>

                    <label class="text-[11px] text-zinc-600 block mb-0.5 font-medium">{{ drJefService.language() === 'EN' ? 'Commercial Debt (' + getCurrencySymbol() + ')' : 'Deuda Comercial (' + getCurrencySymbol() + ')' }}</label>

                    <input

                      type="number"

                      [(ngModel)]="realitySeed.finances.current_debt"

                      class="w-full bg-white border border-black/15 rounded-xl px-2.5 py-1.5 font-mono text-red-600 font-bold focus:border-[#FF5500]"

                    />

                  </div>

                </div>

              </div>

            }



            <!-- 5. METAS Y PROYECCIÓN CAUSAL (Corto, Mediano y Largo Plazo) -->
            <div class="p-3.5 rounded-2xl bg-amber-50/80 border border-amber-200/80 space-y-3">
              <div class="flex items-center justify-between">
                <span class="text-xs font-bold text-amber-900 font-mono uppercase tracking-wider flex items-center gap-1.5">
                  <span>🎯</span> {{ drJefService.language() === 'EN' ? 'Goals, Ideals & Causal Verification' : 'Metas, Ideales y Proyecciones' }}
                </span>
                <span class="text-[10px] px-2 py-0.5 rounded-full bg-amber-200 text-amber-900 font-mono font-bold">1A · 2-3A · 5A+</span>
              </div>

              <!-- 1 Año: Sueldo y Modalidad -->
              <div class="space-y-2">
                <div class="flex items-center justify-between">
                  <label class="text-[11px] text-amber-900 font-bold block">{{ drJefService.language() === 'EN' ? '1. Short-Term Goal (1 Year)' : '1. Meta a Corto Plazo (1 Año)' }}</label>
                  <span class="text-[10px] text-amber-700 font-mono">{{ drJefService.language() === 'EN' ? 'Immediate Horizon' : 'Horizonte Inmediato' }}</span>
                </div>
                <div class="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <label class="text-[11px] text-amber-900 block mb-1 font-medium">{{ drJefService.language() === 'EN' ? '1-Year Target Salary (' + getCurrencySymbol() + '/mo)' : 'Sueldo Meta 1A (' + getCurrencySymbol() + '/m)' }}</label>
                    <input
                      type="number"
                      min="0"
                      [(ngModel)]="realitySeed.target_monthly_salary_1y"
                      (ngModelChange)="onGoalFieldChanged()"
                      class="w-full bg-white border border-amber-300 rounded-xl px-2.5 py-1.5 font-mono text-zinc-900 font-bold focus:border-[#FF5500]"
                    />
                  </div>
                  <div>
                    <label class="text-[11px] text-amber-900 block mb-1 font-medium">{{ drJefService.language() === 'EN' ? 'Desired Modality' : 'Modalidad Deseada' }}</label>
                    <select
                      [(ngModel)]="realitySeed.work_modality_target"
                      class="w-full bg-white border border-amber-300 rounded-xl px-2 py-1.5 text-xs text-zinc-900 focus:outline-none focus:border-[#FF5500] font-medium cursor-pointer"
                    >
                      <option value="LOCAL_CITY">{{ drJefService.language() === 'EN' ? 'On-site in my city' : 'Presencial en mi ciudad' }}</option>
                      <option value="HYBRID_NATIONAL">{{ drJefService.language() === 'EN' ? 'National hybrid' : 'Híbrido nacional' }}</option>
                      <option value="REMOTE_GLOBAL">{{ drJefService.language() === 'EN' ? 'Remote national / global' : 'Remoto nacional / global' }}</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label class="text-[11px] text-amber-900 block mb-1 font-medium">{{ drJefService.language() === 'EN' ? 'Specific Goal Description' : 'Descripción Meta 1 Año' }}</label>
                  <textarea
                    [(ngModel)]="realitySeed.one_year_goal"
                    (ngModelChange)="onGoalFieldChanged()"
                    rows="2"
                    [placeholder]="drJefService.language() === 'EN' ? 'e.g. Secure formal contract/internship, graduate, double revenue...' : 'ej. Conseguir prácticas/trabajo formal en mi carrera, avanzar ciclos, generar ingresos estables...'"
                    class="w-full bg-white border border-amber-300 rounded-xl p-2.5 text-xs text-zinc-900 placeholder-zinc-400 focus:outline-none focus:border-[#FF5500] resize-none leading-relaxed"
                  ></textarea>
                </div>
              </div>

              <!-- 2 a 3 Años: Mediano Plazo -->
              <div class="pt-2 border-t border-amber-200/70 space-y-1.5">
                <div class="flex items-center justify-between">
                  <label class="text-[11px] text-amber-900 font-bold block">{{ drJefService.language() === 'EN' ? '2. Medium-Term Goals (2 to 3 Years)' : '2. Metas a Mediano Plazo (2 a 3 Años)' }}</label>
                  <span class="text-[10px] text-amber-700 font-mono">{{ drJefService.language() === 'EN' ? 'Consolidation' : 'Consolidación' }}</span>
                </div>
                <textarea
                  [(ngModel)]="realitySeed.medium_term_goals"
                  (ngModelChange)="onGoalFieldChanged()"
                  rows="2"
                  [placeholder]="drJefService.language() === 'EN' ? 'e.g. Finish degree/thesis, move out independently, build 6-month emergency fund, acquire tech workstation...' : 'ej. Titularme, mudarme a departamento propio/alquiler, tener fondo de emergencia de S/ 5,000, comprar laptop pro...'"
                  class="w-full bg-white border border-amber-300 rounded-xl p-2.5 text-xs text-zinc-900 placeholder-zinc-400 focus:outline-none focus:border-[#FF5500] resize-none leading-relaxed"
                ></textarea>
              </div>

              <!-- 5+ Años: Largo Plazo / Ideales -->
              <div class="pt-2 border-t border-amber-200/70 space-y-1.5">
                <div class="flex items-center justify-between">
                  <label class="text-[11px] text-amber-900 font-bold block">{{ drJefService.language() === 'EN' ? '3. Long-Term Ideals & Goals (5+ Years: Travel / Work Abroad)' : '3. Ideales y Metas a Largo Plazo (5+ Años: Viajar, Trabajar Fuera)' }}</label>
                  <span class="text-[10px] text-amber-700 font-mono">{{ drJefService.language() === 'EN' ? 'Aspirations' : 'Ideales de Vida' }}</span>
                </div>
                <textarea
                  [(ngModel)]="realitySeed.long_term_goals"
                  (ngModelChange)="onGoalFieldChanged()"
                  rows="2"
                  [placeholder]="drJefService.language() === 'EN' ? 'e.g. Travel and work abroad (Europe/Spain/Australia), buy own house/apartment, launch startup...' : 'ej. Viajar y radicar/trabajar en el extranjero (España, Europa o Canadá), comprar departamento, fundar empresa propia...'"
                  class="w-full bg-white border border-amber-300 rounded-xl p-2.5 text-xs text-zinc-900 placeholder-zinc-400 focus:outline-none focus:border-[#FF5500] resize-none leading-relaxed"
                ></textarea>
                <p class="text-[10px] text-amber-800/80 leading-tight">
                  {{ drJefService.language() === 'EN'
                    ? '💡 Mirror Future verifies if your current savings rate and timeline realistically support these long-term aspirations or if a capital/time gap needs intervention.'
                    : '💡 Mirror Future verifies with causal rigor if your savings rate and timeline realistically support these long-term goals.' }}
                </p>
              </div>
            </div>

            <!-- 5.1 HISTORIAL LABORAL Y TRAYECTORIA (EVENTOS LIFE2VEC) -->
            <div class="p-3.5 rounded-2xl bg-gradient-to-r from-zinc-900 to-zinc-950 text-white border border-white/10 space-y-3">
              <div class="flex items-center justify-between">
                <span class="text-xs font-bold text-white font-mono uppercase tracking-wider flex items-center gap-1.5">
                  <span class="text-[#FF5500]">📜</span> {{ drJefService.language() === 'EN' ? 'Career Milestones (Life2Vec Sequence)' : 'Historial Laboral (Eventos Life2Vec)' }}
                </span>
                <span class="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 font-mono font-bold">
                  {{ (realitySeed.past_career_events?.length || 0) }} {{ drJefService.language() === 'EN' ? 'events' : 'hitos' }}
                </span>
              </div>
              <p class="text-[10px] text-zinc-400 leading-tight">
                {{ drJefService.language() === 'EN'
                  ? 'Sequential milestones that feed the Life2Vec neural network to autocomplete your future career.'
                  : 'Secuencia de eventos que alimentan la red neuronal Life2Vec para autocompletar tu carrera y salario.' }}
              </p>

              <!-- Botones de Acción Rápida -->
              <div class="flex flex-wrap items-center gap-2 pt-1">
                <button
                  type="button"
                  (click)="synthesizeCareerHistory()"
                  class="px-2.5 py-1 rounded-lg bg-orange-600 hover:bg-[#FF5500] text-white text-[11px] font-bold transition flex items-center gap-1 cursor-pointer">
                  <span>⚡</span>
                  <span>{{ drJefService.language() === 'EN' ? 'Synthesize with AI' : 'Sintetizar con IA' }}</span>
                </button>

                <button
                  type="button"
                  (click)="isAddingCareerEvent.set(!isAddingCareerEvent())"
                  class="px-2.5 py-1 rounded-lg bg-white/10 hover:bg-white/20 text-white text-[11px] font-bold transition flex items-center gap-1 cursor-pointer border border-white/10">
                  <span>+</span>
                  <span>{{ drJefService.language() === 'EN' ? 'Add Milestone' : 'Agregar Hito' }}</span>
                </button>

                <label class="px-2.5 py-1 rounded-lg bg-white/10 hover:bg-white/20 text-zinc-300 hover:text-white text-[11px] font-medium transition flex items-center gap-1 cursor-pointer border border-white/10">
                  <span>📄</span>
                  <span>{{ drJefService.language() === 'EN' ? 'Upload CV (.txt)' : 'Subir CV (.txt)' }}</span>
                  <input type="file" (change)="onCvFileUploaded($event)" accept=".txt,.pdf,.docx" class="hidden" />
                </label>
              </div>

              <!-- Formulario de Agregar Hito -->
              @if (isAddingCareerEvent()) {
                <div class="p-3 rounded-xl bg-white/5 border border-white/10 space-y-2 text-xs">
                  <div class="grid grid-cols-3 gap-2">
                    <div>
                      <label class="text-[10px] text-zinc-400 block mb-0.5">Año</label>
                      <input
                        type="number"
                        [(ngModel)]="newCareerEvent.year"
                        class="w-full bg-black/50 border border-white/20 rounded-lg px-2 py-1 text-white font-mono text-xs"
                      />
                    </div>
                    <div>
                      <label class="text-[10px] text-zinc-400 block mb-0.5">Edad</label>
                      <input
                        type="number"
                        [(ngModel)]="newCareerEvent.age_at_event"
                        class="w-full bg-black/50 border border-white/20 rounded-lg px-2 py-1 text-white font-mono text-xs"
                      />
                    </div>
                    <div>
                      <label class="text-[10px] text-zinc-400 block mb-0.5">Tipo</label>
                      <select
                        [(ngModel)]="newCareerEvent.event_type"
                        class="w-full bg-black/50 border border-white/20 rounded-lg px-1.5 py-1 text-white text-xs">
                        <option value="EDUCATION">Educación</option>
                        <option value="FIRST_JOB">Primer Trabajo</option>
                        <option value="ROLE_CHANGE">Cambio de Rol</option>
                        <option value="SKILL_ACQUISITION">Habilidad</option>
                        <option value="FREELANCE_OR_BUSINESS">Negocio/Free</option>
                        <option value="CURRENT_STATE">Estado Actual</option>
                      </select>
                    </div>
                  </div>
                  <div>
                    <label class="text-[10px] text-zinc-400 block mb-0.5">Título / Puesto / Estudio</label>
                    <input
                      type="text"
                      [(ngModel)]="newCareerEvent.title_or_role"
                      placeholder="ej. Practicante TI, Asistente Comercial, Inicio Tesis..."
                      class="w-full bg-black/50 border border-white/20 rounded-lg px-2 py-1 text-white text-xs"
                    />
                  </div>
                  <div class="grid grid-cols-2 gap-2">
                    <div>
                      <label class="text-[10px] text-zinc-400 block mb-0.5">Ingreso Mensual</label>
                      <input
                        type="number"
                        [(ngModel)]="newCareerEvent.monthly_income"
                        class="w-full bg-black/50 border border-white/20 rounded-lg px-2 py-1 text-white font-mono text-xs"
                      />
                    </div>
                    <div>
                      <label class="text-[10px] text-zinc-400 block mb-0.5">Ciudad</label>
                      <input
                        type="text"
                        [(ngModel)]="newCareerEvent.location"
                        placeholder="ej. Huancayo, Lima"
                        class="w-full bg-black/50 border border-white/20 rounded-lg px-2 py-1 text-white text-xs"
                      />
                    </div>
                  </div>
                  <div class="flex justify-end gap-2 pt-1">
                    <button
                      type="button"
                      (click)="isAddingCareerEvent.set(false)"
                      class="px-2.5 py-1 rounded-lg bg-zinc-800 text-zinc-300 text-[11px] font-medium hover:bg-zinc-700">
                      Cancelar
                    </button>
                    <button
                      type="button"
                      (click)="addCareerEvent()"
                      class="px-3 py-1 rounded-lg bg-[#FF5500] text-white text-[11px] font-bold hover:bg-orange-600">
                      Guardar Hito
                    </button>
                  </div>
                </div>
              }

              <!-- Lista de Hitos Pasados -->
              @if (realitySeed.past_career_events && realitySeed.past_career_events.length > 0) {
                <div class="space-y-1.5 max-h-48 overflow-y-auto pr-1">
                  @for (ev of realitySeed.past_career_events; track $index) {
                    <div class="p-2 rounded-xl bg-white/5 border border-white/10 flex items-center justify-between gap-2 text-xs">
                      <div class="min-w-0 flex-1">
                        <div class="flex items-center gap-1.5 text-[10px] font-mono text-zinc-400">
                          <span class="text-orange-400 font-bold">{{ ev.year }}</span>
                          <span>•</span>
                          <span>{{ ev.age_at_event }} años</span>
                          <span>•</span>
                          <span class="px-1.5 py-0.2 rounded bg-white/10 text-zinc-300 uppercase text-[9px]">{{ ev.event_type }}</span>
                        </div>
                        <div class="text-white font-medium truncate text-[11px] mt-0.5">
                          {{ ev.title_or_role }}
                        </div>
                        @if (ev.monthly_income > 0) {
                          <div class="text-[10px] font-mono text-emerald-400">
                            {{ getCurrencySymbol() }} {{ ev.monthly_income | number:'1.0-0' }}/mes &bull; {{ ev.location }}
                          </div>
                        }
                      </div>
                      <button
                        type="button"
                        (click)="removeCareerEvent($index)"
                        title="Eliminar hito"
                        class="p-1 text-zinc-500 hover:text-rose-400 transition cursor-pointer text-xs">
                        ✕
                      </button>
                    </div>
                  }
                </div>
              } @else {
                <div class="p-2.5 rounded-xl bg-white/5 border border-dashed border-white/10 text-center text-[11px] text-zinc-400">
                  {{ drJefService.language() === 'EN'
                    ? 'No past events added yet. Click "Synthesize with AI" to generate automatically from your profile.'
                    : 'Aún no has agregado hitos. Haz clic en "Sintetizar con IA" para generarlos automáticamente según tu perfil.' }}
                </div>
              }
            </div>



            <!-- 6. SITUACIÓN DE VIVIENDA -->

            <div class="p-3 rounded-2xl bg-[#F5F5F7] border border-black/10 flex items-center justify-between gap-3 text-xs">

              <span class="text-zinc-700 font-medium text-xs">{{ drJefService.language() === 'EN' ? '🏠 Housing:' : '🏠 Vivienda:' }}</span>

              <select

                [(ngModel)]="realitySeed.housing_situation"

                class="bg-white border border-black/15 rounded-xl px-2.5 py-1.5 text-xs text-zinc-900 focus:outline-none focus:border-[#FF5500] font-medium cursor-pointer"

              >

                <option value="FAMILY_HOME">{{ drJefService.language() === 'EN' ? 'Family Home (No rent)' : 'Hogar Familiar (Sin alquiler)' }}</option>

                <option value="RENTING_INDEPENDENT">{{ drJefService.language() === 'EN' ? 'Rent / Independent Mortgage' : 'Alquiler / Hipoteca Indep.' }}</option>

              </select>

            </div>



            <!-- 7. IDENTIDAD PARA BÚSQUEDA REAL (100% Opcional) -->

            <div class="p-3.5 rounded-2xl bg-[#F5F5F7] border border-black/10 space-y-2">

              <div class="flex items-center justify-between">

                <span class="text-xs font-bold text-zinc-800 font-mono uppercase tracking-wider flex items-center gap-1.5">

                  <span>👤</span> {{ drJefService.language() === 'EN' ? 'Real Identity' : 'Identidad Real' }}

                </span>

                <span class="text-[10px] text-zinc-500 font-mono">{{ drJefService.language() === 'EN' ? '100% Optional' : '100% Opcional' }}</span>

              </div>

              <p class="text-[10px] text-zinc-500">

                {{ drJefService.language() === 'EN' ? 'If you lack a digital footprint or prefer privacy, the engine uses your city and trade to benchmark your environment.' : 'Si no tienes huella digital o prefieres privacidad, el motor usará tu ciudad y actividad para investigar tu entorno.' }}

              </p>

              <div class="grid grid-cols-1 gap-2">

                <div>

                  <label class="text-[11px] text-zinc-600 block mb-0.5 font-medium">{{ drJefService.language() === 'EN' ? 'Full Name' : 'Nombre y Apellido' }}</label>

                  <input

                    type="text"

                    [(ngModel)]="realitySeed.full_name"

                    [placeholder]="drJefService.language() === 'EN' ? 'e.g. Alex Smith (Optional)' : 'ej. Tu Nombre Completo (Opcional)'"

                    class="w-full bg-white border border-black/15 rounded-xl px-3 py-1.5 text-xs text-zinc-900 focus:outline-none focus:border-[#FF5500]"

                  />

                </div>

              </div>

            </div>



            <!-- 8. FAMILIA, ENTORNO Y CÓMO ERES TÚ (COLAPSABLE) -->

            <div class="p-3.5 rounded-2xl bg-[#F5F5F7] border border-black/10 space-y-2.5">

              <button

                type="button"

                (click)="toggleFamilySection()"

                class="w-full flex items-center justify-between text-left cursor-pointer group"

              >

                <div class="flex items-center gap-1.5">

                  <span>👨‍👩‍👧</span>

                  <span class="text-xs font-bold text-zinc-800 font-mono uppercase tracking-wider group-hover:text-[#FF5500] transition">

                    {{ drJefService.language() === 'EN' ? 'Family, Environment & Who You Are' : 'Familia, Entorno y Cómo Eres Tú' }}

                  </span>

                </div>

                <span class="text-xs font-mono text-zinc-400 group-hover:text-black transition">

                  {{ isFamilySectionOpen() ? '▲' : '▼' }}

                </span>

              </button>



              @if (isFamilySectionOpen()) {

                <div class="space-y-3 pt-1 border-t border-black/5 text-xs">

                  

                  <!-- BOTÓN GENERAR PREGUNTAS DINÁMICAS (Para usuarios bloqueados) -->

                  <div class="p-2.5 bg-gradient-to-r from-orange-50 to-amber-50 rounded-xl border border-orange-200/60">

                    <div class="flex items-center justify-between gap-2">

                      <div class="text-[11px] text-zinc-700">

                        <span class="font-bold text-zinc-900">{{ drJefService.language() === 'EN' ? 'Need inspiration?' : '¿No sabes qué escribir?' }}</span>

                        <p class="text-[10px] text-zinc-500 leading-tight">

                          {{ drJefService.language() === 'EN' ? 'AI asks tailored questions to discover your reality' : 'Haz click para que la IA formule preguntas sobre tu situación' }}

                        </p>

                      </div>

                      <button

                        type="button"

                        (click)="generateDynamicQuestions()"

                        [disabled]="isGeneratingQuestions()"

                        class="px-2.5 py-1.5 bg-[#FF5500] hover:bg-[#E04B00] text-white rounded-lg text-[10px] font-bold tracking-wide transition shadow-sm flex items-center gap-1 shrink-0 cursor-pointer disabled:opacity-50"

                      >

                        @if (isGeneratingQuestions()) {

                          <span class="animate-spin text-xs">⏳</span>

                          <span>{{ drJefService.language() === 'EN' ? 'Thinking...' : 'Pensando...' }}</span>

                        } @else {

                          <span>✨</span>

                          <span>{{ drJefService.language() === 'EN' ? 'Ask Me Questions' : 'Descubrir con IA' }}</span>

                        }

                      </button>

                    </div>



                    <!-- Chips de preguntas generadas -->

                    @if (discoveryQuestions().length > 0) {

                      <div class="mt-2.5 space-y-1.5 pt-2 border-t border-orange-200/50">

                        <span class="text-[10px] font-bold text-orange-950 uppercase tracking-wider block">

                          {{ drJefService.language() === 'EN' ? '💡 Discovery Prompts (click to add to your answers):' : '💡 Preguntas Guía (haz click para responderlas):' }}

                        </span>

                        <div class="space-y-1">

                          @for (q of discoveryQuestions(); track $index) {

                            <button

                              type="button"

                              (click)="insertDiscoveryQuestion(q)"

                              class="w-full text-left p-1.5 rounded-lg bg-white/90 hover:bg-white text-[11px] text-zinc-800 border border-orange-200/60 transition cursor-pointer flex items-start gap-1.5 group"

                            >

                              <span class="text-[#FF5500] group-hover:scale-110 transition font-bold shrink-0">💬</span>

                              <span class="leading-tight">{{ q }}</span>

                            </button>

                          }

                        </div>

                      </div>

                    }

                  </div>



                  <!-- Pregunta 1: Familia y Hogar -->

                  <div>

                    <div class="flex items-center justify-between mb-1">

                      <label class="text-[11px] text-zinc-700 block font-bold">

                        {{ drJefService.language() === 'EN' ? '1. Your Family & Home' : '1. Tu Familia y Hogar' }}

                      </label>

                      <button

                        type="button"

                        (click)="toggleSpeechRecognition('open_family_and_dependents')"

                        [class]="listeningField() === 'open_family_and_dependents' ? 'bg-red-500 text-white animate-pulse' : 'bg-zinc-200 hover:bg-zinc-300 text-zinc-700'"

                        class="px-2 py-0.5 rounded-md text-[10px] font-bold flex items-center gap-1 transition cursor-pointer"

                        [title]="drJefService.language() === 'EN' ? 'Dictate by voice' : 'Dictar por voz'"

                      >

                        <span>🎙️</span>

                        <span>{{ listeningField() === 'open_family_and_dependents' ? (drJefService.language() === 'EN' ? 'Listening...' : 'Escuchando...') : (drJefService.language() === 'EN' ? 'Voice' : 'Dictar') }}</span>

                      </button>

                    </div>

                    <p class="text-[10px] text-zinc-500 mb-1 leading-snug">

                      {{ drJefService.language() === 'EN'

                        ? 'Who do you live with today, who depends on you (financially or for care), and what is the daily atmosphere like at home?'

                        : '¿Con quiénes vives hoy, quiénes dependen de ti (en dinero o cuidados) y cómo es el ambiente en tu casa día a día?'

                      }}

                    </p>

                    <textarea

                      [(ngModel)]="realitySeed.open_family_and_dependents"

                      rows="2"

                      [placeholder]="drJefService.language() === 'EN'

                        ? 'e.g. Living with my parents and contributing to bills; supportive but occasional financial tension...'

                        : 'Ej: Vivo con mis padres y apoyo con los gastos de la casa; hay cariño pero a veces mucha presión económica...'

                      "

                      class="w-full bg-white border border-black/15 rounded-xl p-2.5 text-xs text-zinc-900 placeholder-zinc-400 focus:outline-none focus:border-[#FF5500] resize-none leading-relaxed"

                    ></textarea>

                  </div>



                  <!-- Pregunta 2: Pareja y Círculo Cercano -->

                  <div>

                    <div class="flex items-center justify-between mb-1">

                      <label class="text-[11px] text-zinc-700 block font-bold">

                        {{ drJefService.language() === 'EN' ? '2. Romantic Situation & Close Circle' : '2. Tu Pareja y Círculo Cercano' }}

                      </label>

                      <button

                        type="button"

                        (click)="toggleSpeechRecognition('open_relationships_and_friends')"

                        [class]="listeningField() === 'open_relationships_and_friends' ? 'bg-red-500 text-white animate-pulse' : 'bg-zinc-200 hover:bg-zinc-300 text-zinc-700'"

                        class="px-2 py-0.5 rounded-md text-[10px] font-bold flex items-center gap-1 transition cursor-pointer"

                        [title]="drJefService.language() === 'EN' ? 'Dictate by voice' : 'Dictar por voz'"

                      >

                        <span>🎙️</span>

                        <span>{{ listeningField() === 'open_relationships_and_friends' ? (drJefService.language() === 'EN' ? 'Listening...' : 'Escuchando...') : (drJefService.language() === 'EN' ? 'Voice' : 'Dictar') }}</span>

                      </button>

                    </div>

                    <p class="text-[10px] text-zinc-500 mb-1 leading-snug">

                      {{ drJefService.language() === 'EN'

                        ? 'What is your current romantic situation, and how do your friends or close circle influence your time, mood, and spending?'

                        : '¿Cómo está hoy tu situación sentimental y cómo influyen tus amigos o entorno cercano en tu tiempo, ánimo y gastos?'

                      }}

                    </p>

                    <textarea

                      [(ngModel)]="realitySeed.open_relationships_and_friends"

                      rows="2"

                      [placeholder]="drJefService.language() === 'EN'

                        ? 'e.g. Single and focused on work; or in a relationship that gives me stability/distraction...'

                        : 'Ej: Estoy soltera enfocada en mis cosas, aunque salgo de vez en cuando; o estoy en una relación que últimamente me genera dudas...'

                      "

                      class="w-full bg-white border border-black/15 rounded-xl p-2.5 text-xs text-zinc-900 placeholder-zinc-400 focus:outline-none focus:border-[#FF5500] resize-none leading-relaxed"

                    ></textarea>

                  </div>



                  <!-- Pregunta 3: Cómo eres tú y cómo reaccionas -->

                  <div>

                    <div class="flex items-center justify-between mb-1">

                      <label class="text-[11px] text-zinc-700 block font-bold">

                        {{ drJefService.language() === 'EN' ? '3. Character & Stress Reaction' : '3. Cómo Eres Tú y Cómo Reaccionas' }}

                      </label>

                      <button

                        type="button"

                        (click)="toggleSpeechRecognition('open_personality_and_habits')"

                        [class]="listeningField() === 'open_personality_and_habits' ? 'bg-red-500 text-white animate-pulse' : 'bg-zinc-200 hover:bg-zinc-300 text-zinc-700'"

                        class="px-2 py-0.5 rounded-md text-[10px] font-bold flex items-center gap-1 transition cursor-pointer"

                        [title]="drJefService.language() === 'EN' ? 'Dictate by voice' : 'Dictar por voz'"

                      >

                        <span>🎙️</span>

                        <span>{{ listeningField() === 'open_personality_and_habits' ? (drJefService.language() === 'EN' ? 'Listening...' : 'Escuchando...') : (drJefService.language() === 'EN' ? 'Voice' : 'Dictar') }}</span>

                      </button>

                    </div>

                    <p class="text-[10px] text-zinc-500 mb-1 leading-snug">

                      {{ drJefService.language() === 'EN'

                        ? 'How would you describe yourself? How do you react under intense stress or tight finances, and which habit is hardest to control?'

                        : '¿Cómo te describes como persona? ¿Cómo reaccionas cuando estás bajo mucho estrés o falta dinero, y qué hábito te cuesta más controlar?'

                      }}

                    </p>

                    <textarea

                      [(ngModel)]="realitySeed.open_personality_and_habits"

                      rows="2"

                      [placeholder]="drJefService.language() === 'EN'

                        ? 'e.g. Resilient and hardworking, but prone to overthinking when cash is tight...'

                        : 'Ej: Soy muy trabajador pero me gana la ansiedad cuando las cosas salen mal; suelo gastar de más cuando me estreso...'

                      "

                      class="w-full bg-white border border-black/15 rounded-xl p-2.5 text-xs text-zinc-900 placeholder-zinc-400 focus:outline-none focus:border-[#FF5500] resize-none leading-relaxed"

                    ></textarea>

                  </div>



                  <!-- Dependientes y Chips de Rasgos -->

                  <div class="pt-2 border-t border-black/5 space-y-2">

                    <div class="flex items-center justify-between">

                      <label class="text-[11px] text-zinc-600 font-medium">

                        {{ drJefService.language() === 'EN' ? 'Economic dependents count:' : 'Personas que dependen de ti:' }}

                      </label>

                      <input

                        type="number"

                        min="0"

                        max="10"

                        [(ngModel)]="realitySeed.dependents_count"

                        class="w-16 bg-white border border-black/15 rounded-lg px-2 py-1 font-mono text-zinc-900 font-bold text-center text-xs focus:border-[#FF5500]"

                      />

                    </div>



                    <div>

                      <label class="text-[10px] text-zinc-500 uppercase tracking-wider block mb-1 font-bold">

                        {{ drJefService.language() === 'EN' ? 'Traits (optional tags):' : 'Rasgos que te identifican (opcional):' }}

                      </label>

                      <div class="flex flex-wrap gap-1.5">

                        <button

                          type="button"

                          (click)="togglePersonalityTrait('RESILIENT')"

                          [class]="isTraitSelected('RESILIENT') ? 'bg-black text-white border-black font-bold' : 'bg-white text-zinc-700 border-black/15 hover:border-black'"

                          class="px-2.5 py-1 rounded-lg text-[11px] border transition cursor-pointer"

                        >

                          🛡️ {{ drJefService.language() === 'EN' ? 'Resilient' : 'Resiliente' }}

                        </button>

                        <button

                          type="button"

                          (click)="togglePersonalityTrait('DISCIPLINED')"

                          [class]="isTraitSelected('DISCIPLINED') ? 'bg-black text-white border-black font-bold' : 'bg-white text-zinc-700 border-black/15 hover:border-black'"

                          class="px-2.5 py-1 rounded-lg text-[11px] border transition cursor-pointer"

                        >

                          ⚡ {{ drJefService.language() === 'EN' ? 'Disciplined' : 'Disciplinado' }}

                        </button>

                        <button

                          type="button"

                          (click)="togglePersonalityTrait('PROCRASTINATOR')"

                          [class]="isTraitSelected('PROCRASTINATOR') ? 'bg-amber-500 text-white border-amber-600 font-bold' : 'bg-white text-zinc-700 border-black/15 hover:border-black'"

                          class="px-2.5 py-1 rounded-lg text-[11px] border transition cursor-pointer"

                        >

                          ⏳ {{ drJefService.language() === 'EN' ? 'Procrastinator' : 'Procrastinador' }}

                        </button>

                        <button

                          type="button"

                          (click)="togglePersonalityTrait('ANXIOUS_OVERTHINKER')"

                          [class]="isTraitSelected('ANXIOUS_OVERTHINKER') ? 'bg-red-500 text-white border-red-600 font-bold' : 'bg-white text-zinc-700 border-black/15 hover:border-black'"

                          class="px-2.5 py-1 rounded-lg text-[11px] border transition cursor-pointer"

                        >

                          🌀 {{ drJefService.language() === 'EN' ? 'Overthinker' : 'Pensador Ansioso' }}

                        </button>

                        <button

                          type="button"

                          (click)="togglePersonalityTrait('IMPULSIVE_SPENDER')"

                          [class]="isTraitSelected('IMPULSIVE_SPENDER') ? 'bg-red-500 text-white border-red-600 font-bold' : 'bg-white text-zinc-700 border-black/15 hover:border-black'"

                          class="px-2.5 py-1 rounded-lg text-[11px] border transition cursor-pointer"

                        >

                          💸 {{ drJefService.language() === 'EN' ? 'Impulsive Spender' : 'Gasto Impulsivo' }}

                        </button>

                        <button

                          type="button"

                          (click)="togglePersonalityTrait('AMBITIOUS')"

                          [class]="isTraitSelected('AMBITIOUS') ? 'bg-purple-600 text-white border-purple-700 font-bold' : 'bg-white text-zinc-700 border-black/15 hover:border-black'"

                          class="px-2.5 py-1 rounded-lg text-[11px] border transition cursor-pointer"

                        >

                          🚀 {{ drJefService.language() === 'EN' ? 'Ambitious' : 'Ambicioso' }}

                        </button>

                        <button

                          type="button"

                          (click)="togglePersonalityTrait('INTROVERT')"

                          [class]="isTraitSelected('INTROVERT') ? 'bg-blue-600 text-white border-blue-700 font-bold' : 'bg-white text-zinc-700 border-black/15 hover:border-black'"

                          class="px-2.5 py-1 rounded-lg text-[11px] border transition cursor-pointer"

                        >

                          🧘 {{ drJefService.language() === 'EN' ? 'Introvert' : 'Introvertido' }}

                        </button>

                      </div>

                    </div>

                  </div>



                </div>

              }

            </div>



            <!-- 3. Presupuesto Diario de 24 Horas -->

            <div class="p-3.5 rounded-2xl bg-[#F5F5F7] border border-black/10 space-y-2.5">

              <div class="flex items-center justify-between">

                <span class="text-xs font-bold text-zinc-800 font-mono uppercase tracking-wider flex items-center gap-1.5">

                  <span>⏱️</span> {{ drJefService.language() === 'EN' ? 'Daily Budget' : 'Presupuesto Diario' }}

                </span>

                <span class="text-[11px] font-mono px-2 py-0.5 rounded-full font-bold"

                  [ngClass]="totalAccountedHours() <= 24 ? 'bg-zinc-200 text-zinc-800' : 'bg-red-100 text-red-800 border border-red-300'">

                  {{ totalAccountedHours() }}h / 24h

                </span>

              </div>



              <div class="space-y-2 text-xs">

                <!-- Sueño -->

                <div class="flex items-center justify-between gap-2">

                  <span class="text-zinc-600 text-xs w-24">{{ drJefService.language() === 'EN' ? '😴 Sleep:' : '😴 Sueño:' }}</span>

                  <input

                    type="range"

                    min="0"

                    max="12"

                    step="0.5"

                    [(ngModel)]="realitySeed.time_use.sleep_hours"

                    class="flex-1 accent-[#FF5500] bg-zinc-200 h-1.5 rounded cursor-pointer"

                  />

                  <span class="font-mono text-black font-bold w-10 text-right">{{ realitySeed.time_use.sleep_hours }}h</span>

                </div>



                <!-- Trabajo -->

                <div class="flex items-center justify-between gap-2">

                  <span class="text-zinc-600 text-xs w-24">{{ drJefService.language() === 'EN' ? '💼 Work:' : '💼 Trabajo:' }}</span>

                  <input

                    type="range"

                    min="0"

                    max="16"

                    step="0.5"

                    [(ngModel)]="realitySeed.time_use.work_hours"

                    class="flex-1 accent-black bg-zinc-200 h-1.5 rounded cursor-pointer"

                  />

                  <span class="font-mono text-black font-bold w-10 text-right">{{ realitySeed.time_use.work_hours }}h</span>

                </div>



                <!-- Tesis / Proyecto -->

                <div class="flex items-center justify-between gap-2">

                  <span class="text-zinc-600 text-xs w-24">{{ drJefService.language() === 'EN' ? '🎯 Project:' : '🎯 Proyecto:' }}</span>

                  <input

                    type="range"

                    min="0"

                    max="12"

                    step="0.5"

                    [(ngModel)]="realitySeed.time_use.study_project_hours"

                    class="flex-1 accent-[#FF5500] bg-zinc-200 h-1.5 rounded cursor-pointer"

                  />

                  <span class="font-mono text-[#FF5500] font-bold w-10 text-right">{{ realitySeed.time_use.study_project_hours }}h</span>

                </div>



                <!-- Distracción en Pantalla -->

                <div class="flex items-center justify-between gap-2">

                  <span class="text-zinc-600 text-xs w-24">{{ drJefService.language() === 'EN' ? '📱 Screen Time:' : '📱 Pantalla Ocio:' }}</span>

                  <input

                    type="range"

                    min="0"

                    max="12"

                    step="0.5"

                    [(ngModel)]="realitySeed.time_use.screen_time_lost_hours"

                    class="flex-1 accent-red-600 bg-zinc-200 h-1.5 rounded cursor-pointer"

                  />

                  <span class="font-mono text-red-600 font-bold w-10 text-right">{{ realitySeed.time_use.screen_time_lost_hours }}h</span>

                </div>

              </div>

            </div>




        </div>
      </ng-template>

      <!-- ======================================================== -->
      <!-- FASE 1: MODO CONVERSACIÓN CENTRADO (CHATEAR / PREDECIR) -->
      <!-- ======================================================== -->
      @if (!futureResponse() && !isLoading()) {
        <div class="max-w-3xl mx-auto space-y-6 py-2">
          
          <!-- REGRESO A HOME EDITORIAL Y SELECTOR DE IDIOMA SINCRONIZADO -->
          <div class="flex items-center justify-between gap-4 pb-1">
            <button
              type="button"
              (click)="goHome()"
              class="inline-flex items-center gap-2.5 px-5 py-2.5 rounded-full border border-neutral-900 bg-neutral-900 text-white hover:bg-neutral-800 text-xs font-bold uppercase tracking-[0.18em] transition-all shadow-md active:scale-95 cursor-pointer group">
              <span class="group-hover:-translate-x-1 transition-transform">←</span>
              <span>{{ drJefService.language() === 'EN' ? 'Return to Home' : 'Volver a la Portada' }}</span>
            </button>

            <div class="flex items-center gap-2 bg-white/95 px-4 py-2 rounded-full border border-black/10 shadow-sm text-xs font-mono">
              <span class="text-zinc-500 font-sans text-[11px] font-medium">{{ drJefService.language() === 'EN' ? 'Language:' : 'Idioma:' }}</span>
              <button
                type="button"
                (click)="drJefService.setLanguage('EN')"
                [class.font-bold]="drJefService.language() === 'EN'"
                [class.text-black]="drJefService.language() === 'EN'"
                class="text-zinc-400 hover:text-black cursor-pointer px-1">
                EN
              </button>
              <span class="text-zinc-300">/</span>
              <button
                type="button"
                (click)="drJefService.setLanguage('ES')"
                [class.font-bold]="drJefService.language() === 'ES'"
                [class.text-black]="drJefService.language() === 'ES'"
                class="text-zinc-400 hover:text-black cursor-pointer px-1">
                ES
              </button>
            </div>
          </div>

          <!-- Header editorial del chat -->
          <div class="p-6 sm:p-7 bg-white/90 border border-black/10 rounded-3xl shadow-sm space-y-3 backdrop-blur-md">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <span class="w-3 h-3 rounded-full bg-[#FF5500]"></span>
                <span class="text-xs font-mono font-bold tracking-wider uppercase text-black">
                  MIRROR FUTURE &bull; {{ drJefService.language() === 'EN' ? 'AI DISCOVERY CHAT' : 'DESCUBRIMIENTO CONVERSACIONAL' }}
                </span>
              </div>
              <div class="flex items-center gap-1.5 p-1 bg-zinc-100 rounded-xl border border-black/10 text-xs">
                <button
                  type="button"
                  (click)="switchInputMode('INTERVIEW')"
                  [class.bg-black]="activeInputMode() === 'INTERVIEW'"
                  [class.text-white]="activeInputMode() === 'INTERVIEW'"
                  [class.text-zinc-600]="activeInputMode() !== 'INTERVIEW'"
                  class="px-3 py-1.5 rounded-lg font-bold transition cursor-pointer">
                  💬 {{ drJefService.language() === 'EN' ? 'Chat' : 'Chat IA' }}
                </button>
                <button
                  type="button"
                  (click)="switchInputMode('FORM')"
                  [class.bg-black]="activeInputMode() === 'FORM'"
                  [class.text-white]="activeInputMode() === 'FORM'"
                  [class.text-zinc-600]="activeInputMode() !== 'FORM'"
                  class="px-3 py-1.5 rounded-lg font-bold transition cursor-pointer">
                  ⚙️ {{ drJefService.language() === 'EN' ? 'Manual' : 'Manual' }}
                </button>
              </div>
            </div>
            <h2 class="text-2xl sm:text-3xl font-black text-zinc-900 tracking-tight">
              {{ drJefService.language() === 'EN' ? 'Tell me who you are. We project your life at 1M, 6M & 1Y.' : 'Cuéntame quién eres. Proyectamos tu vida a 1M, 6M y 1 Año.' }}
            </h2>
            <p class="text-xs sm:text-sm text-zinc-600 leading-relaxed">
              {{ drJefService.language() === 'EN' ? 'Chat naturally or speak with your voice. Mirror Future synthesizes your real dossier and executes a Monte Carlo projection.' : 'Conversa con naturalidad o dicta con tu voz. Mirror Future sintetiza tu realidad en un dossier completo y ejecuta una proyección causal Monte Carlo de 1,000 trayectorias.' }}
            </p>
          </div>

          <!-- Contenido: Chat o Formulario Manual -->
          @if (activeInputMode() === 'INTERVIEW') {
            @if (!dossierGenerated()) {
              <div class="bg-white/95 border border-black/10 rounded-3xl p-5 sm:p-7 shadow-xl space-y-5">
                  <!-- FICHA DE REALIDAD IDENTIFICADA EN TIEMPO REAL -->
                  <div class="p-3.5 rounded-2xl bg-zinc-950 text-white border border-white/10 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-lg">
                    <div class="flex items-center gap-3 min-w-0">
                      <div class="w-10 h-10 rounded-xl bg-orange-500/20 border border-orange-500/40 flex items-center justify-center text-xl shrink-0">
                        {{ getProfileIcon(realitySeed.life_profile_type) }}
                      </div>
                      <div class="min-w-0">
                        <div class="flex items-center gap-2 flex-wrap">
                          <span class="text-xs font-black tracking-wide text-white truncate">
                            {{ realitySeed.full_name || (drJefService.language() === 'EN' ? 'Discovering identity...' : 'Identificándote en el chat...') }}
                          </span>
                          @if (realitySeed.age) {
                            <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-orange-500/20 text-orange-300 border border-orange-500/40 font-bold">
                              {{ realitySeed.age }} {{ drJefService.language() === 'EN' ? 'yo' : 'años' }}
                            </span>
                          }
                          @if (realitySeed.location.city) {
                            <span class="text-[10px] font-mono text-zinc-400">
                              📍 {{ realitySeed.location.city }}, {{ realitySeed.location.country || 'PE' }}
                            </span>
                          }
                        </div>
                        <div class="text-[11px] text-[#FF5500] font-bold truncate mt-0.5 flex items-center gap-1.5">
                          <span>{{ getProfileLabel(realitySeed.life_profile_type) }}</span>
                          @if (realitySeed.occupation) {
                            <span class="text-zinc-500">&bull;</span>
                            <span class="text-zinc-300 font-medium">{{ realitySeed.occupation }}</span>
                          }
                        </div>
                      </div>
                    </div>
                    <button
                      type="button"
                      (click)="switchInputMode('FORM')"
                      class="px-3 py-1.5 rounded-xl bg-white/10 hover:bg-[#FF5500] text-zinc-200 hover:text-white text-xs font-mono font-bold transition cursor-pointer shrink-0 border border-white/15 flex items-center gap-1.5">
                      <span>⚙️</span>
                      <span>{{ drJefService.language() === 'EN' ? 'View in Manual' : 'Ver datos en Manual' }}</span>
                    </button>
                  </div>

                  <!-- Barra de progreso de descubrimiento y pilares -->
                  <div class="p-3.5 rounded-2xl bg-gradient-to-r from-orange-50 to-amber-50 border border-orange-200/70 space-y-2">
                    <div class="flex items-center justify-between text-xs font-bold text-zinc-800">
                      <span class="flex items-center gap-1.5">
                        <span class="text-[#FF5500]">✦</span>
                        <span>{{ drJefService.language() === 'EN' ? 'Reality Knowledge' : 'Conocimiento de tu realidad' }}: {{ interviewCompletenessPct() }}%</span>
                      </span>
                      <span class="font-mono text-[11px] text-zinc-500">{{ getMissingPillarsText() }}</span>
                    </div>
                    <div class="w-full bg-zinc-200 h-2 rounded-full overflow-hidden">
                      <div
                        class="bg-gradient-to-r from-[#FF5500] to-amber-500 h-2 rounded-full transition-all duration-500 ease-out"
                        [style.width.%]="interviewCompletenessPct()">
                      </div>
                    </div>
                  </div>

                  <!-- Autocompletado rápido con archivo, Foto de Referencia y CV Laboral -->
                  <div class="grid grid-cols-1 sm:grid-cols-3 gap-2">
                    <div class="p-2.5 rounded-xl bg-zinc-50 border border-black/10 flex items-center justify-between gap-2">
                      <div class="flex items-center gap-2 text-xs text-zinc-600 truncate min-w-0">
                        <span class="text-base shrink-0">📎</span>
                        <span class="truncate">{{ uploadedFileName() || (drJefService.language() === 'EN' ? 'WhatsApp / Cal' : 'WhatsApp / Cal') }}</span>
                      </div>
                      <label class="px-2.5 py-1 rounded-lg bg-black text-white text-[11px] font-bold hover:bg-[#FF5500] transition cursor-pointer shrink-0">
                        <span>{{ drJefService.language() === 'EN' ? 'Upload' : 'Subir' }}</span>
                        <input type="file" (change)="onInterviewFileUploaded($event)" accept=".ics,.txt,.zip" class="hidden" />
                      </label>
                    </div>

                    <div class="p-2.5 rounded-xl bg-zinc-50 border border-black/10 flex items-center justify-between gap-2">
                      <div class="flex items-center gap-2 text-xs text-zinc-600 truncate min-w-0">
                        <span class="text-base shrink-0">📄</span>
                        <span class="truncate">{{ drJefService.language() === 'EN' ? 'CV / Career' : 'CV / Resumen' }}</span>
                      </div>
                      <label class="px-2.5 py-1 rounded-lg bg-orange-600 hover:bg-[#FF5500] text-white text-[11px] font-bold transition cursor-pointer shrink-0">
                        <span>{{ drJefService.language() === 'EN' ? 'Upload' : 'Subir' }}</span>
                        <input type="file" (change)="onCvFileUploaded($event)" accept=".txt,.pdf,.docx" class="hidden" />
                      </label>
                    </div>

                    <div class="p-2.5 rounded-xl bg-zinc-50 border border-black/10 flex items-center justify-between gap-2">
                      <div class="flex items-center gap-2 text-xs text-zinc-600 truncate min-w-0">
                        <span class="text-base shrink-0">📸</span>
                        @if (userPhotoPreview()) {
                          <img [src]="userPhotoPreview()" class="w-5 h-5 rounded-md object-cover border border-black/20 shrink-0" alt="Ref" />
                          <span class="truncate font-bold text-emerald-700">{{ drJefService.language() === 'EN' ? 'Photo linked' : 'Foto' }}</span>
                        } @else {
                          <span class="truncate">{{ drJefService.language() === 'EN' ? 'Photo (video)' : 'Foto (video)' }}</span>
                        }
                      </div>
                      <label class="px-2.5 py-1 rounded-lg bg-black text-white text-[11px] font-bold hover:bg-[#FF5500] transition cursor-pointer shrink-0">
                        <span>{{ userPhotoPreview() ? (drJefService.language() === 'EN' ? 'Change' : 'Cambiar') : (drJefService.language() === 'EN' ? 'Upload' : 'Subir') }}</span>
                        <input type="file" (change)="onPhotoUpload($event)" accept="image/*" class="hidden" />
                      </label>
                    </div>
                  </div>

                  <!-- Historial de Conversación con Scroll -->
                  <div class="max-h-[380px] overflow-y-auto space-y-3 p-3 bg-zinc-50/80 rounded-2xl border border-black/10 flex flex-col">
                    @for (msg of interviewHistory(); track $index) {
                      @if (msg.role === 'assistant') {
                        <div class="flex items-start gap-2 max-w-[90%]">
                          <div class="w-6 h-6 rounded-lg bg-black text-white flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5">
                            IA
                          </div>
                          <div class="p-3 rounded-2xl rounded-tl-sm bg-white border border-black/10 text-xs text-zinc-800 leading-relaxed shadow-xs">
                            {{ msg.content }}
                          </div>
                        </div>
                      } @else {
                        <div class="flex items-start gap-2 max-w-[90%] self-end flex-row-reverse">
                          <div class="w-6 h-6 rounded-lg bg-[#FF5500] text-white flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5">
                            Tú
                          </div>
                          <div class="p-3 rounded-2xl rounded-tr-sm bg-zinc-900 text-white text-xs leading-relaxed shadow-xs">
                            {{ msg.content }}
                          </div>
                        </div>
                      }
                    }

                    @if (isInterviewThinking()) {
                      <div class="flex items-start gap-2 max-w-[90%]">
                        <div class="w-6 h-6 rounded-lg bg-black text-white flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5">
                          IA
                        </div>
                        <div class="p-3 rounded-2xl rounded-tl-sm bg-white border border-black/10 text-xs text-zinc-500 flex items-center gap-2">
                          <span class="w-2 h-2 rounded-full bg-[#FF5500] animate-ping"></span>
                          <span>{{ drJefService.language() === 'EN' ? 'Analyzing your reality & causal factors...' : 'Analizando tu realidad y factores causales...' }}</span>
                        </div>
                      </div>
                    }
                  </div>

                  <!-- Input para escribir o dictar por voz -->
                  <div class="space-y-2">
                    <div class="relative">
                      <textarea
                        [(ngModel)]="interviewInputText"
                        (keydown.enter)="$event.preventDefault(); sendInterviewMessage()"
                        rows="3"
                        [placeholder]="drJefService.language() === 'EN' ? 'Type or dictate who you are, city, daily routine, goals...' : 'Escribe o dicta quién eres, ciudad, rutina, metas...'"
                        class="w-full p-3 rounded-2xl bg-white border border-black/15 text-xs text-zinc-900 focus:outline-none focus:border-[#FF5500] focus:ring-1 focus:ring-[#FF5500] resize-none pr-10 shadow-inner">
                      </textarea>

                      <button
                        type="button"
                        (click)="toggleInterviewVoice()"
                        [class.bg-red-600]="isInterviewListening()"
                        [class.text-white]="isInterviewListening()"
                        [class.shadow-md]="isInterviewListening()"
                        [class.shadow-red-500]="isInterviewListening()"
                        [class.bg-zinc-100]="!isInterviewListening()"
                        [class.text-zinc-600]="!isInterviewListening()"
                        [title]="drJefService.language() === 'EN' ? (isInterviewListening() ? 'Stop voice recording' : 'Continuous Voice Dictation') : (isInterviewListening() ? 'Pausar dictado' : 'Dictado continuo por voz')"
                        class="absolute right-2.5 bottom-3.5 w-8 h-8 rounded-xl flex items-center justify-center text-sm hover:scale-105 transition cursor-pointer border border-black/10">
                        @if (isInterviewListening()) {
                          <span class="animate-pulse text-xs">🔴</span>
                        } @else {
                          <span>🎙️</span>
                        }
                      </button>
                    </div>

                    <div class="flex items-center justify-between gap-2 flex-wrap">
                      <button
                        type="button"
                        (click)="toggleInterviewVoice()"
                        class="text-xs transition flex items-center gap-1.5 font-medium cursor-pointer"
                        [class.text-red-600]="isInterviewListening()"
                        [class.text-zinc-500]="!isInterviewListening()"
                        [class.hover:text-zinc-900]="!isInterviewListening()">
                        @if (isInterviewListening()) {
                          <span class="relative flex h-2.5 w-2.5">
                            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                            <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-red-600"></span>
                          </span>
                          <span class="font-bold text-[11px] sm:text-xs">
                            {{ drJefService.language() === 'EN' ? 'Listening continuously... (speak freely, click to pause)' : 'Escuchando sin cortes... (habla libremente, clic para pausar)' }}
                          </span>
                        } @else {
                          <span>🎙️ {{ drJefService.language() === 'EN' ? 'Continuous voice dictation' : 'Dictar por voz continuo' }}</span>
                        }
                      </button>

                      <button
                        type="button"
                        (click)="sendInterviewMessage()"
                        [disabled]="!interviewInputText().trim() || isInterviewThinking()"
                        class="px-4 py-2 rounded-xl bg-black hover:bg-[#FF5500] text-white text-xs font-bold transition flex items-center gap-1.5 disabled:opacity-40 cursor-pointer shadow-md">
                        <span>{{ drJefService.language() === 'EN' ? 'Send' : 'Responder' }}</span>
                        <span>➔</span>
                      </button>
                    </div>
                  </div>

                  <!-- Botón directo: "✨ Ya conté lo principal: Generar el Texto Completo de Cómo Soy" -->
                  <button
                    type="button"
                    (click)="forceCompleteInterview()"
                    [disabled]="isInterviewThinking()"
                    class="w-full py-3.5 px-4 rounded-2xl bg-gradient-to-r from-zinc-900 to-zinc-800 hover:from-[#FF5500] hover:to-orange-600 text-white font-extrabold text-xs uppercase tracking-wide transition-all shadow-md active:scale-98 cursor-pointer flex items-center justify-center gap-2 border border-white/10">
                    @if (isInterviewThinking()) {
                      <span class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                      <span>{{ drJefService.language() === 'EN' ? 'Synthesizing...' : 'Sintetizando...' }}</span>
                    } @else {
                      <span>✨</span>
                      <span>{{ drJefService.language() === 'EN' ? 'I have shared the main points: Compose My Full Dossier' : 'Ya conté lo principal: Generar el Texto Completo de Cómo Soy' }}</span>
                    }
                  </button>
                </div>
              } @else {
                <!-- VISTA DE CONFIRMACIÓN Y EDICIÓN LIBRE: "📄 TU REALIDAD HOY (SÍNTESIS COMPLETA DE LA IA)" -->
                <div class="flex flex-col gap-4">
                  <div class="flex items-center justify-between pb-2 border-b border-black/10">
                    <div class="flex items-center gap-2">
                      <span class="text-base">📄</span>
                      <h4 class="text-xs font-extrabold text-black uppercase tracking-wider font-mono">
                        {{ drJefService.language() === 'EN' ? 'YOUR REALITY TODAY (AI DOSSIER)' : 'TU REALIDAD HOY (SÍNTESIS COMPLETA DE LA IA)' }}
                      </h4>
                    </div>
                    <button
                      type="button"
                      (click)="dossierGenerated.set(false)"
                      class="text-[11px] text-[#FF5500] hover:underline font-bold flex items-center gap-1 cursor-pointer">
                      <span>💬</span>
                      <span>{{ drJefService.language() === 'EN' ? 'Chat more' : 'Seguir conversando' }}</span>
                    </button>
                  </div>

                  <!-- Textarea amplio y editable para el dossier completo -->
                  <div class="space-y-1.5">
                    <textarea
                      [(ngModel)]="fullPersonDossierText"
                      (ngModelChange)="onDossierEdited($event)"
                      (blur)="syncDossier()"
                      rows="9"
                      class="w-full p-4 rounded-2xl bg-amber-50/40 border border-amber-300/80 text-xs text-zinc-900 leading-relaxed font-sans focus:outline-none focus:border-[#FF5500] focus:ring-2 focus:ring-[#FF5500]/20 resize-none shadow-inner">
                    </textarea>
                    <div class="flex items-center justify-between text-[10px] text-zinc-500 px-1">
                      <span>✏️ {{ drJefService.language() === 'EN' ? 'You can edit any detail, goal or number directly here.' : 'Puedes editar cualquier detalle, meta o cifra directamente aquí.' }}</span>
                      @if (isSyncingDossier()) {
                        <span class="text-[#FF5500] font-bold animate-pulse">Sincronizando parámetros...</span>
                      }
                    </div>
                  </div>

                  <!-- Pastillas resumen de parámetros extraídos -->
                  <div class="p-3 rounded-2xl bg-zinc-100 border border-black/10 space-y-2">
                    <span class="text-[10px] font-bold uppercase tracking-wider text-zinc-500 font-mono block">
                      {{ drJefService.language() === 'EN' ? 'Calibrated Parameters' : 'Parámetros Calibrados' }}
                    </span>
                    <div class="flex flex-wrap gap-1.5">
                      <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-white border border-black/10 text-xs font-bold text-zinc-800 shadow-xs">
                        📍 {{ realitySeed.location.city || 'Ciudad' }}, {{ realitySeed.location.country }} ({{ getCurrencySymbol(realitySeed.finances.currency) }})
                      </span>
                      <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-white border border-black/10 text-xs font-bold text-zinc-800 shadow-xs">
                        💼 {{ realitySeed.career_or_degree || realitySeed.occupation }} {{ realitySeed.months_to_graduation ? '(' + realitySeed.months_to_graduation + ' mes p/ egresar)' : '' }}
                      </span>
                      <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-white border border-black/10 text-xs font-bold text-emerald-800 bg-emerald-50/60 shadow-xs">
                        💰 Ingreso: {{ getCurrencySymbol(realitySeed.finances.currency) }} {{ realitySeed.finances.monthly_income || 0 }} | Gasto: {{ getCurrencySymbol(realitySeed.finances.currency) }} {{ realitySeed.finances.monthly_expenses || 0 }} | Ahorro: {{ getCurrencySymbol(realitySeed.finances.currency) }} {{ realitySeed.finances.current_savings || 0 }}
                      </span>
                      <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-white border border-black/10 text-xs font-bold text-blue-800 bg-blue-50/60 shadow-xs">
                        👨‍👩‍👧 {{ realitySeed.dependents_count ? 'Cuidado de ' + realitySeed.dependents_count + ' dependientes' : 'Hogar familiar' }}
                      </span>
                      <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-white border border-black/10 text-xs font-bold text-purple-800 bg-purple-50/60 shadow-xs">
                        🧠 {{ getSpanishTraitNames(realitySeed.personality_traits) }}
                      </span>
                    </div>
                  </div>

                  @if (validationError()) {
                    <div class="p-3.5 rounded-2xl bg-amber-50 border-2 border-amber-400 text-amber-950 text-xs font-semibold flex items-start gap-2.5 shadow-sm mb-3">
                      <span class="text-base shrink-0">⚠️</span>
                      <span class="leading-relaxed">{{ validationError() }}</span>
                    </div>
                  }
                  <!-- BOTÓN GIGANTE DE MÁXIMO RELIEVE -->
                  <button
                    type="button"
                    (click)="predictFuture()"
                    [disabled]="isLoading()"
                    class="w-full py-4 rounded-2xl bg-black hover:bg-[#FF5500] text-white font-black text-xs uppercase tracking-wider shadow-xl hover:shadow-2xl hover:shadow-orange-500/20 transition-all active:scale-98 cursor-pointer flex items-center justify-center gap-2 border border-white/20 disabled:opacity-50">
                    @if (isLoading()) {
                      <span class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                      <span>{{ drJefService.language() === 'EN' ? 'Simulating 1,000 Trajectories...' : 'Calculando 1,000 Trayectorias...' }}</span>
                    } @else {
                      <span>🔮</span>
                      <span>{{ drJefService.language() === 'EN' ? 'PREDICT MY EXACT FUTURE (1 MO • 6 MO • 1 YR)' : 'PREDECIR MI FUTURO EXACTO (1 MES • 6 MESES • 1 AÑO)' }}</span>
                    }
                  </button>
                </div>
              }
          } @else {
            <div class="bg-white/95 border border-black/10 rounded-3xl p-5 sm:p-8 shadow-xl space-y-5">
              <ng-container *ngTemplateOutlet="parametersFormTemplate"></ng-container>
              @if (validationError()) {
                <div class="p-3.5 rounded-2xl bg-amber-50 border-2 border-amber-400 text-amber-950 text-xs font-semibold flex items-start gap-2.5 shadow-sm mb-3">
                  <span class="text-base shrink-0">⚠️</span>
                  <span class="leading-relaxed">{{ validationError() }}</span>
                </div>
              }
              <button
                type="button"
                (click)="predictFuture()"
                [disabled]="isLoading()"
                class="w-full py-4 rounded-2xl bg-black hover:bg-[#FF5500] text-white font-black text-xs uppercase tracking-wider shadow-lg transition active:scale-98 cursor-pointer flex items-center justify-center gap-2">
                <span>🔮</span>
                <span>{{ drJefService.language() === 'EN' ? 'PREDICT MY FUTURE SELF' : 'PREDECIR MI FUTURO YO' }}</span>
              </button>
            </div>
          }
        </div>
      }

      <!-- ======================================================== -->
      <!-- FASE 2: PANTALLA DE CARGA (isLoading())                  -->
      <!-- ======================================================== -->
      @if (isLoading()) {
        <div class="max-w-2xl mx-auto p-12 sm:p-16 rounded-3xl bg-white border border-black/10 text-center flex flex-col items-center justify-center gap-5 shadow-2xl my-16">
          <div class="w-16 h-16 rounded-2xl bg-[#FF5500]/15 border border-[#FF5500]/30 flex items-center justify-center text-3xl text-[#FF5500] animate-spin">
            ⚡
          </div>
          <div class="space-y-2">
            <h3 class="text-xl font-black text-black tracking-tight">
              {{ drJefService.language() === 'EN' ? 'Running Stochastic Trajectories' : 'Ejecutando Simulación Estocástica' }}
            </h3>
            <p class="text-xs sm:text-sm text-zinc-500 font-mono">
              {{ dynamicProgressText() }}
            </p>
          </div>
        </div>
      }

      <!-- ======================================================== -->
      <!-- FASE 3: PREDICCIÓN CAUSAL REVELADA + MENÚ DESPLEGABLE     -->
      <!-- ======================================================== -->
      @if (futureResponse(); as resp) {
        <div class="max-w-7xl mx-auto space-y-6">

          <!-- ACTION BAR SUPERIOR -->
          <div class="p-4 rounded-2xl bg-white/95 border border-black/10 shadow-md flex flex-wrap items-center justify-between gap-3 sticky top-4 z-30 backdrop-blur-md">
            <div class="flex items-center gap-3">
              <button
                type="button"
                (click)="goHome()"
                class="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-zinc-900 text-white text-xs font-bold uppercase tracking-wider hover:bg-zinc-800 transition cursor-pointer">
                <span>←</span>
                <span>{{ drJefService.language() === 'EN' ? 'Home' : 'Portada' }}</span>
              </button>
              <div class="hidden sm:flex items-center gap-2 font-mono text-xs text-zinc-600">
                <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                <span class="font-bold text-black">{{ realitySeed.location.city }}, {{ realitySeed.location.country }}</span>
                <span>({{ getCurrencySymbol(realitySeed.finances.currency) }})</span>
              </div>
            </div>

            <div class="flex items-center gap-2.5">
              <button
                type="button"
                (click)="startNewConversation()"
                class="px-4 py-2 rounded-xl bg-zinc-100 hover:bg-zinc-200 text-zinc-800 text-xs font-bold transition flex items-center gap-1.5 cursor-pointer border border-black/10 shadow-xs">
                <span>💬</span>
                <span>{{ drJefService.language() === 'EN' ? 'New Chat' : 'Nueva Conversación' }}</span>
              </button>
              <button
                type="button"
                (click)="toggleParametersDrawer()"
                class="px-5 py-2.5 rounded-xl bg-black hover:bg-[#FF5500] text-white text-xs font-black uppercase tracking-wider transition flex items-center gap-2 cursor-pointer shadow-lg hover:shadow-orange-500/20 active:scale-95">
                <span>⚙️</span>
                <span>{{ drJefService.language() === 'EN' ? 'Adjust Parameters' : 'Ajustar Parámetros' }}</span>
                <span class="w-2 h-2 rounded-full bg-[#FF5500] border border-white"></span>
              </button>
            </div>
          </div>

          <!-- CONTENIDO DE LA PREDICCIÓN (Nivel 1, Nivel 2, Nivel 3, Laboratorio 3D) -->
                <section class="bg-white/95 border border-black/10 rounded-3xl p-6 md:p-8 shadow-xl text-zinc-900 space-y-6">

                  

                  <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-4 border-b border-black/10 gap-3">

                    <div>

                      <span class="text-xs font-mono font-bold uppercase tracking-wider text-[#FF5500] block">

                        {{ drJefService.language() === 'EN' ? 'Level 1 • Portrait of Your Future Self' : 'Nivel 1 • Retrato de tu Futuro Yo' }}

                      </span>

                      <h3 class="text-xl md:text-2xl font-black text-black">

                        {{ drJefService.language() === 'EN' ? 'The Progressive Verdict' : 'El Veredicto Progresivo' }}

                      </h3>

                    </div>
                  </div>



                  <!-- Tarjeta del Horizonte Activo -->

                  @let horizon = getActiveHorizon(resp);

                  <div class="space-y-6">

                    

                    <!-- ============================================================== -->
                    <!-- 🧬 AUTOCOMPLETADO DE CARRERA E INGRESOS (MOTOR LIFE2VEC LABORAL) -->
                    <!-- ============================================================== -->
                    @if (resp.career_autocompletion; as cAuto) {
                      <div class="bg-gradient-to-br from-zinc-950 via-zinc-900 to-black text-white rounded-3xl p-6 md:p-8 shadow-2xl border border-white/15 space-y-6 relative overflow-hidden">
                        <!-- Decorative ambient glows -->
                        <div class="absolute -top-20 -right-20 w-72 h-72 bg-[#FF5500]/15 rounded-full blur-3xl pointer-events-none"></div>
                        <div class="absolute -bottom-20 -left-20 w-72 h-72 bg-blue-600/15 rounded-full blur-3xl pointer-events-none"></div>

                        <!-- Header -->
                        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/10 pb-5 relative z-10">
                          <div class="space-y-1.5">
                            <div class="flex flex-wrap items-center gap-2">
                              <span class="w-8 h-8 rounded-xl bg-[#FF5500]/20 border border-[#FF5500]/40 flex items-center justify-center text-lg shadow-xs">🧬</span>
                              <span class="text-xs font-mono font-bold uppercase tracking-wider text-[#FF5500]">
                                {{ drJefService.language() === 'EN' ? 'Life2Vec Sequential Career Engine' : 'Motor Life2Vec de Carrera e Ingresos' }}
                              </span>
                              <span class="px-2.5 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-bold">
                                {{ cAuto.past_events_encoded_count }} {{ drJefService.language() === 'EN' ? 'events encoded' : 'hitos codificados' }}
                              </span>
                            </div>
                            <h3 class="text-xl md:text-2xl font-black text-white tracking-tight">
                              {{ drJefService.language() === 'EN' ? 'Career & Income Autocompletion' : 'Autocompletado de Carrera y Salarios Futuros' }}
                            </h3>
                            <p class="text-xs text-zinc-300 max-w-2xl leading-relaxed">
                              {{ cAuto.trajectory_summary }}
                            </p>
                          </div>

                          <!-- Cohort Percentile Badge -->
                          <div class="p-4 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md text-center shrink-0">
                            <span class="text-[10px] font-mono uppercase text-zinc-400 block mb-0.5">
                              {{ drJefService.language() === 'EN' ? 'Cohort Percentile' : 'Percentil de Competitividad' }}
                            </span>
                            <span class="text-3xl font-black font-mono text-emerald-400 tracking-tight">
                              Top {{ 100 - cAuto.cohort_similarity_percentile }}%
                            </span>
                            <span class="text-[10px] font-mono text-zinc-300 block mt-0.5 font-medium">
                              {{ cAuto.cohort_rank_descriptor }}
                            </span>
                          </div>
                        </div>

                        <!-- AI Exposure vs AI Leverage Meters -->
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 relative z-10">
                          <!-- AI Automation Exposure -->
                          <div class="p-4 rounded-2xl bg-white/5 border border-white/10 space-y-2">
                            <div class="flex items-center justify-between text-xs">
                              <span class="font-bold flex items-center gap-1.5 text-zinc-200">
                                <span>⚠️</span> {{ drJefService.language() === 'EN' ? 'AI Automation Risk' : 'Riesgo de Reemplazo por IA' }}
                              </span>
                              <span class="font-mono font-bold text-orange-400 text-sm">{{ cAuto.ai_automation_exposure_pct }}%</span>
                            </div>
                            <div class="w-full bg-white/10 rounded-full h-2.5 overflow-hidden">
                              <div class="h-full rounded-full transition-all duration-700 bg-gradient-to-r from-emerald-500 via-amber-500 to-rose-500" [style.width.%]="cAuto.ai_automation_exposure_pct"></div>
                            </div>
                            <span class="text-[10px] text-zinc-400 block">
                              {{ drJefService.language() === 'EN' ? 'Portion of current tasks susceptible to generative AI automation.' : 'Porcentaje de tareas operativas sustituibles por IA en tu rol actual.' }}
                            </span>
                          </div>

                          <!-- AI Leverage Potential -->
                          <div class="p-4 rounded-2xl bg-white/5 border border-white/10 space-y-2">
                            <div class="flex items-center justify-between text-xs">
                              <span class="font-bold flex items-center gap-1.5 text-zinc-200">
                                <span>🚀</span> {{ drJefService.language() === 'EN' ? 'AI Leverage Potential (Advantage)' : 'Potencial de Apalancamiento con IA (Ventaja)' }}
                              </span>
                              <span class="font-mono font-bold text-emerald-400 text-sm">{{ cAuto.ai_leverage_potential_pct }}%</span>
                            </div>
                            <div class="w-full bg-white/10 rounded-full h-2.5 overflow-hidden">
                              <div class="h-full rounded-full transition-all duration-700 bg-gradient-to-r from-blue-500 to-emerald-400" [style.width.%]="cAuto.ai_leverage_potential_pct"></div>
                            </div>
                            <span class="text-[10px] text-zinc-400 block">
                              {{ drJefService.language() === 'EN' ? 'Capacity to multiply productivity and command premium compensation.' : 'Capacidad de multiplicar tu velocidad de entrega y cobrar tarifas premium.' }}
                            </span>
                          </div>
                        </div>

                        <!-- Sequential Timeline: [Historial Pasado] -> [Hoy] -> [1 Mes] -> [6 Meses] -> [1 Año] -> [3 Años] -> [5 Años] -->
                        <div class="space-y-3 relative z-10">
                          <div class="flex items-center justify-between">
                            <span class="text-xs font-mono font-bold uppercase tracking-wider text-zinc-200 flex items-center gap-1.5">
                              <span>⏱️</span> {{ drJefService.language() === 'EN' ? 'Life2Vec Sequential Trajectory' : 'Línea de Tiempo Secuencial Life2Vec' }}
                            </span>
                            <span class="text-[10px] font-mono text-zinc-400">
                              {{ drJefService.language() === 'EN' ? 'Click on any horizon to inspect details' : 'Haz clic en cualquier horizonte para ver su detalle' }}
                            </span>
                          </div>

                          <!-- Sequence Diagram Flow / Stepper Selector -->
                          <div class="p-3 rounded-2xl bg-white/5 border border-white/10 overflow-x-auto">
                            <div class="flex items-center gap-2 min-w-max text-xs font-mono">
                              <!-- Step 0: Historial Pasado -->
                              <div class="p-2.5 rounded-xl bg-zinc-800/80 border border-zinc-700 text-center min-w-[120px]">
                                <span class="text-[10px] text-zinc-400 block font-bold">HISTORIAL</span>
                                <span class="text-white font-bold block truncate">{{ cAuto.past_events_encoded_count }} Hitos Pasados</span>
                                <span class="text-[9px] text-zinc-400">Educación / Oficio</span>
                              </div>
                              <span class="text-zinc-600 font-bold text-sm shrink-0">➔</span>

                              <!-- Step 1: Hoy -->
                              <div class="p-2.5 rounded-xl bg-blue-950/80 border border-blue-600 text-center min-w-[130px]">
                                <span class="text-[10px] text-blue-300 block font-bold">HOY (DÍA 0)</span>
                                <span class="text-white font-bold block truncate text-[11px]">{{ realitySeed.occupation || 'Situación Actual' }}</span>
                                <span class="text-[9px] text-blue-300 font-bold">{{ resp.macro_context.currency_symbol || getCurrencySymbol(resp.macro_context.currency) }} {{ realitySeed.finances.monthly_income | number:'1.0-0' }}</span>
                              </div>
                              <span class="text-zinc-600 font-bold text-sm shrink-0">➔</span>

                              <!-- Interactive Future Horizons (0: 1M, 1: 6M, 2: 1Y, 3: 3Y, 4: 5Y) -->
                              @for (node of cAuto.predicted_career_transitions; track $index) {
                                <button
                                  type="button"
                                  (click)="selectCareerHorizon($index)"
                                  [class]="selectedCareerHorizonIndex() === $index
                                    ? 'bg-[#FF5500]/20 border-[#FF5500] ring-2 ring-[#FF5500]/50 text-white shadow-lg shadow-orange-950/40'
                                    : 'bg-zinc-900/80 border-white/10 hover:border-white/30 text-zinc-300 hover:text-white'"
                                  class="p-2.5 rounded-xl border text-center transition cursor-pointer min-w-[130px] flex flex-col justify-between shrink-0"
                                >
                                  <div class="flex items-center justify-between gap-1 w-full mb-1">
                                    <span class="text-[10px] font-bold uppercase truncate" [class.text-[#FF5500]]="selectedCareerHorizonIndex() === $index">{{ node.horizon_label }}</span>
                                    <span class="text-[9px] px-1.5 py-0.2 rounded font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                                      {{ node.transition_probability_pct }}%
                                    </span>
                                  </div>
                                  <span class="font-bold text-[11px] truncate block text-left w-full">{{ node.p50_likely_role }}</span>
                                  <span class="text-[10px] font-mono font-bold text-emerald-400 block text-left mt-0.5">
                                    {{ resp.macro_context.currency_symbol || getCurrencySymbol(resp.macro_context.currency) }} {{ node.p50_income | number:'1.0-0' }}/m
                                  </span>
                                </button>
                                @if (!$last) {
                                  <span class="text-zinc-600 font-bold text-sm shrink-0">➔</span>
                                }
                              }
                            </div>
                          </div>
                        </div>

                        <!-- Focus Card: Detalle del Horizonte Seleccionado -->
                        @if (cAuto.predicted_career_transitions[selectedCareerHorizonIndex()]; as activeNode) {
                          <div class="p-5 rounded-2xl bg-zinc-900/95 border border-[#FF5500]/40 shadow-xl space-y-4 relative z-10">
                            <!-- Focus Card Header -->
                            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-white/10 pb-3">
                              <div class="flex items-center gap-2">
                                <span class="w-2.5 h-2.5 rounded-full bg-[#FF5500] animate-pulse"></span>
                                <h4 class="text-sm md:text-base font-black font-mono text-white uppercase tracking-wide">
                                  {{ activeNode.horizon_label }} &bull; {{ drJefService.language() === 'EN' ? 'Autocompleted Trajectory & Salary Bands' : 'Proyección y Bandas Salariales' }}
                                </h4>
                              </div>
                              <div class="flex items-center gap-2">
                                <span class="text-xs font-mono px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-bold">
                                  {{ activeNode.transition_probability_pct }}% {{ drJefService.language() === 'EN' ? 'transition prob.' : 'probabilidad de transición' }}
                                </span>
                                @if (activeNode.cohort_rank_descriptor) {
                                  <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-white/10 text-zinc-300 border border-white/15">
                                    {{ activeNode.cohort_rank_descriptor }}
                                  </span>
                                }
                              </div>
                            </div>

                            <!-- 3 Salary & Role Scenarios: P50 (Inercial) vs P90 (Óptimo) vs P10 (Estancamiento) -->
                            <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                              <!-- P50 Likely Role -->
                              <div class="p-3.5 rounded-xl bg-white/5 border border-white/10 hover:border-white/20 transition space-y-2">
                                <div class="flex items-center justify-between text-[10px] font-mono text-zinc-400">
                                  <span class="font-bold flex items-center gap-1"><span>🎯</span> CAMINO PROBABLE (P50)</span>
                                  <span class="text-emerald-400 font-bold font-mono text-xs">
                                    {{ resp.macro_context.currency_symbol || getCurrencySymbol(resp.macro_context.currency) }} {{ activeNode.p50_income | number:'1.0-0' }}/m
                                  </span>
                                </div>
                                <div class="text-white font-bold text-xs leading-snug">{{ activeNode.p50_likely_role }}</div>
                                <p class="text-[10px] text-zinc-400 leading-tight">
                                  {{ drJefService.language() === 'EN' ? 'Most statistically probable outcome based on your current inertia and cohort peers.' : 'Resultado más probable si mantienes tu inercia y ritmo actual de estudio/trabajo.' }}
                                </p>
                              </div>

                              <!-- P90 Accelerated Role -->
                              <div class="p-3.5 rounded-xl bg-orange-950/40 border border-orange-700/50 hover:border-orange-500 transition space-y-2">
                                <div class="flex items-center justify-between text-[10px] font-mono text-orange-300">
                                  <span class="font-bold flex items-center gap-1"><span>✨</span> CAMINO ÓPTIMO (P90)</span>
                                  <span class="text-orange-300 font-bold font-mono text-xs">
                                    {{ resp.macro_context.currency_symbol || getCurrencySymbol(resp.macro_context.currency) }} {{ activeNode.p90_income | number:'1.0-0' }}/m
                                  </span>
                                </div>
                                <div class="text-white font-bold text-xs leading-snug">{{ activeNode.p90_accelerated_role }}</div>
                                <p class="text-[10px] text-orange-200/80 leading-tight">
                                  {{ drJefService.language() === 'EN' ? 'Unlocked by executing strategic catalysts, portfolio validation and high-leverage skills.' : 'Desbloqueado aplicando las palancas clave (portafolio, reducción de distracciones e inglés).' }}
                                </p>
                              </div>

                              <!-- P10 Stagnation Role -->
                              <div class="p-3.5 rounded-xl bg-zinc-900/90 border border-rose-900/40 hover:border-rose-800/60 transition space-y-2">
                                <div class="flex items-center justify-between text-[10px] font-mono text-zinc-400">
                                  <span class="font-bold flex items-center gap-1 text-rose-300"><span>⚠️</span> ESTANCAMIENTO (P10)</span>
                                  <span class="text-zinc-400 font-mono text-xs">
                                    {{ resp.macro_context.currency_symbol || getCurrencySymbol(resp.macro_context.currency) }} {{ activeNode.p10_income | number:'1.0-0' }}/m
                                  </span>
                                </div>
                                <div class="text-zinc-300 font-medium text-xs leading-snug">{{ activeNode.p10_stagnation_role }}</div>
                                <p class="text-[10px] text-zinc-500 leading-tight">
                                  {{ drJefService.language() === 'EN' ? 'Risk of underemployment or locked salary if key blockers remain unaddressed.' : 'Riesgo de subempleo o tope salarial si no superas los cuellos de botella detectados.' }}
                                </p>
                              </div>
                            </div>

                            <!-- Catalysts & Risk Factors for Active Horizon -->
                            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 border-t border-white/10 text-xs">
                              <div class="p-2.5 rounded-xl bg-white/5 border border-white/10 space-y-1">
                                <span class="text-[11px] font-bold text-orange-400 flex items-center gap-1">
                                  <span>🚀</span> {{ drJefService.language() === 'EN' ? 'Catalysts to Unlock P90:' : 'Palancas para desbloquear el camino óptimo:' }}
                                </span>
                                <span class="text-zinc-200 block text-[11px]">
                                  {{ (activeNode.required_skills_to_unlock || activeNode.key_catalysts || []).join(' · ') || (drJefService.language() === 'EN' ? 'Continuous skill practice and proactive job outreach' : 'Práctica constante y prospección activa') }}
                                </span>
                              </div>
                              <div class="p-2.5 rounded-xl bg-white/5 border border-white/10 space-y-1">
                                <span class="text-[11px] font-bold text-rose-400 flex items-center gap-1">
                                  <span>⚠️</span> {{ drJefService.language() === 'EN' ? 'Main Risk Factor (P10 trap):' : 'Riesgo principal de estancamiento:' }}
                                </span>
                                <span class="text-zinc-300 block text-[11px]">
                                  {{ activeNode.key_risk_factor || (activeNode.blockers && activeNode.blockers[0]) || (drJefService.language() === 'EN' ? 'Inaction and passive routine' : 'Inacción y rutina pasiva') }}
                                </span>
                              </div>
                            </div>
                          </div>
                        }

                        <!-- Executive Comparison Table across all 5 Horizons -->
                        <div class="p-4 rounded-2xl bg-zinc-900/80 border border-white/10 relative z-10 space-y-2">
                          <div class="flex items-center justify-between pb-2 border-b border-white/10">
                            <span class="text-xs font-mono font-bold uppercase tracking-wider text-zinc-200 flex items-center gap-1.5">
                              <span>📊</span> {{ drJefService.language() === 'EN' ? 'Executive Horizons Comparison' : 'Comparativa Ejecutiva de los 5 Horizontes' }}
                            </span>
                            <span class="text-[10px] font-mono text-zinc-400">
                              {{ drJefService.language() === 'EN' ? 'Click row to inspect' : 'Haz clic en una fila para enfocar' }}
                            </span>
                          </div>

                          <div class="overflow-x-auto">
                            <table class="w-full text-left text-xs font-mono">
                              <thead>
                                <tr class="text-[10px] uppercase text-zinc-400 border-b border-white/10">
                                  <th class="py-2 pr-3">Horizonte</th>
                                  <th class="py-2 px-3">Rol Probable (P50)</th>
                                  <th class="py-2 px-3 text-right">Salario P50</th>
                                  <th class="py-2 px-3 text-right text-orange-400">Óptimo P90</th>
                                  <th class="py-2 px-3 text-right text-zinc-500">Mínimo P10</th>
                                  <th class="py-2 pl-3 text-right">Prob. Salto</th>
                                </tr>
                              </thead>
                              <tbody class="divide-y divide-white/5">
                                @for (node of cAuto.predicted_career_transitions; track $index) {
                                  <tr
                                    (click)="selectCareerHorizon($index)"
                                    [class]="selectedCareerHorizonIndex() === $index ? 'bg-[#FF5500]/15 text-white' : 'hover:bg-white/5 text-zinc-300 cursor-pointer'"
                                    class="transition cursor-pointer"
                                  >
                                    <td class="py-2.5 pr-3 font-bold flex items-center gap-1.5">
                                      <span class="w-1.5 h-1.5 rounded-full" [class]="selectedCareerHorizonIndex() === $index ? 'bg-[#FF5500]' : 'bg-zinc-600'"></span>
                                      <span>{{ node.horizon_label }}</span>
                                    </td>
                                    <td class="py-2.5 px-3 max-w-[220px] truncate" [title]="node.p50_likely_role">
                                      {{ node.p50_likely_role }}
                                    </td>
                                    <td class="py-2.5 px-3 text-right font-bold text-emerald-400">
                                      {{ resp.macro_context.currency_symbol || getCurrencySymbol(resp.macro_context.currency) }} {{ node.p50_income | number:'1.0-0' }}
                                    </td>
                                    <td class="py-2.5 px-3 text-right font-bold text-orange-300">
                                      {{ resp.macro_context.currency_symbol || getCurrencySymbol(resp.macro_context.currency) }} {{ node.p90_income | number:'1.0-0' }}
                                    </td>
                                    <td class="py-2.5 px-3 text-right text-zinc-400">
                                      {{ resp.macro_context.currency_symbol || getCurrencySymbol(resp.macro_context.currency) }} {{ node.p10_income | number:'1.0-0' }}
                                    </td>
                                    <td class="py-2.5 pl-3 text-right font-bold">
                                      <span class="px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-[10px]">
                                        {{ node.transition_probability_pct }}%
                                      </span>
                                    </td>
                                  </tr>
                                }
                              </tbody>
                            </table>
                          </div>
                        </div>

                        <!-- Bottlenecks & Strategic Accelerator Skills (Only when populated) -->
                        @if ((cAuto.career_bottlenecks && cAuto.career_bottlenecks.length > 0) || (cAuto.recommended_high_leverage_skills && cAuto.recommended_high_leverage_skills.length > 0)) {
                          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-3 border-t border-white/10 relative z-10">
                            <!-- Career Bottlenecks -->
                            @if (cAuto.career_bottlenecks && cAuto.career_bottlenecks.length > 0) {
                              <div class="p-4 rounded-2xl bg-rose-950/30 border border-rose-800/40 space-y-2">
                                <span class="text-xs font-bold text-rose-300 flex items-center gap-1.5 font-mono">
                                  <span>🛑</span> {{ drJefService.language() === 'EN' ? 'Identified Career Bottlenecks' : 'Cuellos de Botella Detectados' }}
                                </span>
                                <ul class="space-y-1.5 text-xs text-zinc-300">
                                  @for (bn of cAuto.career_bottlenecks; track $index) {
                                    @if (bn && bn.trim()) {
                                      <li class="flex items-start gap-2">
                                        <span class="text-rose-400 mt-0.5">•</span>
                                        <span class="leading-tight">{{ bn }}</span>
                                      </li>
                                    }
                                  }
                                </ul>
                              </div>
                            }

                            <!-- High Leverage Skills to Unlock -->
                            @if (cAuto.recommended_high_leverage_skills && cAuto.recommended_high_leverage_skills.length > 0) {
                              <div class="p-4 rounded-2xl bg-emerald-950/30 border border-emerald-800/40 space-y-2">
                                <span class="text-xs font-bold text-emerald-300 flex items-center gap-1.5 font-mono">
                                  <span>⚡</span> {{ drJefService.language() === 'EN' ? 'High-Leverage Skills to Prioritize' : 'Habilidades Aceleradoras de Alto Retorno' }}
                                </span>
                                <div class="flex flex-wrap gap-1.5 pt-1">
                                  @for (skill of cAuto.recommended_high_leverage_skills; track $index) {
                                    @if (skill && skill.trim()) {
                                      <span class="px-2.5 py-1 rounded-lg bg-emerald-900/50 border border-emerald-700/50 text-emerald-200 text-xs font-mono font-medium">
                                        {{ skill }}
                                      </span>
                                    }
                                  }
                                </div>
                              </div>
                            }
                          </div>
                        }

                        <!-- ============================================================== -->
                        <!-- 📊 AUDITORÍA EMPÍRICA DE MERCADO Y MATCH DE VACANTES REALES     -->
                        <!-- ============================================================== -->
                        <div class="mt-6 pt-5 border-t border-white/10 relative z-10 space-y-5">
                          <!-- Section Header -->
                          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-zinc-900/90 p-4 rounded-2xl border border-cyan-500/30">
                            <div class="flex items-center gap-3">
                              <span class="w-10 h-10 rounded-xl bg-cyan-950 border border-cyan-500/40 flex items-center justify-center text-cyan-400 text-lg font-bold shrink-0">
                                📊
                              </span>
                              <div>
                                <h4 class="text-sm md:text-base font-black font-mono text-white uppercase tracking-wide flex items-center gap-2">
                                  <span>{{ getOpportunitiesSectionTitle() }}</span>
                                  <span class="text-[10px] px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">384d Match</span>
                                </h4>
                                <span class="text-[11px] font-mono text-zinc-400 block">
                                  {{ getOpportunitiesSectionSubtitle() }}
                                </span>
                              </div>
                            </div>

                            <div class="flex items-center gap-2 flex-wrap">
                              <span class="text-[11px] font-mono px-3 py-1 rounded-xl bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 font-bold flex items-center gap-1.5">
                                <span>🎯</span>
                                <span>{{ drJefService.language() === 'EN' ? 'Audited Competence' : 'Competencia Auditada' }}: x{{ cAuto.verified_competence_multiplier || 1.0 }}</span>
                              </span>
                              <span class="text-[11px] font-mono px-2.5 py-1 rounded-xl bg-white/10 text-zinc-300 border border-white/15">
                                {{ realitySeed.location.city || 'Local' }}, {{ realitySeed.location.country || 'PE' }}
                              </span>
                            </div>
                          </div>

                          <!-- 1. VACANTES REALES ABIERTAS CON MATCH VECTORIAL 384d -->
                          @if (cAuto.real_job_openings && cAuto.real_job_openings.length > 0) {
                            <div class="space-y-3">
                              <div class="flex items-center justify-between">
                                <span class="text-xs font-mono font-bold uppercase tracking-wider text-cyan-300 flex items-center gap-1.5">
                                  <span>💼</span> {{ getOpportunitiesListLabel() }} ({{ cAuto.real_job_openings.length }})
                                </span>
                                <span class="text-[10px] font-mono text-zinc-400">
                                  {{ drJefService.language() === 'EN' ? 'Direct ATS & qualifications matching' : 'Cotejo directo de requisitos y habilidades' }}
                                </span>
                              </div>

                              <div class="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                                @for (job of cAuto.real_job_openings; track $index) {
                                  <div class="p-4 rounded-2xl bg-zinc-900/90 border border-white/10 hover:border-cyan-500/40 transition space-y-3 flex flex-col justify-between">
                                    <div class="space-y-2">
                                      <!-- Job Title & Match Badge -->
                                      <div class="flex items-start justify-between gap-2">
                                        <div>
                                          <h5 class="text-white font-bold text-xs md:text-sm leading-snug">{{ job.job_title }}</h5>
                                          <span class="text-[11px] font-mono text-zinc-400 block">{{ job.company_or_entity }} &bull; {{ job.location_and_modality }}</span>
                                        </div>
                                        <span
                                          [class]="job.exact_match_score_pct >= 70
                                            ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                                            : (job.exact_match_score_pct >= 48
                                              ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                                              : 'bg-rose-500/20 text-rose-300 border-rose-500/40')"
                                          class="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border shrink-0"
                                        >
                                          {{ job.exact_match_score_pct }}% Match
                                        </span>
                                      </div>

                                      <!-- Salary Comparison: Gross vs Net Liquid -->
                                      <div class="p-2.5 rounded-xl bg-black/40 border border-white/5 space-y-1">
                                        <div class="flex items-center justify-between text-xs font-mono">
                                          <span class="text-zinc-400 text-[11px]">{{ drJefService.language() === 'EN' ? 'Gross Range' : 'Rango Bruto Publicado' }}:</span>
                                          <span class="text-zinc-200 font-bold">{{ job.offered_salary_range }}</span>
                                        </div>
                                        <div class="flex items-center justify-between text-xs font-mono pt-1 border-t border-white/5">
                                          <span class="text-emerald-400 font-bold flex items-center gap-1 text-[11px]">
                                            <span>💵</span> {{ drJefService.language() === 'EN' ? 'Net In-Hand Disposable' : 'Sueldo Líquido Neto en Mano' }}:
                                          </span>
                                          <span class="text-emerald-300 font-black font-mono text-xs">
                                            {{ resp.macro_context.currency_symbol || 'S/' }} {{ job.net_salary_monthly | number:'1.0-0' }}/m
                                          </span>
                                        </div>
                                        <span class="text-[9px] font-mono text-zinc-500 block text-right">
                                          {{ drJefService.language() === 'EN' ? 'After 13% statutory tax/pension & local transport' : 'Descontando ~13% ley (AFP/ONP) y movilidad local' }}
                                        </span>
                                      </div>

                                      <!-- Required skills pills -->
                                      @if (job.required_skills_and_credentials && job.required_skills_and_credentials.length > 0) {
                                        <div class="space-y-1">
                                          <span class="text-[10px] font-mono uppercase text-zinc-400 font-bold block">{{ drJefService.language() === 'EN' ? 'Requirements' : 'Requisitos Pedidos' }}:</span>
                                          <div class="flex flex-wrap gap-1">
                                            @for (req of job.required_skills_and_credentials; track $index) {
                                              <span class="text-[10px] font-mono px-2 py-0.5 rounded-md bg-white/5 text-zinc-300 border border-white/10">
                                                {{ req }}
                                              </span>
                                            }
                                          </div>
                                        </div>
                                      }

                                      <!-- Missing requirements / Gap alerts -->
                                      <div class="text-[11px] font-mono pt-1">
                                        @if (job.missing_requirements && job.missing_requirements.length > 0) {
                                          <div class="p-2 rounded-lg bg-rose-950/40 border border-rose-800/40 space-y-1">
                                            <span class="text-rose-300 font-bold block text-[10px]">⚠️ {{ drJefService.language() === 'EN' ? 'Pending Gap to Qualify' : 'Brecha Pendiente para Postular' }}:</span>
                                            @for (miss of job.missing_requirements; track $index) {
                                              <span class="text-rose-200 block text-[10px] leading-tight">• {{ miss }}</span>
                                            }
                                            <span class="text-orange-300 font-bold block text-[10px] pt-0.5">
                                              ⏳ {{ drJefService.language() === 'EN' ? 'Estimated time to close gap' : 'Tiempo estimado para cerrar brecha' }}: ~{{ job.weeks_to_close_gap }} {{ drJefService.language() === 'EN' ? 'weeks' : 'semanas' }}
                                            </span>
                                          </div>
                                        } @else {
                                          <div class="p-2 rounded-lg bg-emerald-950/40 border border-emerald-800/40 text-emerald-300 text-[10px] font-bold">
                                            ✅ {{ drJefService.language() === 'EN' ? 'You meet 100% of candidate requirements today' : 'Calificas con el 100% de los requisitos para postular hoy' }}
                                          </div>
                                        }
                                      </div>
                                    </div>

                                    <!-- Link button -->
                                    <div class="pt-2">
                                      <a
                                        [href]="job.source_url"
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        class="w-full py-1.5 px-3 rounded-xl bg-cyan-950 hover:bg-cyan-900 border border-cyan-600/50 text-cyan-200 hover:text-white text-xs font-mono font-bold transition flex items-center justify-center gap-1.5"
                                      >
                                        <span>{{ getOpportunityButtonLabel() }}</span>
                                        <span>↗</span>
                                      </a>
                                    </div>
                                  </div>
                                }
                              </div>
                            </div>
                          }

                          <!-- 2. RELOJ ACTUARIAL DE INSERCIÓN LABORAL (MODELO WEIBULL/COX) -->
                          @if (cAuto.actuarial_insertion; as act) {
                            <div class="p-4 md:p-5 rounded-2xl bg-zinc-900/90 border border-orange-500/30 space-y-4">
                              <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-white/10 pb-3">
                                <div>
                                  <h5 class="text-sm md:text-base font-black font-mono text-white uppercase tracking-wide flex items-center gap-2">
                                    <span>⏱️</span>
                                    <span>{{ getActuarialClockTitle() }}</span>
                                  </h5>
                                  <span class="text-[11px] font-mono text-zinc-400 block">
                                    {{ drJefService.language() === 'EN' ? 'Weekly hiring hazard probability curve factored by graduation milestone, caregiving & market match' : 'Curva de probabilidad semanal ponderada por mes de egreso, horas de cuidado y match del mercado' }}
                                  </span>
                                </div>
                                <span class="text-[10px] font-mono px-2.5 py-1 rounded-full bg-orange-500/20 text-orange-300 border border-orange-500/40 font-bold self-start sm:self-auto">
                                  52 Semanas / 1 Año
                                </span>
                              </div>

                              <!-- 3 Metrics Highlights -->
                              <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                                <!-- P50 Median Contract -->
                                <div class="p-3 rounded-xl bg-white/5 border border-white/10 space-y-1">
                                  <span class="text-[10px] font-mono uppercase text-zinc-400 block font-bold">
                                    🎯 {{ drJefService.language() === 'EN' ? 'P50 Likely Contract Time' : 'Semanas a Contrato (P50 Mediana)' }}
                                  </span>
                                  <span class="text-lg md:text-xl font-black font-mono text-emerald-400 block">
                                    {{ act.estimated_weeks_to_first_contract_p50 }} {{ drJefService.language() === 'EN' ? 'weeks' : 'semanas' }}
                                  </span>
                                  <span class="text-[10px] font-mono text-zinc-400 block">
                                    ~{{ (act.estimated_weeks_to_first_contract_p50 / 4.3) | number:'1.1-1' }} {{ drJefService.language() === 'EN' ? 'months from today' : 'meses desde hoy' }}
                                  </span>
                                </div>

                                <!-- P90 Accelerated Contract -->
                                <div class="p-3 rounded-xl bg-orange-950/30 border border-orange-700/40 space-y-1">
                                  <span class="text-[10px] font-mono uppercase text-orange-300 block font-bold">
                                    ⚡ {{ drJefService.language() === 'EN' ? 'P90 Accelerated Route' : 'Camino Óptimo Acelerado (P90)' }}
                                  </span>
                                  <span class="text-lg md:text-xl font-black font-mono text-orange-400 block">
                                    {{ act.estimated_weeks_to_first_contract_p90 }} {{ drJefService.language() === 'EN' ? 'weeks' : 'semanas' }}
                                  </span>
                                  <span class="text-[10px] font-mono text-orange-300/80 block">
                                    ~{{ (act.estimated_weeks_to_first_contract_p90 / 4.3) | number:'1.1-1' }} {{ drJefService.language() === 'EN' ? 'months with active portfolio' : 'meses con portafolio activo' }}
                                  </span>
                                </div>

                                <!-- 75% Probability Milestone -->
                                <div class="p-3 rounded-xl bg-cyan-950/30 border border-cyan-700/40 space-y-1">
                                  <span class="text-[10px] font-mono uppercase text-cyan-300 block font-bold">
                                    🛡️ {{ drJefService.language() === 'EN' ? '75% Certainty Threshold' : 'Umbral de Certeza (>75%)' }}
                                  </span>
                                  <span class="text-lg md:text-xl font-black font-mono text-cyan-400 block">
                                    Semana {{ act.weeks_to_75pct_probability }}
                                  </span>
                                  <span class="text-[10px] font-mono text-cyan-300/80 block">
                                    {{ drJefService.language() === 'EN' ? 'Statistical confidence threshold' : 'Punto de inflexión de contratación segura' }}
                                  </span>
                                </div>
                              </div>

                              <!-- Monthly Cash Flow Ledger Breakdown -->
                              @if (act.cash_flow_monthly_breakdown; as cf) {
                                <div class="p-3.5 rounded-xl bg-black/50 border border-white/10 space-y-2.5">
                                  <span class="text-xs font-mono font-bold uppercase tracking-wider text-zinc-300 block">
                                    💰 {{ drJefService.language() === 'EN' ? 'Empirical Monthly Cashflow Breakdown' : 'Desglose Contable Real de Flujo de Caja Mensual' }}
                                  </span>
                                  <div class="grid grid-cols-2 sm:grid-cols-5 gap-2 text-xs font-mono">
                                    <div class="p-2 rounded-lg bg-white/5 border border-white/5">
                                      <span class="text-[10px] text-zinc-400 block">Sueldo Bruto</span>
                                      <span class="text-white font-bold block">{{ resp.macro_context.currency_symbol || 'S/' }} {{ cf.gross_salary | number:'1.0-0' }}</span>
                                    </div>
                                    <div class="p-2 rounded-lg bg-rose-950/20 border border-rose-900/30">
                                      <span class="text-[10px] text-rose-300 block">Retención Ley (~13%)</span>
                                      <span class="text-rose-300 font-bold block">- {{ resp.macro_context.currency_symbol || 'S/' }} {{ cf.statutory_deductions_afp_onp | number:'1.0-0' }}</span>
                                    </div>
                                    <div class="p-2 rounded-lg bg-amber-950/20 border border-amber-900/30">
                                      <span class="text-[10px] text-amber-300 block">Transporte/Alimentación</span>
                                      <span class="text-amber-300 font-bold block">- {{ resp.macro_context.currency_symbol || 'S/' }} {{ cf.local_commute_and_meals | number:'1.0-0' }}</span>
                                    </div>
                                    <div class="p-2 rounded-lg bg-emerald-950/40 border border-emerald-600/40">
                                      <span class="text-[10px] text-emerald-300 block font-bold">Líquido Neto Real</span>
                                      <span class="text-emerald-300 font-black block">{{ resp.macro_context.currency_symbol || 'S/' }} {{ cf.net_liquid_disposable | number:'1.0-0' }}</span>
                                    </div>
                                    <div class="p-2 rounded-lg bg-cyan-950/30 border border-cyan-700/30">
                                      <span class="text-[10px] text-cyan-300 block font-bold">Capacidad Ahorro</span>
                                      <span class="text-cyan-300 font-black block">+ {{ resp.macro_context.currency_symbol || 'S/' }} {{ cf.real_savings_capacity | number:'1.0-0' }}</span>
                                    </div>
                                  </div>
                                </div>
                              }

                              <!-- Month by Month Progression Table -->
                              @if (act.exact_net_salary_progression && act.exact_net_salary_progression.length > 0) {
                                <div class="space-y-2">
                                  <span class="text-xs font-mono font-bold uppercase tracking-wider text-zinc-300 block">
                                    📈 {{ drJefService.language() === 'EN' ? 'Month-by-Month Net Salary & Hiring Progression' : 'Progresión Salarial Contable Mes a Mes' }}
                                  </span>
                                  <div class="overflow-x-auto">
                                    <table class="w-full text-left text-xs font-mono">
                                      <thead>
                                        <tr class="text-[10px] uppercase text-zinc-400 border-b border-white/10">
                                          <th class="py-2 pr-3">Mes</th>
                                          <th class="py-2 px-3 text-right">Sueldo Bruto</th>
                                          <th class="py-2 px-3 text-right text-rose-400">Descuentos</th>
                                          <th class="py-2 px-3 text-right text-emerald-400 font-bold">Líquido Neto</th>
                                          <th class="py-2 px-3 text-right text-cyan-400">Capacidad Ahorro</th>
                                          <th class="py-2 pl-3 text-right">Prob. Contratado</th>
                                        </tr>
                                      </thead>
                                      <tbody class="divide-y divide-white/5">
                                        @for (prog of act.exact_net_salary_progression; track $index) {
                                          @if (prog.month_index <= 6 || prog.month_index === 12 || prog.month_index === 36) {
                                            <tr class="hover:bg-white/5 text-zinc-300 transition">
                                              <td class="py-2.5 pr-3 font-bold text-white flex items-center gap-1.5">
                                                <span class="w-1.5 h-1.5 rounded-full" [class]="prog.month_index === 36 ? 'bg-orange-400' : 'bg-cyan-400'"></span>
                                                <span>{{ prog.month_label }}</span>
                                              </td>
                                              <td class="py-2.5 px-3 text-right text-zinc-300">
                                                {{ resp.macro_context.currency_symbol || 'S/' }} {{ prog.gross_salary | number:'1.0-0' }}
                                              </td>
                                              <td class="py-2.5 px-3 text-right text-rose-300/80">
                                                -{{ resp.macro_context.currency_symbol || 'S/' }} {{ prog.statutory_deductions | number:'1.0-0' }}
                                              </td>
                                              <td class="py-2.5 px-3 text-right font-bold text-emerald-400">
                                                {{ resp.macro_context.currency_symbol || 'S/' }} {{ prog.net_liquid_disposable | number:'1.0-0' }}
                                              </td>
                                              <td class="py-2.5 px-3 text-right text-cyan-300 font-bold">
                                                {{ resp.macro_context.currency_symbol || 'S/' }} {{ prog.real_savings_capacity | number:'1.0-0' }}
                                              </td>
                                              <td class="py-2.5 pl-3 text-right">
                                                <span class="px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-[10px] font-bold">
                                                  {{ prog.hiring_probability_pct }}%
                                                </span>
                                              </td>
                                            </tr>
                                          }
                                        }
                                      </tbody>
                                    </table>
                                  </div>
                                </div>
                              }
                            </div>
                          }
                        </div>
                      </div>
                    }



                                        <!-- ============================================================== -->
                    <!-- 🧭 GUÍA PASO A PASO: QUÉ SEGUIR Y QUÉ CAMBIAR DÍA A DÍA        -->
                    <!-- ============================================================== -->
                    @if (resp.career_autocompletion?.strategic_roadmap && resp.career_autocompletion!.strategic_roadmap!.length > 0) {
                      <div class="rounded-3xl border border-black/10 bg-white p-6 md:p-8 shadow-sm space-y-6">
                        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-black/10">
                          <div>
                            <div class="flex items-center gap-2 mb-1">
                              <span class="px-2.5 py-0.5 rounded-full bg-[#FF5500]/10 text-[#FF5500] font-mono text-[10px] font-bold tracking-wider uppercase">
                                Hoja de Ruta Secuencial
                              </span>
                              <span class="text-xs font-mono text-zinc-400">4 Fases Estratégicas</span>
                            </div>
                            <h4 class="text-lg md:text-xl font-black text-black tracking-tight">
                              {{ drJefService.language() === 'EN' ? '🧭 Step-by-Step Strategic Guide: What to Follow & Change Daily' : '🧭 Guía Paso a Paso: Qué Seguir y Qué Cambiar Día a Día para Llegar a tu Futuro Óptimo' }}
                            </h4>
                            <p class="text-xs text-zinc-600 mt-1">
                              {{ drJefService.language() === 'EN' ? 'Actionable transitions, daily routine habits, and traps to avoid calibrated to your profile and market.' : 'Transiciones accionables, hábitos diarios y trampas a evitar calibradas para tu perfil y mercado.' }}
                            </p>
                          </div>

                          <!-- Selector de Fases (Tabs) -->
                          <div class="flex flex-wrap items-center gap-1.5 p-1 bg-[#F5F5F7] rounded-2xl border border-black/10 self-start md:self-auto">
                            @for (phase of resp.career_autocompletion!.strategic_roadmap!; track phase.phase_key; let idx = $index) {
                              <button
                                type="button"
                                (click)="selectRoadmapPhase(idx)"
                                [class]="selectedRoadmapPhaseIndex() === idx ? 'bg-black text-white shadow-xs font-bold' : 'text-zinc-600 hover:text-black font-semibold'"
                                class="px-3 py-1.5 rounded-xl text-xs transition-all cursor-pointer whitespace-nowrap"
                              >
                                {{ phase.timeframe }}
                              </button>
                            }
                          </div>
                        </div>

                        <!-- Detalle de la Fase Seleccionada -->
                        @let activePhase = resp.career_autocompletion!.strategic_roadmap![selectedRoadmapPhaseIndex()] || resp.career_autocompletion!.strategic_roadmap![0];
                        @if (activePhase) {
                          <div class="space-y-6">
                            <!-- Cabecera de la Fase: Objetivo y Banda Salarial -->
                            <div class="p-5 rounded-2xl bg-gradient-to-r from-zinc-900 to-zinc-950 text-white flex flex-col sm:flex-row sm:items-center justify-between gap-4 border border-zinc-800">
                              <div class="space-y-1">
                                <span class="text-xs font-mono text-[#FF5500] font-bold uppercase tracking-wider">
                                  {{ activePhase.phase_label }}
                                </span>
                                <h5 class="text-base font-bold text-zinc-100">
                                  🎯 {{ activePhase.main_objective }}
                                </h5>
                              </div>
                              <div class="px-4 py-2.5 rounded-xl bg-white/10 border border-white/15 backdrop-blur-xs text-right shrink-0">
                                <span class="text-[10px] text-zinc-400 block font-mono uppercase tracking-wider">Banda Salarial Objetivo</span>
                                <span class="text-sm font-mono font-black text-emerald-400">
                                  {{ activePhase.target_salary_range }}
                                </span>
                              </div>
                            </div>

                            <!-- Grid 2 Columnas: Hábitos Diarios vs Qué Seguir (Hitos) -->
                            <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
                              <!-- Columna 1: QUÉ CAMBIAR DÍA A DÍA -->
                              <div class="p-5 rounded-2xl bg-[#F5F5F7] border border-black/10 space-y-3.5">
                                <div class="flex items-center gap-2 pb-2 border-b border-black/10">
                                  <span class="w-6 h-6 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center text-xs font-bold shrink-0">🔄</span>
                                  <h6 class="text-xs font-mono font-bold uppercase tracking-wider text-black">
                                    {{ drJefService.language() === 'EN' ? 'Daily Routine: What to change every day' : 'Qué cambiar en tu rutina diaria (Hábitos de cada día)' }}
                                  </h6>
                                </div>
                                <div class="space-y-2.5">
                                  @for (habit of activePhase.daily_changes_to_implement; track hIdx; let hIdx = $index) {
                                    <div class="p-3 rounded-xl bg-white border border-black/5 flex items-start gap-2.5 shadow-2xs">
                                      <span class="w-5 h-5 rounded-full bg-blue-50 text-blue-700 text-[11px] font-bold flex items-center justify-center shrink-0 mt-0.5">
                                        {{ hIdx + 1 }}
                                      </span>
                                      <p class="text-xs text-zinc-800 leading-relaxed font-medium">
                                        {{ habit }}
                                      </p>
                                    </div>
                                  }
                                </div>
                              </div>

                              <!-- Columna 2: QUÉ SEGUIR PARA LLEGAR A TAL PUNTO (Hitos y Pasos) -->
                              <div class="p-5 rounded-2xl bg-[#F5F5F7] border border-black/10 space-y-3.5">
                                <div class="flex items-center gap-2 pb-2 border-b border-black/10">
                                  <span class="w-6 h-6 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center text-xs font-bold shrink-0">🚀</span>
                                  <h6 class="text-xs font-mono font-bold uppercase tracking-wider text-black">
                                    {{ drJefService.language() === 'EN' ? 'What to pursue to reach this milestone (Concrete steps)' : 'Qué seguir para llegar a este punto (Hitos y pasos concretos)' }}
                                  </h6>
                                </div>
                                <div class="space-y-2.5">
                                  @for (milestone of activePhase.strategic_actions_milestones; track mIdx; let mIdx = $index) {
                                    <div class="p-3 rounded-xl bg-white border border-black/5 flex items-start gap-2.5 shadow-2xs">
                                      <span class="w-5 h-5 rounded-full bg-emerald-50 text-emerald-700 text-[11px] font-bold flex items-center justify-center shrink-0 mt-0.5">
                                        {{ mIdx + 1 }}
                                      </span>
                                      <p class="text-xs text-zinc-800 leading-relaxed font-medium">
                                        {{ milestone }}
                                      </p>
                                    </div>
                                  }
                                </div>
                              </div>
                            </div>

                            <!-- Trampa Crítica a Evitar -->
                            <div class="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-950 flex items-start gap-3">
                              <span class="text-lg shrink-0 mt-0.5">⚠️</span>
                              <div class="space-y-0.5">
                                <span class="text-xs font-mono font-bold uppercase tracking-wider text-rose-800 block">
                                  {{ drJefService.language() === 'EN' ? 'Critical trap to avoid in this phase:' : 'Trampa crítica a evitar en esta etapa:' }}
                                </span>
                                <p class="text-xs text-rose-900 leading-relaxed">
                                  {{ activePhase.critical_trap_to_avoid }}
                                </p>
                              </div>
                            </div>
                          </div>
                        }
                      </div>
                    }

<!-- ============================================================== -->

                    <!-- 🪞 ESPEJO VISUAL: ASÍ TE VERÁS EN ESTE HORIZONTE              -->

                    <!-- ============================================================== -->

                    <div class="bg-white rounded-3xl border border-black/10 p-5 md:p-6 shadow-sm space-y-4">

                      <!-- Cabecera de la tarjeta con Switch en la esquina superior -->

                      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-2 border-b border-black/10">

                        <div class="flex items-center gap-2">

                          <span class="w-8 h-8 rounded-xl bg-purple-100 border border-purple-200 flex items-center justify-center text-purple-700 text-sm font-bold shrink-0">

                            🪞

                          </span>

                          <div>

                            <h4 class="text-xs sm:text-sm font-black uppercase tracking-wider text-black font-mono">

                              {{ drJefService.language() === 'EN' ? 'Visual Mirror: How you will look in this horizon' : 'Espejo Visual: Así te verás en este horizonte' }}

                            </h4>

                            <span class="text-[11px] text-zinc-500 font-sans">

                              {{ horizon.horizon_label }} &bull; {{ drJefService.language() === 'EN' ? 'Projection of habits, energy & countenance' : 'Proyección de hábitos, energía y semblante' }}

                            </span>

                          </div>

                        </div>



                        <!-- Switch y Botón de Foto en la esquina superior -->
                        <div class="flex items-center gap-2 self-stretch sm:self-auto flex-wrap justify-end">
                          @if (!userPhotoPreview()) {
                            <label class="px-3 py-1.5 rounded-xl bg-amber-50 hover:bg-amber-100 border border-amber-300 text-amber-900 text-xs font-bold cursor-pointer transition shadow-xs flex items-center gap-1.5 shrink-0">
                              <span>📸</span>
                              <span>{{ drJefService.language() === 'EN' ? 'Link Face Photo' : 'Vincular Foto Real' }}</span>
                              <input type="file" (change)="onPhotoUpload($event)" accept="image/*" class="hidden" />
                            </label>
                          }

                          <div class="flex items-center bg-[#F5F5F7] p-1 rounded-2xl border border-black/10">
                            <button
                              type="button"
                              (click)="setVisualMirrorMode('CURRENT')"
                              [class]="visualMirrorMode() === 'CURRENT' ? 'bg-black text-white shadow-xs' : 'text-zinc-600 hover:text-black'"
                              class="px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center justify-center gap-1.5"
                            >
                              <span>{{ drJefService.language() === 'EN' ? 'View Current Path (Risk ' + ((horizon.burnout_risk * 100) | number:'1.0-0') + '%' + ')' : 'Ver Mi Camino Actual (Riesgo ' + ((horizon.burnout_risk * 100) | number:'1.0-0') + '%' + ')' }}</span>
                            </button>

                            <button
                              type="button"
                              (click)="setVisualMirrorMode('OPTIMAL')"
                              [class]="visualMirrorMode() === 'OPTIMAL' ? 'bg-[#FF5500] text-white shadow-xs' : 'text-zinc-600 hover:text-black'"
                              class="px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center justify-center gap-1"
                            >
                              <span>{{ drJefService.language() === 'EN' ? '✨ View Mirror Future Golden Path' : '✨ Ver Camino Óptimo Mirror Future' }}</span>
                            </button>
                          </div>
                        </div>

                      </div>



                      <!-- Escenario Visual y Modo Video Cinematográfico -->
                      <div class="space-y-3">
                        <!-- Banner de Estado de la Foto de Referencia (Solo si hay foto vinculada) -->
                        @if (userPhotoPreview()) {
                          <div class="flex items-center justify-between p-2.5 rounded-xl bg-zinc-100 border border-black/10 text-xs shadow-xs">
                            <div class="flex items-center gap-2.5 min-w-0">
                              <img [src]="userPhotoPreview()" class="w-8 h-8 rounded-lg object-cover border border-black/20 shrink-0 shadow-xs" alt="Ref" />
                              <div class="min-w-0">
                                <span class="font-bold text-zinc-900 block leading-tight flex items-center gap-1.5 truncate">
                                  <span class="w-2 h-2 rounded-full bg-emerald-500 shrink-0"></span>
                                  {{ drJefService.language() === 'EN' ? 'Simulation linked to your reference photo' : 'Simulación vinculada a tu foto de referencia real' }}
                                </span>
                                <span class="text-[10px] text-zinc-500 block truncate">
                                  {{ drJefService.language() === 'EN' ? 'Your future self and video are rendered directly from your face' : 'Tu futuro yo e imagen/video se generan a partir de tu propio rostro' }}
                                </span>
                              </div>
                            </div>
                            <div class="flex items-center gap-2 shrink-0">
                              <label class="px-2.5 py-1 rounded-lg bg-white border border-black/15 text-[11px] font-bold text-zinc-700 hover:text-black cursor-pointer shadow-xs transition">
                                {{ drJefService.language() === 'EN' ? 'Change Photo' : 'Cambiar Foto' }}
                                <input type="file" (change)="onPhotoUpload($event)" accept="image/*" class="hidden" />
                              </label>
                              <button type="button" (click)="removeUserPhoto()" class="text-xs text-red-500 hover:text-red-700 font-bold px-1.5 py-1 rounded-md hover:bg-red-50 cursor-pointer">
                                ✕
                              </button>
                            </div>
                          </div>
                        } @else {
                          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-amber-950 text-xs shadow-xs">
                            <div class="flex items-center gap-2.5 min-w-0">
                              <span class="text-xl shrink-0">📷</span>
                              <div class="min-w-0">
                                <span class="font-bold text-amber-900 block leading-tight">
                                  {{ drJefService.language() === 'EN' ? 'No real photo linked (using conceptual AI face)' : 'Sin foto real vinculada (mostrando rostro conceptual con IA)' }}
                                </span>
                                <span class="text-[11px] text-amber-800/80 block mt-0.5">
                                  {{ drJefService.language() === 'EN' ? 'Upload your photo to project YOUR real face in the video and prevent synthetic faces.' : 'Sube tu foto para proyectar TU rostro exacto en el video y evitar rostros inventados.' }}
                                </span>
                              </div>
                            </div>
                            <label class="px-3.5 py-1.5 rounded-xl bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs cursor-pointer shadow-xs transition flex items-center justify-center gap-1.5 shrink-0">
                              <span>📷</span>
                              <span>{{ drJefService.language() === 'EN' ? 'Upload My Photo' : 'Subir Mi Foto Real' }}</span>
                              <input type="file" (change)="onPhotoUpload($event)" accept="image/*" class="hidden" />
                            </label>
                          </div>
                        }

                        <!-- Contenedor del Visor Cinematográfico (Imagen o Video) -->
                        <div class="relative w-full aspect-[16/9] sm:aspect-[21/9] rounded-2xl overflow-hidden bg-zinc-950 border border-black/15 shadow-inner group select-none">
                          
                          <!-- Si el modo video está activo y reproduciendo -->
                          @if (isVideoModeActive() && horizon.future_self_video_url) {
                            <video
                              [src]="getVideoUrl(horizon)"
                              autoplay
                              loop
                              muted
                              playsinline
                              class="w-full h-full object-cover"
                            ></video>
                          } @else {
                            <!-- Imagen con Movimiento de Cámara suave (Scale/Pan - Ken Burns) -->
                            <img
                              [src]="getMirrorImageUrl(horizon)"
                              [alt]="getMirrorCaption(horizon)"
                              class="w-full h-full object-cover transition-transform duration-700 ease-out"
                              [ngClass]="{
                                'animate-cinematic-pan scale-105': isCinematicVoicePlaying(),
                                'group-hover:scale-102': !isCinematicVoicePlaying()
                              }"
                            />
                          }

                          <!-- Gradient Overlay cinematográfico -->
                          <div class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/35 to-black/20 pointer-events-none"></div>

                          <!-- Badge superior izquierdo: Estado y Selector de Foto vs Futuro Yo -->
                          <div class="absolute top-3 left-3 flex items-center gap-2 z-10 flex-wrap">
                            <span
                              class="px-2.5 py-1 rounded-full text-[10px] font-mono font-bold uppercase tracking-wider backdrop-blur-md shadow-xs border"
                              [ngClass]="visualMirrorMode() === 'OPTIMAL' ? 'bg-emerald-500/80 border-emerald-400 text-white' : (horizon.burnout_risk >= 0.45 ? 'bg-red-600/80 border-red-400 text-white' : 'bg-black/60 border-white/20 text-white')"
                            >
                              {{ visualMirrorMode() === 'OPTIMAL' ? (drJefService.language() === 'EN' ? '✨ Mirror Future Golden Path' : '✨ Camino Óptimo Mirror Future') : (drJefService.language() === 'EN' ? 'Current Inertial Route' : 'Ruta Inercial Actual') }}
                            </span>

                            <!-- Selector Comparativo: Futuro Yo vs Foto Original -->
                            @if (userPhotoPreview() || horizon.reference_photo_url) {
                              <div class="inline-flex rounded-full p-0.5 bg-black/70 backdrop-blur-md border border-white/25 text-[10px] font-bold shadow-xs">
                                <button
                                  type="button"
                                  (click)="showOriginalPhoto.set(false)"
                                  [class]="!showOriginalPhoto() ? 'bg-[#FF5500] text-white px-2.5 py-0.5 rounded-full shadow-xs' : 'text-zinc-300 hover:text-white px-2.5 py-0.5 cursor-pointer'"
                                >
                                  🔮 {{ drJefService.language() === 'EN' ? 'Future Self' : 'Futuro Yo' }}
                                </button>
                                <button
                                  type="button"
                                  (click)="showOriginalPhoto.set(true)"
                                  [class]="showOriginalPhoto() ? 'bg-white text-black px-2.5 py-0.5 rounded-full shadow-xs' : 'text-zinc-300 hover:text-white px-2.5 py-0.5 cursor-pointer'"
                                >
                                  📸 {{ drJefService.language() === 'EN' ? 'My Photo' : 'Mi Foto' }}
                                </button>
                              </div>
                            }
                          </div>

                          <!-- Indicador En Vivo / Ondas de Audio si está reproduciendo -->
                          @if (isCinematicVoicePlaying()) {
                            <div class="absolute top-3 right-3 flex items-center gap-2 z-10 bg-black/75 backdrop-blur-md px-3 py-1 rounded-full border border-white/20 text-white text-[11px] font-mono shadow-md">
                              <span class="w-2 h-2 rounded-full bg-red-500 animate-ping"></span>
                              <span class="text-xs font-bold text-red-400">{{ drJefService.language() === 'EN' ? 'LIVE SIMULATION' : 'SIMULACIÓN EN VIVO' }}</span>
                              <div class="flex items-end gap-0.5 h-3.5 px-0.5">
                                <span class="w-1 bg-[#FF5500] rounded-full animate-audio-bar-1 h-2"></span>
                                <span class="w-1 bg-[#FF5500] rounded-full animate-audio-bar-2 h-3.5"></span>
                                <span class="w-1 bg-[#FF5500] rounded-full animate-audio-bar-3 h-1.5"></span>
                                <span class="w-1 bg-[#FF5500] rounded-full animate-audio-bar-2 h-2.5"></span>
                              </div>
                            </div>
                          }

                          <!-- Contenido Inferior: Subtítulos en pantalla o Pie de Foto -->
                          <div class="absolute inset-x-0 bottom-0 p-3 sm:p-5 flex flex-col justify-end z-10 space-y-2">
                            @if (isCinematicVoicePlaying()) {
                              <div class="bg-black/85 backdrop-blur-md border border-white/20 rounded-xl p-3 sm:p-4 text-center max-w-3xl mx-auto shadow-2xl">
                                <div class="text-[10px] font-mono text-[#FF5500] uppercase tracking-widest font-black mb-1 flex items-center justify-center gap-1.5">
                                  <span>🎙️</span> {{ drJefService.language() === 'EN' ? 'Your Future Self Speaking to You:' : 'Tu Yo del Futuro Hablándote:' }}
                                </div>
                                <p class="text-xs sm:text-sm md:text-base font-semibold text-white leading-relaxed drop-shadow-md">
                                  "{{ getMirrorVoiceScript(horizon) }}"
                                </p>
                              </div>
                            } @else {
                              <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
                                <p class="text-xs sm:text-sm text-white/95 font-medium leading-snug drop-shadow-md max-w-2xl">
                                  {{ getMirrorCaption(horizon) }}
                                </p>
                                <span class="text-[10px] font-mono text-zinc-300 shrink-0 bg-black/40 px-2 py-0.5 rounded-md backdrop-blur-xs border border-white/10">
                                  {{ selectedHorizonKey() === '1_MONTH' ? '30D' : (selectedHorizonKey() === '6_MONTHS' ? '180D' : '365D') }} &bull; {{ realitySeed.location.city || (drJefService.language() === 'EN' ? 'City' : 'Ciudad') }}
                                </span>
                              </div>
                            }
                          </div>
                        </div>

                        <!-- Acciones del Espejo: Reproducir Video, Descargar MP4 y Nota de Calibración -->
                        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pt-1">
                          <div class="flex items-center gap-2 flex-wrap w-full sm:w-auto">
                            @if (!isCinematicVoicePlaying()) {
                              <button
                                type="button"
                                (click)="playCinematicSimulation(horizon)"
                                class="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-black hover:bg-[#FF5500] text-white font-black text-xs uppercase tracking-wider transition-all duration-200 flex items-center justify-center gap-2 shadow-md hover:shadow-lg active:scale-95 cursor-pointer"
                              >
                                <span>🎬</span>
                                <span>{{ drJefService.language() === 'EN' ? 'Play Video & Voice Simulation' : 'Reproducir Video y Voz de tu Futuro Yo' }}</span>
                              </button>
                            } @else {
                              <button
                                type="button"
                                (click)="stopCinematicSimulation()"
                                class="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-red-600 hover:bg-red-700 text-white font-black text-xs uppercase tracking-wider transition-all duration-200 flex items-center justify-center gap-2 shadow-md hover:shadow-lg active:scale-95 cursor-pointer animate-pulse"
                              >
                                <span>⏹️</span>
                                <span>{{ drJefService.language() === 'EN' ? 'Stop Video Simulation' : 'Detener Simulación de Video' }}</span>
                              </button>
                            }

                            <!-- Botón Descargar Video MP4 -->
                            <a
                              [href]="getVideoDownloadUrl(horizon)" target="_blank"
                              [download]="'mirror_future_future_self_' + selectedHorizonKey() + '.mp4'"
                              class="px-4 py-2.5 rounded-xl bg-zinc-200 hover:bg-zinc-300 text-zinc-900 font-bold text-xs transition flex items-center justify-center gap-1.5 shadow-xs cursor-pointer"
                              [title]="drJefService.language() === 'EN' ? 'Download future self cinematic video (.mp4)' : 'Descargar video cinemático (.mp4)'"
                            >
                              <span>⬇</span>
                              <span>{{ drJefService.language() === 'EN' ? 'Download MP4' : 'Descargar Video MP4' }}</span>
                            </a>
                          </div>

                          <span class="text-[11px] text-zinc-500 font-mono leading-tight">
                            {{ userPhotoPreview() ? (drJefService.language() === 'EN' ? '✨ Identity anchored in your reference photo and calibrated by Monte Carlo simulation.' : '✨ Identidad anclada en tu foto de referencia y calibrada por simulación Monte Carlo.') : (drJefService.language() === 'EN' ? 'AI conceptual image generated from your projected metrics.' : 'Imagen conceptual proyectada a partir de tus métricas.') }}
                          </span>
                        </div>
                      </div>

                    </div>



                    <!-- BARRA COMPACTA: INTELIGENCIA EN TIEMPO REAL CONSULTADA HOY -->

                    <div class="p-3.5 sm:p-4 rounded-2xl bg-[#F5F5F7] border border-black/10 space-y-3">

                      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-0.5">

                        <div class="flex items-center gap-2">

                          <span class="text-xs font-bold text-zinc-900 font-mono flex items-center gap-1.5">

                            {{ drJefService.language() === 'EN' ? '🌐 Real Market in ' + (realitySeed.location.city || 'your City') + ' (Economy, Salaries & Companies)' : '🌐 Mercado Real en ' + (realitySeed.location.city || 'tu Ciudad') + ' (Economía, Sueldos y Empresas)' }}

                          </span>

                        </div>

                        <div class="flex items-center gap-1.5 self-start sm:self-auto">

                          <span class="inline-flex items-center gap-1 text-[10px] font-mono font-semibold text-emerald-800 bg-emerald-100 border border-emerald-300/60 px-2 py-0.5 rounded-full">

                            <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>

                            <span>Live Grounding</span>

                          </span>

                          <span class="text-[11px] text-zinc-500 font-mono">

                            {{ getLiveWebSources(resp).length }} {{ drJefService.language() === 'EN' ? 'sources' : 'fuentes' }}

                          </span>

                        </div>

                      </div>



                      @if (resp.live_web_intelligence) {

                        <!-- Rango Salarial Local vs Remoto y Empresas Detectadas -->

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">

                          <div class="p-2.5 bg-white rounded-xl border border-black/10 flex items-center justify-between">

                            <div>

                              <span class="text-[10px] text-zinc-500 font-mono block">{{ drJefService.language() === 'EN' ? 'Salary Range in ' + (realitySeed.location.city || 'City') : 'Rango Salarial en ' + (realitySeed.location.city || 'Ciudad') }}</span>

                              <span class="font-bold text-zinc-900 font-mono">

                                {{ getCurrencySymbol() }}{{ resp.live_web_intelligence.local_salary_range_min || 1200 }} - {{ getCurrencySymbol() }}{{ resp.live_web_intelligence.local_salary_range_max || 3000 }} {{ realitySeed.finances.currency || 'USD' }}/m

                              </span>

                            </div>

                            <span class="text-xs px-2 py-0.5 rounded-md bg-blue-50 text-blue-700 font-semibold border border-blue-200">{{ drJefService.language() === 'EN' ? 'Local' : 'Local' }}</span>

                          </div>



                          <div class="p-2.5 bg-white rounded-xl border border-black/10 flex items-center justify-between">

                            <div>

                              <span class="text-[10px] text-zinc-500 font-mono block">{{ drJefService.language() === 'EN' ? 'Remote / National Range' : 'Rango Remoto / Nacional' }}</span>

                              <span class="font-bold text-emerald-700 font-mono">

                                {{ getCurrencySymbol() }}{{ resp.live_web_intelligence.remote_salary_range_min || 2500 }} - {{ getCurrencySymbol() }}{{ resp.live_web_intelligence.remote_salary_range_max || 6000 }} {{ realitySeed.finances.currency || 'USD' }}/m

                              </span>

                            </div>

                            <span class="text-xs px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-700 font-semibold border border-emerald-200">{{ drJefService.language() === 'EN' ? 'Remote' : 'Remoto' }}</span>

                          </div>

                        </div>



                        @if (resp.live_web_intelligence.local_companies_found && resp.live_web_intelligence.local_companies_found.length > 0) {

                          <div class="px-3 py-2 bg-white rounded-xl border border-black/10 text-[11px] flex items-center gap-2">

                            <span class="font-bold text-zinc-700 shrink-0">{{ drJefService.language() === 'EN' ? '🏢 Companies in ' + (realitySeed.location.city || 'the city') + ':' : '🏢 Empresas en ' + (realitySeed.location.city || 'la ciudad') + ':' }}</span>

                            <span class="text-zinc-600 truncate">{{ resp.live_web_intelligence.local_companies_found.join(' • ') }}</span>

                          </div>

                        }

                      }



                      <!-- Píldoras Clicables de Fuentes Reales -->

                      <div class="flex flex-wrap gap-2 pt-0.5">

                        @for (source of getLiveWebSources(resp); track source.url + source.title) {

                          <a

                            [href]="source.url"

                            target="_blank"

                            rel="noopener noreferrer"

                            class="group inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white border border-black/10 hover:border-[#FF5500] hover:shadow-sm text-zinc-800 hover:text-black transition-all cursor-pointer text-xs"

                            [title]="(drJefService.language() === 'EN' ? 'Open source in new tab: ' : 'Abrir fuente en pestaña nueva: ') + source.title"

                          >

                            <span class="px-1.5 py-0.5 rounded-md text-[10px] font-mono font-bold uppercase tracking-wider bg-zinc-100 text-zinc-600 group-hover:bg-[#FF5500]/10 group-hover:text-[#FF5500] transition-colors">

                              {{ source.category }}

                            </span>

                            <span class="font-medium text-xs truncate max-w-[180px] sm:max-w-[260px] md:max-w-xs text-zinc-900 group-hover:text-black">

                              {{ source.title }}

                            </span>

                            <span class="text-zinc-400 group-hover:text-[#FF5500] text-xs font-bold transition-transform group-hover:translate-x-0.5">

                              ↗

                            </span>

                          </a>

                        }

                      </div>

                    </div>



                    <!-- Radar 5D de Puntuación -->

                    <div class="grid grid-cols-2 sm:grid-cols-5 gap-2 pt-2">

                      <div class="p-2.5 rounded-xl bg-[#F5F5F7] border border-black/10 text-center">

                        <span class="text-[10px] text-zinc-500 block font-medium">{{ drJefService.language() === 'EN' ? 'Finances' : 'Finanzas' }}</span>

                        <span class="text-base font-black text-black font-mono">{{ horizon.scores_5d.finances }}/100</span>

                      </div>

                      <div class="p-2.5 rounded-xl bg-[#F5F5F7] border border-black/10 text-center">

                        <span class="text-[10px] text-zinc-500 block font-medium">{{ drJefService.language() === 'EN' ? 'Energy' : 'Energía' }}</span>

                        <span class="text-base font-black text-black font-mono">{{ horizon.scores_5d.health_energy }}/100</span>

                      </div>

                      <div class="p-2.5 rounded-xl bg-[#F5F5F7] border border-black/10 text-center">

                        <span class="text-[10px] text-zinc-500 block font-medium">{{ drJefService.language() === 'EN' ? 'Career' : 'Carrera' }}</span>

                        <span class="text-base font-black text-black font-mono">{{ horizon.scores_5d.career }}/100</span>

                      </div>

                      <div class="p-2.5 rounded-xl bg-[#F5F5F7] border border-black/10 text-center">

                        <span class="text-[10px] text-zinc-500 block font-medium">{{ drJefService.language() === 'EN' ? 'Relationships' : 'Vínculos' }}</span>

                        <span class="text-base font-black text-black font-mono">{{ horizon.scores_5d.relationships }}/100</span>

                      </div>

                      <div class="p-2.5 rounded-xl bg-[#F5F5F7] border border-black/10 text-center col-span-2 sm:col-span-1">

                        <span class="text-[10px] text-zinc-500 block font-medium">{{ drJefService.language() === 'EN' ? 'Resilience' : 'Resiliencia' }}</span>

                        <span class="text-base font-black text-black font-mono">{{ horizon.scores_5d.macro_resilience }}/100</span>

                      </div>

                    </div>



                  </div>



                </section>

                <!-- ============================================================== -->
                <!-- VERIFICACIÓN CAUSAL DE METAS E IDEALES (1A, 2-3A, 5A+)         -->
                <!-- ============================================================== -->
                @if (resp.goals_verification) {
                  <section class="bg-white/95 border border-black/10 rounded-3xl p-6 md:p-8 shadow-xl text-zinc-900 space-y-6">
                    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-4 border-b border-black/10 gap-3">
                      <div>
                        <span class="text-xs font-mono font-bold uppercase tracking-wider text-[#FF5500] block">
                          {{ drJefService.language() === 'EN' ? 'Causal Reality Check • Multi-Horizon Goals & Ideals' : 'Auditoría Causal • Metas e Ideales en Múltiples Horizontes' }}
                        </span>
                        <h3 class="text-xl md:text-2xl font-black text-black flex items-center gap-2">
                          <span>🎯</span> {{ drJefService.language() === 'EN' ? 'Empirical Feasibility of Your Goals & Dreams' : '¿Se están cumpliendo tus metas e ideales reales?' }}
                        </h3>
                      </div>
                      <span class="text-xs font-mono font-bold px-3 py-1 rounded-full bg-black/5 border border-black/10 text-zinc-700">
                        {{ drJefService.language() === 'EN' ? 'Validation 1Y · 3Y · 5Y+' : 'Validación 1A · 3A · 5A+' }}
                      </span>
                    </div>

                    <!-- Veredicto General -->
                    <div class="p-4 rounded-2xl bg-amber-50/90 border border-amber-200/80 space-y-1.5">
                      <div class="flex items-center gap-2">
                        <span class="text-amber-600 font-bold text-sm">⚖️</span>
                        <span class="text-xs font-mono uppercase tracking-wider font-bold text-amber-900">
                          {{ drJefService.language() === 'EN' ? 'Audit Summary & Reality Verdict' : 'Dictamen Global de Cumplimiento' }}
                        </span>
                      </div>
                      <p class="text-xs text-amber-950 font-medium leading-relaxed">
                        {{ resp.goals_verification.global_synthesis }}
                      </p>
                    </div>

                    <!-- Lista de Metas Evaluadas en Horizontes -->
                    <div class="space-y-4">
                      @for (g of getEvaluatedGoals(resp.goals_verification); track g.horizon_type) {
                        <div class="p-4 rounded-2xl border transition-all"
                             [ngClass]="{
                               'bg-emerald-50/60 border-emerald-300': g.feasibility_status === 'VIABLE_ON_TRACK',
                               'bg-amber-50/60 border-amber-300': g.feasibility_status === 'AT_RISK_GAPS',
                               'bg-rose-50/60 border-rose-300': g.feasibility_status === 'NOT_FEASIBLE_INSUFFICIENT_RESOURCES'
                             }">
                          <!-- Header Meta -->
                          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2.5 border-b border-black/5">
                            <div class="flex items-center gap-2">
                              <span class="text-xs font-mono font-bold px-2 py-0.5 rounded-md bg-white border border-black/10 text-zinc-800">
                                {{ g.horizon_label }}
                              </span>
                              <span class="text-xs font-bold text-zinc-900">
                                {{ g.goal_statement }}
                              </span>
                            </div>

                            <!-- Badge Estado -->
                            <div class="flex items-center gap-2 self-start sm:self-auto">
                              <span class="text-xs font-mono font-bold px-2.5 py-1 rounded-full text-white"
                                    [ngClass]="{
                                      'bg-emerald-600': g.feasibility_status === 'VIABLE_ON_TRACK',
                                      'bg-amber-600': g.feasibility_status === 'AT_RISK_GAPS',
                                      'bg-rose-600': g.feasibility_status === 'NOT_FEASIBLE_INSUFFICIENT_RESOURCES'
                                    }">
                                {{ g.feasibility_status === 'VIABLE_ON_TRACK' ? (drJefService.language() === 'EN' ? 'FEASIBLE' : 'VIABLE') :
                                   g.feasibility_status === 'AT_RISK_GAPS' ? (drJefService.language() === 'EN' ? 'PARTIAL / CONDITIONAL' : 'PARCIAL / CONDICIONADA') :
                                   (drJefService.language() === 'EN' ? 'CRITICAL GAP' : 'BRECHA CRÍTICA') }}
                              </span>
                              <span class="text-xs font-mono font-black text-zinc-700">
                                {{ g.feasibility_pct }}%
                              </span>
                            </div>
                          </div>

                          <!-- Barra de Factibilidad -->
                          <div class="w-full bg-black/10 rounded-full h-2 my-2.5 overflow-hidden">
                            <div class="h-full rounded-full transition-all duration-500"
                                 [style.width.%]="g.feasibility_pct"
                                 [ngClass]="{
                                   'bg-emerald-500': g.feasibility_pct >= 65,
                                   'bg-amber-500': g.feasibility_pct >= 35 && g.feasibility_pct < 65,
                                   'bg-rose-500': g.feasibility_pct < 35
                                 }"></div>
                          </div>

                          <!-- Desglose Financiero: Requerido vs Proyectado vs Brecha -->
                          <div class="grid grid-cols-1 sm:grid-cols-3 gap-2 py-2 text-xs font-mono">
                            <div class="p-2 rounded-xl bg-white/80 border border-black/5">
                              <span class="text-[10px] text-zinc-500 block uppercase">{{ drJefService.language() === 'EN' ? 'Capital Needed' : 'Capital Requerido' }}</span>
                              <span class="text-xs font-bold text-zinc-900">{{ getCurrencySymbol() }} {{ g.required_capital | number:'1.0-0' }}</span>
                            </div>
                            <div class="p-2 rounded-xl bg-white/80 border border-black/5">
                              <span class="text-[10px] text-zinc-500 block uppercase">{{ drJefService.language() === 'EN' ? 'Projected Savings' : 'Ahorro Proyectado' }}</span>
                              <span class="text-xs font-bold text-emerald-700">{{ getCurrencySymbol() }} {{ g.projected_savings_capital | number:'1.0-0' }}</span>
                            </div>
                            <div class="p-2 rounded-xl bg-white/80 border border-black/5">
                              <span class="text-[10px] text-zinc-500 block uppercase">{{ drJefService.language() === 'EN' ? 'Capital Gap / Deficit' : 'Déficit / Brecha' }}</span>
                              <span class="text-xs font-bold" [ngClass]="g.capital_gap > 0 ? 'text-rose-600' : 'text-emerald-700'">
                                {{ g.capital_gap > 0 ? ('-' + getCurrencySymbol() + ' ' + (g.capital_gap | number:'1.0-0')) : (drJefService.language() === 'EN' ? 'Covered' : 'Cubierto') }}
                              </span>
                            </div>
                          </div>

                          <!-- Veredicto de Realidad -->
                          <div class="mt-2 text-xs font-medium text-zinc-800 bg-white/70 p-2.5 rounded-xl border border-black/5 leading-relaxed">
                            <span class="font-bold text-zinc-900">📌 {{ drJefService.language() === 'EN' ? 'Reality Check:' : 'Examen de Realidad:' }}</span>
                            {{ g.reality_check_verdict }}
                          </div>

                          <!-- Prerrequisitos Faltantes vs Cumplidos -->
                          @if (g.prerequisites_missing && g.prerequisites_missing.length > 0) {
                            <div class="mt-2 text-[11px] text-rose-800 bg-rose-50 p-2 rounded-xl border border-rose-200/60">
                              <span class="font-bold">⚠️ {{ drJefService.language() === 'EN' ? 'Missing Prerequisites to achieve this:' : 'Prerrequisitos faltantes para cumplirlo:' }}</span>
                              <ul class="list-disc list-inside mt-0.5 space-y-0.5 font-medium">
                                @for (pre of g.prerequisites_missing; track $index) {
                                  <li>{{ pre }}</li>
                                }
                              </ul>
                            </div>
                          }

                          @if (g.prerequisites_met && g.prerequisites_met.length > 0) {
                            <div class="mt-1.5 text-[11px] text-emerald-800 bg-emerald-50 p-2 rounded-xl border border-emerald-200/60">
                              <span class="font-bold">✅ {{ drJefService.language() === 'EN' ? 'Strengths & Met Prerequisites:' : 'Fortalezas y prerrequisitos cubiertos:' }}</span>
                              <ul class="list-disc list-inside mt-0.5 space-y-0.5 font-medium">
                                @for (m of g.prerequisites_met; track $index) {
                                  <li>{{ m }}</li>
                                }
                              </ul>
                            </div>
                          }

                          <!-- Recomendación / Puente Estratégico -->
                          <div class="mt-2 text-[11px] text-zinc-700 italic border-l-2 border-[#FF5500] pl-2.5 py-0.5">
                            <span class="font-bold not-italic text-zinc-900">💡 {{ drJefService.language() === 'EN' ? 'Strategic Bridge:' : 'Puente Estratégico:' }}</span>
                            {{ g.strategic_bridge }}
                          </div>
                        </div>
                      }
                    </div>

                    <!-- Síntesis Estratégica Global -->
                    <div class="p-4 rounded-2xl bg-zinc-900 text-white space-y-2">
                      <span class="text-xs font-mono font-bold text-[#FF5500] uppercase tracking-wider block">
                        🚀 {{ drJefService.language() === 'EN' ? 'Actionable Blueprint to Close Feasibility Gaps' : 'Plan de Acción para Cerrar la Brecha y Cumplir tus Ideales' }}
                      </span>
                      <p class="text-xs text-zinc-200 leading-relaxed">
                        {{ resp.goals_verification.global_synthesis }}
                      </p>
                    </div>
                  </section>
                }

                <!-- ============================================================== -->
                <!-- NIVEL 2: CAUSAS RAÍZ Y PALANCAS DEL CAMINO DORADO             -->

                <!-- ============================================================== -->

                <section class="bg-white/95 border border-black/10 rounded-3xl p-6 md:p-8 shadow-xl text-zinc-900 space-y-6">

                  

                  <div class="pb-3 border-b border-black/10">

                    <span class="text-xs font-mono font-bold uppercase tracking-wider text-[#FF5500] block">

                      {{ drJefService.language() === 'EN' ? 'Level 2 • Causal Diagnosis & Levers' : 'Nivel 2 • Diagnóstico Causal & Palancas' }}

                    </span>

                    <h3 class="text-xl font-black text-black">

                      {{ drJefService.language() === 'EN' ? 'Why does this happen and how to intervene in your future?' : '¿Por qué ocurre esto y cómo intervenir tu futuro?' }}

                    </h3>

                  </div>



                  <!-- 3 Causas Raíz -->

                  <div class="space-y-3">

                    <span class="text-xs font-bold text-zinc-800 uppercase tracking-wider block font-mono">

                      {{ drJefService.language() === 'EN' ? 'The 3 Root Causes of your Trajectory:' : 'Las 3 Causas Raíz de tu Trayectoria:' }}

                    </span>

                    

                    <div class="grid grid-cols-1 md:grid-cols-3 gap-3">

                      @for (rc of resp.root_causes; track rc.rank) {

                        <div class="p-4 rounded-2xl bg-[#F5F5F7] border border-black/10 space-y-2">

                          <div class="flex items-center gap-2">

                            <span class="w-5 h-5 rounded-full bg-black text-white font-mono text-[10px] font-bold flex items-center justify-center shrink-0">

                              {{ rc.rank }}

                            </span>

                            <span class="text-[11px] font-bold text-zinc-700 uppercase tracking-wider truncate">

                              {{ rc.category }}

                            </span>

                          </div>

                          <h4 class="text-xs font-bold text-black leading-snug">

                            {{ rc.title }}

                          </h4>

                          <p class="text-[11px] text-zinc-600 leading-relaxed font-normal">

                            {{ rc.description }}

                          </p>

                          <div class="p-2 rounded bg-white border border-black/5 text-[10px] text-zinc-500 italic">

                            {{ rc.evidence_quote }}

                          </div>

                        </div>

                      }

                    </div>

                  </div>



                  <!-- Palancas de Rescate del Camino Dorado -->

                  <div class="space-y-3 pt-2 border-t border-black/10">

                    <div class="flex items-center justify-between">

                      <span class="text-xs font-bold text-zinc-800 uppercase tracking-wider font-mono">

                        {{ drJefService.language() === 'EN' ? 'Golden Path Rescue Levers:' : 'Palancas del Camino Dorado:' }}

                      </span>

                      <button

                        type="button"

                        (click)="downloadIcs()"

                        [disabled]="isDownloadingIcs()"

                        class="px-4 py-2 rounded-xl bg-[#FF5500] hover:bg-black text-white font-bold text-xs uppercase tracking-wider transition cursor-pointer flex items-center gap-2 shadow-sm">

                        @if (isDownloadingIcs()) {

                          <span>{{ drJefService.language() === 'EN' ? 'Generating Schedule...' : 'Generando Horario...' }}</span>

                        } @else {

                          <span>{{ drJefService.language() === 'EN' ? '📅 Download Schedule (.ICS)' : '📅 Descargar Horario .ICS' }}</span>

                        }

                      </button>

                    </div>



                    <div class="grid grid-cols-1 md:grid-cols-3 gap-3">

                      @for (adj of resp.golden_path_adjustments; track adj.lever_title) {

                        <div class="p-4 rounded-2xl bg-[#FAF9F6] border border-black/10 space-y-2">

                          <div class="flex items-center justify-between">

                            <span class="text-xs font-bold text-black uppercase font-mono">{{ adj.lever_title }}</span>

                            <span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">

                              {{ adj.expected_gain }}

                            </span>

                          </div>

                          <div class="text-[11px] space-y-1">

                            <div class="text-zinc-500">

                              <span class="font-semibold text-zinc-700">{{ drJefService.language() === 'EN' ? 'Today:' : 'Hoy:' }}</span> {{ adj.current_trajectory_value }}

                            </div>

                            <div class="text-zinc-900 font-medium">

                              <span class="font-bold text-[#FF5500]">{{ drJefService.language() === 'EN' ? 'Mirror Future Target:' : 'Meta Mirror Future:' }}</span> {{ adj.optimal_dr_jef_value }}

                            </div>

                          </div>

                          <p class="text-[11px] text-zinc-600 font-normal pt-1">

                            {{ adj.actionable_prescription }}

                          </p>

                        </div>

                      }

                    </div>

                  </div>



                </section>



                <!-- ============================================================== -->

                <!-- NIVEL 3: LABORATORIO CIENTÍFICO (3D Y MONTE CARLO CHART)       -->

                <!-- ============================================================== -->

                <section class="bg-white/95 border border-black/10 rounded-3xl p-6 md:p-8 shadow-xl text-zinc-900 space-y-6">

                  

                  <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-3 border-b border-black/10 gap-3">

                    <div>

                      <span class="text-xs font-mono font-bold uppercase tracking-wider text-zinc-500 block">

                        {{ drJefService.language() === 'EN' ? 'Level 3 • Scientific Laboratory' : 'Nivel 3 • Laboratorio Científico' }}

                      </span>

                      <h3 class="text-xl font-black text-black">

                        {{ drJefService.language() === 'EN' ? 'Stochastic Simulation & Probability Curves' : 'Simulación Estocástica y Curvas de Probabilidad' }}

                      </h3>

                    </div>



                    <button

                      type="button"

                      (click)="toggleScientificLab()"

                      class="px-5 py-2 rounded-xl border-2 border-black bg-white hover:bg-black hover:text-white text-black font-bold text-xs uppercase tracking-wider transition cursor-pointer flex items-center gap-2">

                      <span>{{ showScientificLab() ? (drJefService.language() === 'EN' ? 'Hide 3D Curves' : 'Ocultar Curvas 3D') : (drJefService.language() === 'EN' ? 'View Monte Carlo Curves & 3D' : 'Ver Curvas Monte Carlo & 3D') }}</span>

                      <span>{{ showScientificLab() ? '▲' : '▼' }}</span>

                    </button>

                  </div>



                  @if (showScientificLab()) {

                    <div class="space-y-6 pt-2">

                      

                      <!-- Visor 3D Three.js -->

                      <div class="rounded-2xl overflow-hidden border border-black/20 shadow-xl bg-slate-950">

                        <app-dr-jef-causal-graph-3d

                          [curves]="drJefService.curves()"

                          [contacts]="drJefService.simulatedContacts()"

                          [branch]="drJefService.selectedBranch()"

                          [selectedDay]="drJefService.selectedDay()"

                          (contactSelected)="drJefService.selectContact($event)"

                          (branchSelected)="drJefService.selectBranch($event)"

                          (dayChanged)="drJefService.selectDay($event)"

                        />

                      </div>



                      <!-- Gráficos Monte Carlo SVG -->

                      <div class="rounded-2xl overflow-hidden border border-black/10 bg-slate-900 shadow-md">

                        <app-monte-carlo-chart

                          [curves]="drJefService.curves()"

                          [prescription]="drJefService.prescription()"

                          [diagnosis]="drJefService.diagnosis()"

                        />

                      </div>



                    </div>

                  }



                </section>


        </div>

        <!-- BOTÓN FLOTANTE PARA ABRIR MENÚ DE PARÁMETROS -->
        <button
          type="button"
          (click)="toggleParametersDrawer()"
          class="fixed bottom-6 right-6 z-40 px-5 py-3 rounded-full bg-black hover:bg-[#FF5500] text-white text-xs font-black uppercase tracking-wider shadow-2xl flex items-center gap-2 cursor-pointer transition active:scale-95 border-2 border-white/20">
          <span>⚙️</span>
          <span>{{ drJefService.language() === 'EN' ? 'Adjust Parameters' : 'Ajustar Parámetros' }}</span>
        </button>

        <!-- MENÚ DESPLEGABLE LATERAL (DRAWER) -->
        @if (isParametersDrawerOpen()) {
          <div
            (click)="closeParametersDrawer()"
            class="fixed inset-0 bg-black/60 backdrop-blur-xs z-50 transition-opacity">
          </div>

          <div
            class="fixed inset-y-0 right-0 z-50 w-full sm:w-[520px] bg-white shadow-2xl p-6 overflow-y-auto flex flex-col gap-5 border-l border-black/15 animate-slide-in text-zinc-900">
            
            <div class="flex items-center justify-between pb-3 border-b border-black/10 shrink-0">
              <div class="flex items-center gap-2.5">
                <div class="w-8 h-8 rounded-xl bg-black text-white flex items-center justify-center text-sm font-bold">
                  ⚙️
                </div>
                <div>
                  <h3 class="text-sm font-black uppercase font-mono text-black">
                    {{ drJefService.language() === 'EN' ? 'Simulation Parameters' : 'Ajuste de Parámetros' }}
                  </h3>
                  <span class="text-xs text-zinc-500">{{ drJefService.language() === 'EN' ? 'Tune your variables and recalculate' : 'Modifica tus variables y recalcula' }}</span>
                </div>
              </div>
              <button
                type="button"
                (click)="closeParametersDrawer()"
                class="w-8 h-8 rounded-full bg-zinc-100 hover:bg-zinc-200 text-zinc-700 flex items-center justify-center font-bold text-sm cursor-pointer transition">
                ✕
              </button>
            </div>

            <!-- Controles de Parámetros Reutilizados -->
            <div class="space-y-4">
              <ng-container *ngTemplateOutlet="parametersFormTemplate"></ng-container>
            </div>

            <!-- Botón Recalcular dentro del Drawer -->
            <div class="pt-3 border-t border-black/10 shrink-0 sticky bottom-0 bg-white">
              <button
                type="button"
                (click)="recalculateFromDrawer()"
                [disabled]="isLoading()"
                class="w-full py-4 rounded-2xl bg-black hover:bg-[#FF5500] text-white font-black text-xs uppercase tracking-wider shadow-xl transition active:scale-98 cursor-pointer flex items-center justify-center gap-2">
                <span>🔄</span>
                <span>{{ drJefService.language() === 'EN' ? 'Recalculate 1M, 6M & 1Y Prediction' : 'Recalcular Predicción a 1M, 6M y 1 Año' }}</span>
              </button>
            </div>
          </div>
        }
      }
    </div>
  `,

})

export class FutureSelfOracleV4Component implements OnInit, OnDestroy {

  private api = inject(DrJefApiService);

  private router = inject(Router);

  drJefService = inject(DrJefService);



  @Output() closeOracle = new EventEmitter<void>();



  goHome(): void {

    this.closeOracle.emit();

    this.router.navigate(['/']);

  }



  // Reality Seed State
  realitySeed: HolisticFutureRequest = {
    location: {
      country: '',
      city: '',
    },
    life_profile_type: 'UNIVERSITY_OR_TECH_STUDENT',
    goal_mode: false,
    lang: 'EN',
    age: 24,
    person_identifier: '',
    full_name: '',
    occupation: '',
    career_or_degree: '',
    daily_income_avg: 0,
    work_days_per_week: 0,
    daily_expense_avg: 0,
    physical_labor_intensity: 'LOW',
    housing_situation: 'FAMILY_HOME',
    one_year_goal: '',
    main_goal_1y: '',
    medium_term_goals: '',
    long_term_goals: '',
    target_monthly_salary_1y: 0,
    dependents_count: 0,
    household_climate: 'SUPPORTIVE',
    relationship_status: 'SINGLE_PEACEFUL',
    social_circle_influence: 'GROWTH',
    open_family_and_dependents: '',
    open_relationships_and_friends: '',
    open_personality_and_habits: '',
    self_description: '',
    personality_traits: [],
    chat_sentiment_avg: null,
    chat_dominant_tag: null,
    chat_median_reply_min: null,
    chat_extracted_summary: null,
    finances: {
      monthly_income: 0,
      monthly_expenses: 0,
      current_savings: 0,
      current_debt: 0,
      currency: 'PEN',
    },
    time_use: {
      sleep_hours: 0,
      work_hours: 0,
      study_project_hours: 0,
      screen_time_lost_hours: 0,
      exercise_hours: 0,
    },
    past_career_events: [],
  };

  // Signals para Motor Secuencial Life2Vec Laboral
  selectedCareerHorizonKey = signal<string>('all');
  selectedCareerHorizonIndex = signal<number>(0);
  isAddingCareerEvent = signal<boolean>(false);
  newCareerEvent: CareerLifeEvent = {
    year: new Date().getFullYear(),
    age_at_event: 24,
    event_type: 'FIRST_JOB',
    title_or_role: '',
    monthly_income: 0,
    location: '',
    description: ''
  };



    // Signals para Motor Conversacional & Dossier
  activeInputMode = signal<'INTERVIEW' | 'FORM'>('INTERVIEW');
  interviewHistory = signal<DiscoveryInterviewMessage[]>([]);
  interviewCompletenessPct = signal<number>(15);
  interviewPillarsCovered = signal<Record<string, boolean>>({});
  isInterviewThinking = signal<boolean>(false);
  interviewInputText = signal<string>('');
  fullPersonDossierText = signal<string>('');
  dossierGenerated = signal<boolean>(false);
  isSyncingDossier = signal<boolean>(false);
  isInterviewListening = signal<boolean>(false);
  private syncDebounceTimer: any = null;
  private voiceBaseText: string = '';
  private voiceAccumulatedFinal: string = '';
  private voiceRestartTimeout: any = null;
  private userManuallyStoppedVoice: boolean = false;

  uploadedFileName = signal<string | null>(null);
  validationError = signal<string | null>(null);

  isLoading = signal<boolean>(false);

  isDownloadingIcs = signal<boolean>(false);

  futureResponse = signal<HolisticFutureResponse | null>(null);



  // Dynamic progress message cycling

  dynamicProgressText = signal<string>('Analizando economía de tu país...');

  private progressInterval: any = null;



  // Progressive Disclosure State

  selectedHorizonKey = signal<'1_MONTH' | '6_MONTHS' | '1_YEAR'>('6_MONTHS');

  showScientificLab = signal<boolean>(false);



  // Collapsible sections state

  isFamilySectionOpen = signal<boolean>(false);

  isPersonalitySectionOpen = signal<boolean>(false);

  chatAnalysisBadge = signal<string | null>(null);



  // Voice dictation & AI Discovery state

  listeningField = signal<'open_family_and_dependents' | 'open_relationships_and_friends' | 'open_personality_and_habits' | null>(null);

  private speechRecognitionInstance: any = null;

  discoveryQuestions = signal<string[]>([]);

  isGeneratingQuestions = signal<boolean>(false);



  // Espejo Visual y Modo Video Cinematográfico

  visualMirrorMode = signal<'CURRENT' | 'OPTIMAL'>('CURRENT');

  isCinematicVoicePlaying = signal<boolean>(false);

  userPhotoPreview = signal<string | null>(null);
  showOriginalPhoto = signal<boolean>(false);
  isVideoModeActive = signal<boolean>(false);
  selectedRoadmapPhaseIndex = signal<number>(0);



  // Computeds

  monthlyCashflow = computed(() => {

    if (this.realitySeed.life_profile_type === 'DAY_TO_DAY_WORKER' && this.realitySeed.daily_income_avg) {

      const inc = (this.realitySeed.daily_income_avg || 0) * (this.realitySeed.work_days_per_week || 6) * 4.333;

      const exp = (this.realitySeed.daily_expense_avg || 0) * 30.417;

      return Math.round(inc - exp);

    }

    return Math.round((this.realitySeed.finances.monthly_income || 0) - (this.realitySeed.finances.monthly_expenses || 0));

  });



  totalAccountedHours = computed(() => {

    const t = this.realitySeed.time_use;

    return (t.sleep_hours || 0) + (t.work_hours || 0) + (t.study_project_hours || 0) + (t.screen_time_lost_hours || 0) + (t.exercise_hours || 0);

  });




  getCurrencyForCountry(country: string): string {
    const c = (country || '').trim().toLowerCase();
    if (c.includes('perú') || c.includes('peru') || c === 'pe') return 'PEN';
    if (c.includes('colombia') || c === 'co') return 'COP';
    if (c.includes('méxico') || c.includes('mexico') || c === 'mx') return 'MXN';
    if (c.includes('chile') || c === 'cl') return 'CLP';
    if (c.includes('argentina') || c === 'ar') return 'ARS';
    if (c.includes('españa') || c.includes('spain') || c === 'es') return 'EUR';
    if (c.includes('bolivia') || c === 'bo') return 'BOB';
    if (c.includes('ecuador') || c === 'ec') return 'USD';
    return 'USD';
  }

  getCurrencySymbol(currency?: string): string {
    const cur = (currency || this.realitySeed?.finances?.currency || 'PEN').toUpperCase();
    switch (cur) {
      case 'PEN': return 'S/';
      case 'COP': return '$';
      case 'MXN': return '$';
      case 'CLP': return '$';
      case 'ARS': return '$';
      case 'EUR': return '€';
      case 'BOB': return 'Bs';
      case 'USD': default: return '$';
    }
  }

  updateCurrencyByCountry(): void {
    const cur = this.getCurrencyForCountry(this.realitySeed?.location?.country || '');
    if (this.realitySeed?.finances) {
      this.realitySeed.finances.currency = cur;
    }
  }

  ngOnInit(): void {
    this.updateCurrencyByCountry();

    // Sincronizar idioma inicial

    this.realitySeed.lang = this.drJefService.language();
    this.initInterviewConversation();

  }



  ngOnDestroy(): void {

    this.stopCinematicSimulation();
    this.stopInterviewVoice();

    if (this.speechRecognitionInstance) {

      try { this.speechRecognitionInstance.stop(); } catch (_) {}

    }

    if (this.progressInterval) {

      clearInterval(this.progressInterval);

    }

  }



  setGoalMode(mode: boolean): void {

    this.realitySeed.goal_mode = mode;

    if (!mode) {

      this.realitySeed.one_year_goal = '';

      this.realitySeed.main_goal_1y = '';

    }

  }



  onProfileTypeChange(): void {
    if (this.realitySeed.finances) {
      if (this.realitySeed.finances.current_savings == null) this.realitySeed.finances.current_savings = 0;
      if (this.realitySeed.finances.current_debt == null) this.realitySeed.finances.current_debt = 0;
    }
    this.updateCurrencyByCountry();
  }

  private startProgressAnimation(): void {

    const isEs = this.drJefService.language() === 'ES';

    const profile = this.realitySeed.life_profile_type;

    const city = this.realitySeed.location.city?.trim() || (isEs ? 'tu ciudad' : 'your city');



    let messages: string[] = [];

    if (isEs) {

      if (profile === 'RURAL_FIELD_PRODUCER') {

        messages = [

          `Consultando precios agrícolas y clima en ${city}...`,

          'Analizando costo de insumos y transporte...',

          'Simulando 1,000 cosechas y volatilidad de mercado...',

          'Modelando desgaste físico y colchón de supervivencia...',

          'Sintetizando veredicto con Llama 3.3 70B...'

        ];

      } else if (profile === 'DAY_TO_DAY_WORKER' || profile === 'SKILLED_TRADE') {

        messages = [

          `Analizando canasta básica y costo de vida en ${city}...`,

          'Midiendo volatilidad de ingresos diarios y días sin venta...',

          'Simulando resistencia biológica y desgaste articular a 365 días...',

          'Calculando colchón de emergencia contra imprevistos...',

          'Sintetizando veredicto con Llama 3.3 70B...'

        ];

      } else {

        messages = [

          `Explorando mercado y empresas en ${city}...`,

          'Midiendo costo de vida local vs opciones remotas...',

          'Simulando transición y 1,000 trayectorias de carrera...',

          'Calculando probabilidad de estabilidad patrimonial...',

          'Sintetizando veredicto con Llama 3.3 70B...'

        ];

      }

    } else {

      messages = [

        `Analyzing living costs and local environment in ${city}...`,

        'Measuring daily income volatility and friction shocks...',

        'Simulating 1,000 Monte Carlo paths of vitality and cashflow...',

        'Calculating financial cushion and physical wear at 365 days...',

        'Synthesizing causal verdict with Llama 3.3 70B...'

      ];

    }



    let idx = 0;

    this.dynamicProgressText.set(messages[0]);

    if (this.progressInterval) clearInterval(this.progressInterval);

    this.progressInterval = setInterval(() => {

      idx = (idx + 1) % messages.length;

      this.dynamicProgressText.set(messages[idx]);

    }, 1400);

  }



  private stopProgressAnimation(): void {

    if (this.progressInterval) {

      clearInterval(this.progressInterval);

      this.progressInterval = null;

    }

  }



  hasEnteredUserData(): boolean {
    // 1. Mensajes del usuario en el chat
    const hasUserMessages = this.interviewHistory().some(
      m => m.role === 'user' && (m.content || '').trim().length > 0
    );
    if (hasUserMessages) return true;

    // 2. Archivo de chat subido o dossier ya generado
    if (this.uploadedFileName() && this.uploadedFileName()!.trim().length > 0) return true;
    if (this.fullPersonDossierText() && this.fullPersonDossierText().trim().length > 10) return true;

    // 3. Foto de referencia subida
    if (this.userPhotoPreview() || this.realitySeed.user_photo_base64) return true;

    // 4. Parámetros manuales
    const s = this.realitySeed;
    if ((s.full_name || s.person_identifier || '').trim().length > 0) return true;
    if ((s.career_or_degree || s.occupation || '').trim().length > 0) return true;
    if ((s.location?.city || '').trim().length > 0) return true;
    if (s.finances && (s.finances.monthly_income > 0 || s.finances.monthly_expenses > 0 || s.finances.current_savings > 0 || s.finances.current_debt > 0)) return true;
    if ((s.daily_income_avg && s.daily_income_avg > 0) || (s.daily_expense_avg && s.daily_expense_avg > 0)) return true;
    if ((s.one_year_goal || s.main_goal_1y || s.medium_term_goals || s.long_term_goals || '').trim().length > 0) return true;
    if ((s.self_description || '').trim().length > 0) return true;
    if (s.past_career_events && s.past_career_events.length > 0) return true;
    if (s.time_use && (s.time_use.work_hours > 0 || s.time_use.study_project_hours > 0)) return true;

    return false;
  }

  predictFuture(): void {
    if (!this.hasEnteredUserData()) {
      const isEs = this.drJefService.language() === 'ES';
      const msg = isEs
        ? '⚠️ No data has been entered yet. Please tell Mirror Future about yourself in the chat or fill in the form before predicting your future.'
        : '⚠️ No data has been entered yet. Please tell Mirror Future about yourself in the chat or fill in the form before predicting your future.';

      this.validationError.set(msg);

      if (this.activeInputMode() === 'INTERVIEW') {
        const chatNotice = isEs
          ? '⚠️ Para poder predecir tu futuro con rigor causal y científico, primero necesito conocerte. Por favor, responde a la pregunta de arriba sobre tu nombre, ocupación, ciudad y metas.'
          : '⚠️ To predict your future with scientific and causal rigor, I first need to learn about you. Please answer the questions above regarding your name, occupation, city, and goals.';

        const currentHist = this.interviewHistory();
        if (!currentHist.some(m => m.content.includes(chatNotice))) {
          this.interviewHistory.set([...currentHist, { role: 'assistant', content: chatNotice }]);
        }
      }
      return;
    }

    this.validationError.set(null);
    this.isLoading.set(true);
    this.startProgressAnimation();



    this.realitySeed.lang = this.drJefService.language();
    if (this.fullPersonDossierText()) {
      this.realitySeed.full_person_dossier_text = this.fullPersonDossierText();
    }



    if (this.realitySeed.career_or_degree) {
      this.realitySeed.occupation = this.realitySeed.career_or_degree;
    } else if (this.realitySeed.occupation) {
      this.realitySeed.career_or_degree = this.realitySeed.occupation;
    }

    if (this.realitySeed.full_name) {
      this.realitySeed.person_identifier = this.realitySeed.full_name;
    }

    // Sincronización financiera específica por arquetipo
    if (this.realitySeed.life_profile_type === 'DAY_TO_DAY_WORKER') {
      if (this.realitySeed.daily_income_avg && this.realitySeed.daily_income_avg > 0) {
        const days = this.realitySeed.work_days_per_week || 6;
        this.realitySeed.finances.monthly_income = Math.round(this.realitySeed.daily_income_avg * days * 4.333);
      }
      if (this.realitySeed.daily_expense_avg && this.realitySeed.daily_expense_avg > 0) {
        this.realitySeed.finances.monthly_expenses = Math.round(this.realitySeed.daily_expense_avg * 30.417);
      }
      this.realitySeed.months_to_graduation = 0;
    }

    // Identificación rigurosa de arquetipo (sin forzar estudiante a egresados o día a día)
    const careerLow = (this.realitySeed.career_or_degree || '').toLowerCase();
    const occLow = (this.realitySeed.occupation || '').toLowerCase();
    const isExplicitGrad = careerLow.includes('egresad') || careerLow.includes('bachiller') ||
                           careerLow.includes('titulad') || careerLow.includes('colegiad') ||
                           occLow.includes('egresad') || occLow.includes('titulad');
    const isDayWorker = this.realitySeed.life_profile_type === 'DAY_TO_DAY_WORKER' ||
                        occLow.includes('comida') || occLow.includes('ambulante') ||
                        occLow.includes('mototaxi') || occLow.includes('taxi');

    if (isExplicitGrad) {
      this.realitySeed.life_profile_type = 'TITLED_PROFESSIONAL';
      this.realitySeed.months_to_graduation = 0;
      if (!this.realitySeed.life_stage) {
        this.realitySeed.life_stage = 'ACTIVE_PROFESSIONAL';
      }
    } else if (isDayWorker) {
      this.realitySeed.life_profile_type = 'DAY_TO_DAY_WORKER';
      this.realitySeed.months_to_graduation = 0;
    } else if (
      this.realitySeed.life_profile_type === 'UNIVERSITY_OR_TECH_STUDENT' ||
      careerLow.includes('estudiant') || occLow.includes('estudiant') ||
      (careerLow.includes('ciclo') && !isExplicitGrad)
    ) {
      this.realitySeed.life_profile_type = 'UNIVERSITY_OR_TECH_STUDENT';
      if (!this.realitySeed.life_stage) {
        this.realitySeed.life_stage = 'WORKING_AND_FINISHING_UNI';
      }
    }

    if (this.realitySeed.one_year_goal || this.realitySeed.medium_term_goals || this.realitySeed.long_term_goals) {
      this.realitySeed.goal_mode = true;
      if (this.realitySeed.one_year_goal) {
        this.realitySeed.main_goal_1y = this.realitySeed.one_year_goal;
      }
    } else if (!this.realitySeed.goal_mode) {
      this.realitySeed.one_year_goal = '';
      this.realitySeed.main_goal_1y = '';
    } else if (this.realitySeed.one_year_goal) {
      this.realitySeed.main_goal_1y = this.realitySeed.one_year_goal;
    }



    this.api.predictFutureSelf(this.realitySeed).subscribe({

      next: (res) => {

        this.futureResponse.set(res);

        if (res.monte_carlo_output) {

          this.drJefService.setMonteCarloOutput(res.monte_carlo_output);

        }

        if (res.social_twin_impact) {

          this.drJefService.setSocialTwinResult(res.social_twin_impact);

        }

        this.isLoading.set(false);

        this.stopProgressAnimation();

      },

      error: (err) => {

        console.error('Error al predecir futuro yo:', err);

        this.isLoading.set(false);

        this.stopProgressAnimation();

      },

    });

  }



  downloadIcs(): void {

    this.isDownloadingIcs.set(true);

    this.api.downloadCalendarIcs(6.5, 2.5, 14).subscribe({

      next: (blob) => {

        this.api.triggerIcsDownload(blob, 'horario_rescate_mirror_future.ics');

        this.isDownloadingIcs.set(false);

      },

      error: (err) => {

        console.error('Error al descargar calendario .ics:', err);

        this.isDownloadingIcs.set(false);

      }

    });

  }



  onCountryChange(): void {
    this.updateCurrencyByCountry();
    if (this.futureResponse() && this.realitySeed.location.country) {

      this.predictFuture();

    }

  }



  getActiveHorizon(resp: HolisticFutureResponse): HorizonSnapshot {

    const k = this.selectedHorizonKey();

    if (k === '1_MONTH') return resp.horizons.one_month;

    if (k === '6_MONTHS') return resp.horizons.six_months;

    return resp.horizons.one_year;

  }



  toggleScientificLab(): void {

    this.showScientificLab.update((v) => !v);

  }



  loadPreset(type: 'day-to-day' | 'rural-farmer' | 'skilled-trade' | 'student-thesis' | 'titled-pro' | 'burnout-dev' | 'screen-time-trap' | 'mirror-optimal' | 'dr-jef-optimal'): void {

    if (type === 'day-to-day') {

      this.realitySeed.life_profile_type = 'DAY_TO_DAY_WORKER';

      this.realitySeed.goal_mode = false;

      this.realitySeed.person_identifier = '';

      this.realitySeed.full_name = '';

      this.realitySeed.occupation = 'Puesto de Abarrotes / Comercio Local';

      this.realitySeed.career_or_degree = 'Comercio Local';

      this.realitySeed.daily_income_avg = 70;

      this.realitySeed.work_days_per_week = 6;

      this.realitySeed.daily_expense_avg = 45;

      this.realitySeed.physical_labor_intensity = 'HIGH';

      this.realitySeed.housing_situation = 'FAMILY_HOME';

      this.realitySeed.dependents_count = 2;

      this.realitySeed.household_climate = 'SUPPORTIVE';

      this.realitySeed.relationship_status = 'SUPPORTIVE_PARTNER';

      this.realitySeed.social_circle_influence = 'GROWTH';

      this.realitySeed.open_family_and_dependents = this.drJefService.language() === 'EN'

        ? 'Living with my wife and two young children in family home; I cover most groceries and utility bills, good unity but constant worry over lacking fixed salary.'

        : 'Vivo con mi esposa y dos hijos pequeños en casa familiar; yo cubro casi toda la comida y servicios, hay unión pero nos preocupa no tener seguro ni sueldo fijo.';

      this.realitySeed.open_relationships_and_friends = this.drJefService.language() === 'EN'

        ? 'My spouse helps at the grocery stall when possible; market friends are hardworking and we support each other during slow days.'

        : 'Mi esposa me ayuda en el puesto cuando puede y nos apoyamos; mis amigos del mercado son trabajadores y nos damos la mano cuando bajan las ventas.';

      this.realitySeed.open_personality_and_habits = this.drJefService.language() === 'EN'

        ? 'Early riser and hardworking, but when daily sales drop I get stressed and find it hard to stop thinking about money.'

        : 'Soy muy madrugador y trabajador, pero cuando las ventas caen me pongo de mal humor y me cuesta desconectar la cabeza del dinero.';

      this.realitySeed.self_description = 'Trabajador perseverante, sostengo a mi familia con esfuerzo diario.';

      this.realitySeed.personality_traits = ['RESILIENT', 'DISCIPLINED'];

      this.realitySeed.one_year_goal = '';

      this.realitySeed.main_goal_1y = '';

      this.realitySeed.finances = {

        monthly_income: 0,
      monthly_expenses: 0,
      current_savings: 0,
      current_debt: 0,
      currency: 'PEN',

      };

      this.realitySeed.time_use = {

        sleep_hours: 6.5,

        work_hours: 9.0,

        study_project_hours: 0.5,

        screen_time_lost_hours: 1.5,

        exercise_hours: 0.5,

      };



    } else if (type === 'rural-farmer') {

      this.realitySeed.life_profile_type = 'RURAL_FIELD_PRODUCER';

      this.realitySeed.goal_mode = false;

      this.realitySeed.person_identifier = 'Saturnino Ramos';

      this.realitySeed.full_name = 'Saturnino Ramos';

      this.realitySeed.rural_product = 'Papa huayro y Hortalizas';

      this.realitySeed.occupation = 'Productor Agrícola';

      this.realitySeed.career_or_degree = 'Productor de Papa';

      this.realitySeed.campaign_income_est = 9500;

      this.realitySeed.physical_labor_intensity = 'HIGH';

      this.realitySeed.housing_situation = 'FAMILY_HOME';

      this.realitySeed.dependents_count = 3;

      this.realitySeed.household_climate = 'SUPPORTIVE';

      this.realitySeed.relationship_status = 'SUPPORTIVE_PARTNER';

      this.realitySeed.social_circle_influence = 'GROWTH';

      this.realitySeed.open_family_and_dependents = this.drJefService.language() === 'EN'

        ? 'Living on the farm with my wife and three children; two older kids help with crops, youngest goes to school; household livelihood depends on harvest results.'

        : 'Vivo en el campo con mi esposa y mis tres hijos; mis dos mayores ayudan en la chacra y el menor estudia; toda la familia depende del resultado de la cosecha.';

      this.realitySeed.open_relationships_and_friends = this.drJefService.language() === 'EN'

        ? 'Solid long-standing partnership based on joint farm labor; community relies on reciprocal work exchanges (ayni) for planting and irrigation.'

        : 'Relación de pareja sólida de muchos años basada en trabajo mutuo; en la comunidad nos organizamos por faenas colectivas (ayni) para sembrar y regar.';

      this.realitySeed.open_personality_and_habits = this.drJefService.language() === 'EN'

        ? 'Patient with nature and relentless worker; struggle to take rest days even when back pain demands physical recovery.'

        : 'Hombre de pocas palabras y mucha paciencia con el clima; me cuesta descansar incluso cuando el cuerpo pide pausa por dolor de espalda.';

      this.realitySeed.self_description = 'Productor del campo, acostumbrado a los ciclos de cosecha y trabajo duro.';

      this.realitySeed.personality_traits = ['RESILIENT'];

      this.realitySeed.one_year_goal = '';

      this.realitySeed.main_goal_1y = '';

      this.realitySeed.finances = {

        monthly_income: 1900,

        monthly_expenses: 1150,

        current_savings: 1200,

        current_debt: 1800,

        currency: 'USD',

      };

      this.realitySeed.time_use = {

        sleep_hours: 7.0,

        work_hours: 8.5,

        study_project_hours: 0.0,

        screen_time_lost_hours: 1.0,

        exercise_hours: 0.5,

      };



    } else if (type === 'skilled-trade') {

      this.realitySeed.life_profile_type = 'SKILLED_TRADE';

      this.realitySeed.goal_mode = false;

      this.realitySeed.person_identifier = 'Carlos Méndez';

      this.realitySeed.full_name = 'Carlos Méndez';

      this.realitySeed.career_or_degree = 'Mecánico Automotriz';

      this.realitySeed.occupation = 'Mecánico Automotriz';

      this.realitySeed.trade_modality = 'INDEPENDENT';

      this.realitySeed.physical_labor_intensity = 'HIGH';

      this.realitySeed.housing_situation = 'RENTING_INDEPENDENT';

      this.realitySeed.dependents_count = 1;

      this.realitySeed.household_climate = 'NEUTRAL';

      this.realitySeed.relationship_status = 'SINGLE_PEACEFUL';

      this.realitySeed.social_circle_influence = 'GROWTH';

      this.realitySeed.open_family_and_dependents = this.drJefService.language() === 'EN'

        ? 'Renting an independent room near the garage; sending monthly child support and helping my mother with medication costs.'

        : 'Alquilo un cuarto independiente cerca del taller; paso una pensión mensual a mi hijo y ayudo a mi madre con sus medicinas.';

      this.realitySeed.open_relationships_and_friends = this.drJefService.language() === 'EN'

        ? 'Single and focused on clearing tool debt; occasionally head out with fellow mechanics on weekends and spend more than planned.'

        : 'Soltero enfocado en pagar deudas y comprar herramientas; a veces los fines de semana salgo con amigos del rubro y se me va más dinero del que debería.';

      this.realitySeed.open_personality_and_habits = this.drJefService.language() === 'EN'

        ? 'Meticulous and honest with clients; under peak garage pressure or delayed parts, anxiety kicks in and I struggle to pace myself.'

        : 'Meticuloso y honesto con los clientes; cuando me lleno de autos y falta un repuesto me da ansiedad y fumo de más.';

      this.realitySeed.self_description = 'Técnico automotriz meticuloso, busco consolidar taller propio.';

      this.realitySeed.personality_traits = ['DISCIPLINED', 'RESILIENT'];

      this.realitySeed.one_year_goal = '';

      this.realitySeed.main_goal_1y = '';

      this.realitySeed.finances = {

        monthly_income: 2300,

        monthly_expenses: 1600,

        current_savings: 1000,

        current_debt: 700,

        currency: 'USD',

      };

      this.realitySeed.time_use = {

        sleep_hours: 6.5,

        work_hours: 8.5,

        study_project_hours: 0.5,

        screen_time_lost_hours: 1.5,

        exercise_hours: 0.5,

      };



    } else if (type === 'student-thesis' || type === 'burnout-dev') {

      this.realitySeed.life_profile_type = 'UNIVERSITY_OR_TECH_STUDENT';

      this.realitySeed.goal_mode = false;

      this.realitySeed.person_identifier = 'Egresado Continental';

      this.realitySeed.full_name = 'Egresado Continental';

      this.realitySeed.university_or_institution = 'Universidad Continental';

      this.realitySeed.current_company_or_org = 'Caja Huancayo (Prácticas)';

      this.realitySeed.occupation = 'Ingeniería de Sistemas';

      this.realitySeed.career_or_degree = 'Ingeniería de Sistemas';

      this.realitySeed.life_stage = 'WORKING_AND_FINISHING_UNI';

      this.realitySeed.months_to_graduation = 1;

      this.realitySeed.years_of_experience = 1.0;

      this.realitySeed.key_skills = 'Python, Angular, SQL, IA';

      this.realitySeed.english_level = 'B1_B2';

      this.realitySeed.work_modality_target = 'LOCAL_CITY';

      this.realitySeed.target_monthly_salary_1y = 4200;

      this.realitySeed.housing_situation = 'FAMILY_HOME';

      this.realitySeed.dependents_count = 0;

      this.realitySeed.household_climate = 'SUPPORTIVE';

      this.realitySeed.relationship_status = 'SINGLE_PEACEFUL';

      this.realitySeed.social_circle_influence = 'GROWTH';

      this.realitySeed.open_family_and_dependents = this.drJefService.language() === 'EN'

        ? 'Living with family; actively caring for my two younger brothers aged 9 and 3.'

        : 'De mi cuidado, mis dos hermanos uno de 9 y otro de 3 en casa familiar.';

      this.realitySeed.open_relationships_and_friends = this.drJefService.language() === 'EN'

        ? 'Single and focused on graduation; university peer group is ambitious and studious, though free time is scarce.'

        : 'Soltera y concentrada en terminar la carrera; mi círculo de la U es de chicos estudiosos pero todos andamos con poco tiempo para salir.';

      this.realitySeed.open_personality_and_habits = this.drJefService.language() === 'EN'

        ? 'High achiever with strong grit; prone to night-time overthinking and sacrificing sleep hours to fix code or thesis revisions.'

        : 'Soy muy responsable y autoexigente; tiendo al sobrepensamiento en las noches y a desvelarme frente a la pantalla programando o corrigiendo la tesis.';

      this.realitySeed.self_description = 'Estudiante en tramo final, ambiciosa pero con tendencia al sobrepensamiento.';

      this.realitySeed.personality_traits = ['PROCRASTINATOR', 'ANXIOUS_OVERTHINKER', 'AMBITIOUS'];

      this.realitySeed.one_year_goal = 'Sustentar tesis con honores, obtener grado y asegurar contrato indefinido';

      this.realitySeed.main_goal_1y = this.realitySeed.one_year_goal;

      this.realitySeed.finances = {

        monthly_income: 0,

        monthly_expenses: 0,

        current_savings: 0,

        current_debt: 0,

        currency: this.getCurrencyForCountry(this.realitySeed.location.country || 'Perú'),

      };

      this.realitySeed.time_use = {

        sleep_hours: 6.0,

        work_hours: 8.0,

        study_project_hours: 3.0,

        screen_time_lost_hours: 2.0,

        exercise_hours: 0.5,

      };



    } else if (type === 'titled-pro' || type === 'mirror-optimal' || type === 'dr-jef-optimal') {

      this.realitySeed.life_profile_type = 'TITLED_PROFESSIONAL';

      this.realitySeed.goal_mode = true;

      this.realitySeed.person_identifier = 'Elena Torres';

      this.realitySeed.full_name = 'Elena Torres';

      this.realitySeed.occupation = 'Contadora Pública Colegiada';

      this.realitySeed.career_or_degree = 'Contabilidad y Finanzas';

      this.realitySeed.contract_type = 'PERMANENT';

      this.realitySeed.years_of_experience = 4.0;

      this.realitySeed.key_skills = 'Auditoría Tributaria, NIIF, SAP ERP';

      this.realitySeed.english_level = 'B1_B2';

      this.realitySeed.work_modality_target = 'LOCAL_CITY';

      this.realitySeed.target_monthly_salary_1y = 5000;

      this.realitySeed.housing_situation = 'FAMILY_HOME';

      this.realitySeed.dependents_count = 1;

      this.realitySeed.household_climate = 'SUPPORTIVE';

      this.realitySeed.relationship_status = 'SUPPORTIVE_PARTNER';

      this.realitySeed.social_circle_influence = 'GROWTH';

      this.realitySeed.open_family_and_dependents = this.drJefService.language() === 'EN'

        ? 'Living with my partner and young child; sharing household expenses equally and coordinating childcare around work schedules.'

        : 'Vivo con mi pareja y nuestro hijo; compartimos los gastos equitativamente y nos apoyamos con el cuidado del niño mientras trabajamos.';

      this.realitySeed.open_relationships_and_friends = this.drJefService.language() === 'EN'

        ? 'Stable, communicative relationship; friend circle consists of fellow working professionals with balanced leisure habits.'

        : 'Relación de pareja comunicativa y estable; mis amistades son profesionales del mismo sector, hacemos reuniones tranquilas.';

      this.realitySeed.open_personality_and_habits = this.drJefService.language() === 'EN'

        ? 'Disciplined and methodic with numbers; main challenge is struggling to delegate and carrying work stress into weekends.'

        : 'Muy disciplinada y estructurada con números; mi talón de Aquiles es que me cuesta delegar y a veces me llevo trabajo mental al fin de semana.';

      this.realitySeed.self_description = 'Profesional organizada, equilibrando trabajo en planilla y crecimiento continuo.';

      this.realitySeed.personality_traits = ['DISCIPLINED', 'AMBITIOUS'];

      this.realitySeed.one_year_goal = 'Ascender a Jefatura Contable o consolidar cartera de clientes independientes';

      this.realitySeed.main_goal_1y = this.realitySeed.one_year_goal;

      this.realitySeed.finances = {

        monthly_income: 3500,

        monthly_expenses: 2200,

        current_savings: 5500,

        current_debt: 1200,

        currency: 'USD',

      };

      this.realitySeed.time_use = {

        sleep_hours: 7.0,

        work_hours: 8.0,

        study_project_hours: 1.5,

        screen_time_lost_hours: 1.5,

        exercise_hours: 1.0,

      };



    } else if (type === 'screen-time-trap') {

      this.realitySeed.life_profile_type = 'UNIVERSITY_OR_TECH_STUDENT';

      this.realitySeed.goal_mode = true;

      this.realitySeed.person_identifier = 'Mateo Ríos';

      this.realitySeed.full_name = 'Mateo Ríos';

      this.realitySeed.university_or_institution = 'Universidad Continental';

      this.realitySeed.occupation = 'Administración y Marketing';

      this.realitySeed.career_or_degree = 'Administración y Marketing';

      this.realitySeed.life_stage = 'STUDENT_MID_CAREER';

      this.realitySeed.months_to_graduation = 12;

      this.realitySeed.years_of_experience = 0.5;

      this.realitySeed.key_skills = 'Marketing Digital, Canva, Excel';

      this.realitySeed.english_level = 'A1_A2';

      this.realitySeed.work_modality_target = 'LOCAL_CITY';

      this.realitySeed.target_monthly_salary_1y = 3000;

      this.realitySeed.housing_situation = 'FAMILY_HOME';

      this.realitySeed.dependents_count = 0;

      this.realitySeed.household_climate = 'SUPPORTIVE';

      this.realitySeed.relationship_status = 'SINGLE_PEACEFUL';

      this.realitySeed.social_circle_influence = 'DRAINING_PARTY';

      this.realitySeed.open_family_and_dependents = this.drJefService.language() === 'EN'

        ? 'Living with parents who cover room and board; no dependents, but tension arises from excessive phone screen time.'

        : 'Vivo con mis padres y ellos cubren techo y comida; no tengo dependientes pero me reclaman que pase tanto tiempo en el celular.';

      this.realitySeed.open_relationships_and_friends = this.drJefService.language() === 'EN'

        ? 'Single with a nightlife-heavy friend group; easily tempted to overspend weekend budget on social outings.'

        : 'Soltero con un grupo de amigos muy fiesteros; salimos cada fin de semana y me dejo llevar fácil para gastar dinero de mis pasajes.';

      this.realitySeed.open_personality_and_habits = this.drJefService.language() === 'EN'

        ? 'Creative and enthusiastic at start, but heavily prone to scrolling procrastination and getting overwhelmed by backlogged deadlines.'

        : 'Creativo y entusiasta al inicio de proyectos, pero procrastino mucho en redes sociales y me paralizo cuando se acumulan entregas.';

      this.realitySeed.self_description = 'Tiendo a posponer metas por distracciones en pantalla y salidas.';

      this.realitySeed.personality_traits = ['PROCRASTINATOR', 'IMPULSIVE_SPENDER'];

      this.realitySeed.one_year_goal = 'Aprobar ciclos universitarios, conseguir prácticas bien remuneradas y ahorrar';

      this.realitySeed.main_goal_1y = this.realitySeed.one_year_goal;

      this.realitySeed.finances = {

        monthly_income: 1200,

        monthly_expenses: 900,

        current_savings: 1500,

        current_debt: 600,

        currency: 'USD',

      };

      this.realitySeed.time_use = {

        sleep_hours: 6.5,

        work_hours: 5.0,

        study_project_hours: 1.5,

        screen_time_lost_hours: 5.5,

        exercise_hours: 0.5,

      };

    }



    this.predictFuture();

  }



  getLiveWebSources(resp: HolisticFutureResponse): LiveWebSource[] {

    if (resp.live_web_sources && resp.live_web_sources.length > 0) {

      return resp.live_web_sources;

    }



    const city = this.realitySeed.location.city?.trim() || '';

    const country = resp.macro_context?.country || this.realitySeed.location.country || '';

    const countryCode = (resp.macro_context?.country_code || '').toLowerCase();

    const occupation = this.realitySeed.career_or_degree?.trim() || this.realitySeed.occupation?.trim() || '';

    const inflation = resp.macro_context?.annual_inflation_rate ?? 3.2;

    const personId = this.realitySeed.full_name?.trim() || this.realitySeed.person_identifier?.trim();



    const sources: LiveWebSource[] = [

      {

        category: 'Macroeconomía',

        title: `Banco Mundial: Inflación ${country} (${inflation}% anual)`,

        url: `https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG?locations=${countryCode}`,

      },

      {

        category: 'Mercado Laboral',

        title: `Mercado Laboral & Demanda Salarial para ${occupation} en ${city}`,

        url: `https://www.google.com/search?q=${encodeURIComponent('demanda laboral salarios ' + occupation + ' ' + city)}`,

      },

      {

        category: 'Costo de Vida',

        title: `Numbeo: Costo de vida e índice de poder adquisitivo en ${city}`,

        url: `https://www.numbeo.com/cost-of-living/in/${encodeURIComponent(city.replace(/\s+/g, '-'))}`,

      },

    ];



    if (personId) {

      sources.unshift({

        category: 'Perfil En Vivo',

        title: `Contexto profesional indexado: ${personId}`,

        url: personId.startsWith('http')

          ? personId

          : `https://www.google.com/search?q=${encodeURIComponent(personId + ' ' + occupation)}`,

      });

    }



    return sources;

  }



  toggleFamilySection(): void {

    this.isFamilySectionOpen.update((v) => !v);

  }



  togglePersonalitySection(): void {

    this.isPersonalitySectionOpen.update((v) => !v);

  }



  togglePersonalityTrait(trait: string): void {

    const traits = this.realitySeed.personality_traits || [];

    const idx = traits.indexOf(trait);

    if (idx >= 0) {

      traits.splice(idx, 1);

    } else {

      traits.push(trait);

    }

    this.realitySeed.personality_traits = [...traits];

  }



  isTraitSelected(trait: string): boolean {

    return (this.realitySeed.personality_traits || []).includes(trait);

  }



  toggleSpeechRecognition(field: 'open_family_and_dependents' | 'open_relationships_and_friends' | 'open_personality_and_habits'): void {

    if (typeof window === 'undefined') return;



    if (this.listeningField() === field) {

      if (this.speechRecognitionInstance) {

        try { this.speechRecognitionInstance.stop(); } catch (_) {}

      }

      this.listeningField.set(null);

      return;

    }



    if (this.speechRecognitionInstance) {

      try { this.speechRecognitionInstance.stop(); } catch (_) {}

    }



    const SpeechRec = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;

    if (!SpeechRec) {

      alert(this.drJefService.language() === 'EN'

        ? 'Speech recognition is not supported in this browser. Please use Google Chrome or Microsoft Edge.'

        : 'El dictado por voz no es compatible con este navegador. Por favor usa Google Chrome o Microsoft Edge.');

      return;

    }



    try {

      const recognition = new SpeechRec();

      recognition.continuous = true;

      recognition.interimResults = false;

      recognition.lang = this.drJefService.language() === 'EN' ? 'en-US' : 'es-PE';



      recognition.onstart = () => {

        this.listeningField.set(field);

      };



      recognition.onresult = (event: any) => {

        const results = event.results;

        if (!results || results.length === 0) return;

        const lastResult = results[results.length - 1];

        if (lastResult && lastResult[0]) {

          const transcript = lastResult[0].transcript.trim();

          const currentVal = (this.realitySeed as any)[field] || '';

          (this.realitySeed as any)[field] = currentVal ? `${currentVal} ${transcript}` : transcript;

        }

      };



      recognition.onerror = (err: any) => {
        if (err && (err.error === 'no-speech' || err.error === 'aborted')) {
          return;
        }
        console.warn('Speech recognition warning:', err);
        if (err && err.error === 'not-allowed') {
          this.listeningField.set(null);
        }
      };

      recognition.onend = () => {
        if (this.listeningField() === field) {
          setTimeout(() => {
            if (this.listeningField() === field) {
              try { recognition.start(); } catch (_) {}
            }
          }, 350);
        }
      };



      this.speechRecognitionInstance = recognition;

      recognition.start();

    } catch (e) {

      console.error('Failed to start speech recognition:', e);

      this.listeningField.set(null);

    }

  }



  generateDynamicQuestions(): void {

    this.isGeneratingQuestions.set(true);

    const req: DiscoveryQuestionsRequest = {

      age: this.realitySeed.age,

      occupation: this.realitySeed.occupation || this.realitySeed.career_or_degree || 'General',

      city: this.realitySeed.location.city,

      lang: this.drJefService.language() as 'EN' | 'ES',

      life_profile_type: this.realitySeed.life_profile_type

    };



    this.api.generateDiscoveryQuestions(req).subscribe({

      next: (res) => {

        this.isGeneratingQuestions.set(false);

        if (res && res.questions && res.questions.length > 0) {

          this.discoveryQuestions.set(res.questions);

        }

      },

      error: (err) => {

        this.isGeneratingQuestions.set(false);

        console.warn('Discovery questions fallback:', err);

        if (this.drJefService.language() === 'EN') {

          this.discoveryQuestions.set([

            `At home in ${this.realitySeed.location.city}, who relies on your financial support or daily care?`,

            'Do your partner and closest friends encourage your progress or pull you into draining expenses?',

            `As a ${this.realitySeed.occupation || 'worker'}, when fatigue and money stress collide, what habit trips you up?`

          ]);

        } else {

          this.discoveryQuestions.set([

            `¿En tu casa en ${this.realitySeed.location.city}, quiénes dependen de tu dinero o de tus cuidados en el día a día?`,

            '¿Tu pareja o tus amistades te impulsan a superarte o te jalan a gastar tiempo y dinero en distracciones?',

            `Como ${this.realitySeed.occupation || 'trabajador'}, cuando se junta el cansancio y la presión de dinero, ¿cuál es tu primera reacción o hábito que te sabotea?`

          ]);

        }

      }

    });

  }



  insertDiscoveryQuestion(q: string): void {

    if (!this.realitySeed.open_family_and_dependents) {

      this.realitySeed.open_family_and_dependents = `${q}\n- `;

    } else if (!this.realitySeed.open_relationships_and_friends) {

      this.realitySeed.open_relationships_and_friends = `${q}\n- `;

    } else if (!this.realitySeed.open_personality_and_habits) {

      this.realitySeed.open_personality_and_habits = `${q}\n- `;

    } else {

      this.realitySeed.open_personality_and_habits += `\n${q}\n- `;

    }

  }



  onFileAutofill(event: Event): void {

    const input = event.target as HTMLInputElement;

    if (!input.files || input.files.length === 0) return;

    const file = input.files[0];

    this.uploadedFileName.set(file.name);



    if (file.name.toLowerCase().endsWith('.ics')) {

      this.api.ingestCalendarIcs(file).subscribe({

        next: (res) => {

          const days = Math.max(1, res.busy_metrics.days_count || 7);

          this.realitySeed.time_use.work_hours = Number((res.busy_metrics.work_hours_total / days).toFixed(1)) || 8.0;

          this.realitySeed.time_use.study_project_hours = Number((res.busy_metrics.thesis_hours_total / days).toFixed(1)) || 2.0;

          this.predictFuture();

        },

        error: () => this.predictFuture()

      });

    } else {

      this.api.ingestWhatsApp(file).subscribe({

        next: (res) => {

          if (res && res.contact_record) {

            const rec = res.contact_record;

            const msgCount = rec.total_messages_analyzed || 0;

            this.realitySeed.chat_median_reply_min = rec.real_median_reply_minutes || null;

            this.realitySeed.chat_extracted_summary =

              rec.extracted_psych_summary ||

              `Chat con ${rec.contact_name} (${rec.relationship_type}), ${msgCount} mensajes, tono ${rec.real_lexical_profile?.tone || 'mixto'}`;



            // Deducción analítica de sentimiento y tag dominante de comunicación

            const tone = (rec.real_lexical_profile?.tone || '').toLowerCase();

            const psych = (rec.extracted_psych_summary || '').toLowerCase();

            if (psych.includes('tensión') || psych.includes('conflicto') || psych.includes('distanciamiento')) {

              this.realitySeed.chat_dominant_tag = 'conflict';

              this.realitySeed.chat_sentiment_avg = -0.35;

            } else if (psych.includes('afecto') || psych.includes('amor') || psych.includes('cariño') || tone.includes('empático')) {

              this.realitySeed.chat_dominant_tag = 'affection';

              this.realitySeed.chat_sentiment_avg = 0.45;

            } else if (psych.includes('tesis') || psych.includes('académico') || psych.includes('presión')) {

              this.realitySeed.chat_dominant_tag = 'thesis_pressure';

              this.realitySeed.chat_sentiment_avg = -0.10;

            } else {

              this.realitySeed.chat_dominant_tag = 'support';

              this.realitySeed.chat_sentiment_avg = 0.25;

            }



            const badgeText = this.drJefService.language() === 'EN'

              ? `💬 Chat analyzed & linked to your emotional projection (${msgCount} real messages)`

              : `💬 Chat analizado e integrado a tu proyección emocional (${msgCount} mensajes reales)`;

            this.chatAnalysisBadge.set(badgeText);

          }

          this.predictFuture();

        },

        error: () => this.predictFuture()

      });

    }

  }



  onPhotoUpload(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (!input.files || input.files.length === 0) return;
    const file = input.files[0];
    if (!file.type.startsWith('image/')) return;

    const reader = new FileReader();
    reader.onload = () => {
      const dataUrl = reader.result as string;
      this.validationError.set(null);
      this.userPhotoPreview.set(dataUrl);
      this.realitySeed.user_photo_base64 = dataUrl;
      this.showOriginalPhoto.set(false);

      if (this.activeInputMode() === 'INTERVIEW') {
        const msg = this.drJefService.language() === 'ES'
          ? '📸 ¡Foto de referencia vinculada exitosamente! El motor biométrico y causal utilizará tus rasgos faciales para proyectar tu propio rostro en la imagen y video del futuro.'
          : '📸 Reference photo linked successfully! The biometric and causal engine will use your facial features to project your own face in future images and video.';
        this.interviewHistory.set([...this.interviewHistory(), { role: 'assistant', content: msg }]);
      }

      if (this.futureResponse()) {
        this.predictFuture();
      }
    };
    reader.readAsDataURL(file);
  }

  removeUserPhoto(): void {
    this.userPhotoPreview.set(null);
    this.showOriginalPhoto.set(false);
    delete this.realitySeed.user_photo_base64;
    if (this.futureResponse()) {
      this.predictFuture();
    }
  }

  setVisualMirrorMode(mode: 'CURRENT' | 'OPTIMAL'): void {
    this.visualMirrorMode.set(mode);
    if (this.isCinematicVoicePlaying()) {
      this.stopCinematicSimulation();
    }
  }

  selectHorizon(key: '1_MONTH' | '6_MONTHS' | '1_YEAR'): void {
    this.selectedHorizonKey.set(key);
    this.stopCinematicSimulation();
  }

  selectRoadmapPhase(idx: number): void {
    this.selectedRoadmapPhaseIndex.set(idx);
  }

  getVideoUrl(horizon: HorizonSnapshot): string {
    const k = this.selectedHorizonKey();
    const mode = this.visualMirrorMode();
    const cleanK = k === '1_MONTH' ? '1_month' : (k === '6_MONTHS' ? '6_months' : '1_year');
    return `http://localhost:8000/api/causal/future-video?horizon=${cleanK}&mode=${mode}`;
  }

  getVideoDownloadUrl(horizon: HorizonSnapshot): string {
    const k = this.selectedHorizonKey();
    const mode = this.visualMirrorMode();
    const cleanK = k === '1_MONTH' ? '1_month' : (k === '6_MONTHS' ? '6_months' : '1_year');
    return `http://localhost:8000/api/causal/future-video?horizon=${cleanK}&mode=${mode}&download=1`;
  }

  getMirrorImageUrl(horizon: HorizonSnapshot): string {
    // Si el usuario eligió ver su foto original de referencia
    if (this.showOriginalPhoto()) {
      return this.userPhotoPreview() || horizon.reference_photo_url || '';
    }

    // Modo Camino Óptimo Golden Path
    const isOptimal = this.visualMirrorMode() === 'OPTIMAL';
    if (isOptimal && horizon.optimal_comparison_image_url) {
      return horizon.optimal_comparison_image_url;
    }

    // Retrato del Futuro Yo generado / proyectado
    if (horizon.future_self_image_url) {
      return horizon.future_self_image_url;
    }

    // Respaldo de foto de referencia o placeholder
    return this.userPhotoPreview() || horizon.reference_photo_url || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=1200&q=80';
  }

  getMirrorCaption(horizon: HorizonSnapshot): string {

    const isEn = this.drJefService.language() === 'EN';

    const isOptimal = this.visualMirrorMode() === 'OPTIMAL';

    if (isOptimal) {

      if (isEn) {

        return `✨ Mirror Future Golden Path: Protected circadian rhythm with 7.5h sleep, active amortizing finances, and clear focus on "${this.realitySeed.one_year_goal || 'your primary goal'}".`;

      }

      return `✨ Camino Óptimo Mirror Future: Ritmo circadiano protegido con 7.5h de sueño, finanzas con amortización activa y foco limpio en "${this.realitySeed.one_year_goal || 'tu meta central'}".`;

    }

    if (horizon.visual_scene_caption) {

      return horizon.visual_scene_caption;

    }

    const city = this.realitySeed.location.city || (isEn ? 'your city' : 'tu ciudad');

    if (isEn) {

      return `Current inertia in ${city}: Projected biological fatigue of ${(horizon.burnout_risk * 100).toFixed(0)}% due to sleep deficit and macroeconomic friction.`;

    }

    return `Inercia actual en ${city}: Fatiga biológica proyectada del ${(horizon.burnout_risk * 100).toFixed(0)}% por déficit de descanso y fricción macroeconómica.`;

  }



  getMirrorVoiceScript(horizon: HorizonSnapshot): string {

    const isEn = this.drJefService.language() === 'EN';

    const isOptimal = this.visualMirrorMode() === 'OPTIMAL';

    const city = this.realitySeed.location.city || (isEn ? 'your city' : 'tu ciudad');

    const k = this.selectedHorizonKey();



    if (isOptimal) {

      if (k === '1_MONTH') {

        return isEn

          ? `Hello! I am your future self in 30 days here in ${city}. By safeguarding our 7.5 hours of sleep and reducing digital distractions, mental clarity returned right away. The journey has just started, but we already feel full control over our daily routine.`

          : `¡Hola! Soy tu futuro yo en 30 días aquí en ${city}. Al proteger nuestras 7.5 horas de sueño y acotar las distracciones digitales, la claridad mental regresó de inmediato. El camino apenas comienza, pero ya sentimos el control total de nuestra rutina.`;

      }

      if (k === '6_MONTHS') {

        return isEn

          ? `Look at me closely. 180 days have passed, and we achieved balance we previously thought impossible. Finances are organized, we are saving steadily, and progress toward our goal is above 70%. This is the version of life we deserve.`

          : `Mírame bien. Han pasado 180 días y logramos un balance que creíamos imposible. Las finanzas están ordenadas, ahorramos con constancia y el avance hacia nuestra meta superó el 70%. Esta es la versión que merecemos vivir.`;

      }

      return isEn

        ? `Let us celebrate! I am your future self at one full year. We met and exceeded our goal, reached our financial cushion, and our biological vitality is at its absolute peak. Every single micro-decision you made today built this exact reality.`

        : `¡Celebremos! Soy tu futuro yo a un año completo. Cumplimos con creces nuestro objetivo, alcanzamos el colchón financiero y nuestra vitalidad está en su punto más alto. Cada micro-decisión de rescate que tomaste hoy construyó exactamente este momento.`;

    } else {

      if (horizon.first_person_voice_script) {

        return horizon.first_person_voice_script;

      }

      if (k === '1_MONTH') {

        return isEn

          ? `Hey... this is you in 30 days. I can already feel how short nights of sleep and rising stress are taking a toll here in ${city}. If we keep spending out of exhaustion and sleeping so little, the goal will drift further away.`

          : `Hola... soy tú en 30 días. Siento cómo las noches cortas de descanso y el estrés empiezan a acumularse aquí en ${city}. Si seguimos gastando por fatiga y durmiendo tan poco, la meta se alejará cada vez más.`;

      }

      if (k === '6_MONTHS') {

        return isEn

          ? `Listen to me... 180 days have gone by. Chronic exhaustion is taking its toll on our work and our relationships. Our burnout overload risk reached ${(horizon.burnout_risk * 100).toFixed(0)}%. We urgently need to stop losing hours today.`

          : `Escúchame... han pasado 180 días. El cansancio crónico ya nos está pasando factura en el trabajo y con nuestros vínculos. El riesgo de sobrecarga llegó al ${(horizon.burnout_risk * 100).toFixed(0)}%. Necesitamos frenar la fuga de horas hoy mismo.`;

      }

      return isEn

        ? `I am your self exactly 365 days into the future. We reached year end drained, with finances stagnated and the feeling of merely surviving rather than thriving. You are still in time inside the oracle to change this outcome.`

        : `Soy tu yo exactamente dentro de 365 días. Llegamos al final del año agotados, con el patrimonio estancado y la sensación de haber sobrevivido en lugar de crecer. Aún estás a tiempo en el oráculo de cambiar este desenlace.`;

    }

  }



  playCinematicSimulation(horizon: HorizonSnapshot): void {

    if (typeof window === 'undefined') return;



    this.stopCinematicSimulation();

    const isEn = this.drJefService.language() === 'EN';

    const script = this.getMirrorVoiceScript(horizon);



    if ('speechSynthesis' in window) {

      window.speechSynthesis.cancel();



      const utterance = new SpeechSynthesisUtterance(script);

      utterance.lang = isEn ? 'en-US' : 'es-ES';

      utterance.rate = 0.94;

      utterance.pitch = 1.0;



      const voices = window.speechSynthesis.getVoices();

      const matchedVoice = voices.find((v) =>

        isEn

          ? v.lang.startsWith('en') || v.lang.includes('English')

          : v.lang.startsWith('es') || v.lang.includes('Spanish')

      );

      if (matchedVoice) {

        utterance.voice = matchedVoice;

      }



      utterance.onstart = () => {
        this.isCinematicVoicePlaying.set(true);
        this.isVideoModeActive.set(true);
      };

      utterance.onend = () => {
        this.isCinematicVoicePlaying.set(false);
        this.isVideoModeActive.set(false);
      };

      utterance.onerror = () => {
        this.isCinematicVoicePlaying.set(false);
        this.isVideoModeActive.set(false);
      };

      window.speechSynthesis.speak(utterance);
      this.isCinematicVoicePlaying.set(true);
      this.isVideoModeActive.set(true);
    } else {
      this.isCinematicVoicePlaying.set(true);
      this.isVideoModeActive.set(true);
      setTimeout(() => {
        this.isCinematicVoicePlaying.set(false);
        this.isVideoModeActive.set(false);
      }, 9000);
    }
  }

  stopCinematicSimulation(): void {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    this.isCinematicVoicePlaying.set(false);
    this.isVideoModeActive.set(false);
  }


  // ==========================================
  // Métodos del Motor Conversacional & Dossier
  // ==========================================

  initInterviewConversation(): void {
    const isEs = this.drJefService.language() === 'ES';
    const initialGreeting = isEs
      ? '¡Hola! Soy tu Oráculo Causal y Motor Laboral Life2Vec Mirror Future. Para reconstruir tu historia y autocompletar tu futuro laboral e ingresos (1 Mes, 6 Meses, 1 Año, 3 Años y 5 Años) con precisión empírica:\n\n1. ¿Cómo te llamas, cuántos años tienes y en qué ciudad vives?\n2. ¿Qué has hecho en los últimos años (estudios cursados, primeros trabajos o proyectos previos)?\n3. ¿Cuál es tu situación laboral e ingresos hoy, y a qué puesto o metas salariales aspiras en 1, 3 y 5 años?'
      : 'Hello! I am your Mirror Future Causal Oracle & Life2Vec Career Engine. To reconstruct your trajectory and autocomplete your career and income (1 Month, 6 Months, 1 Year, 3 Years, 5 Years) with empirical precision:\n\n1. What is your name, age, and city of residence?\n2. What have you accomplished over past years (studies, prior jobs, ventures, skills)?\n3. What is your role and income today, and what career goals do you target across 1, 3, and 5 years?';
    this.interviewHistory.set([
      { role: 'assistant', content: initialGreeting }
    ]);
    this.interviewCompletenessPct.set(15);
    this.interviewPillarsCovered.set({ identity: false, goals: false, economy: false, routine: false, family: false, personality: false });
  }

  sendInterviewMessage(): void {
    this.stopInterviewVoice();
    this.validationError.set(null);
    const text = (this.interviewInputText() || '').trim();
    if (!text || this.isInterviewThinking()) return;

    const updatedHistory: DiscoveryInterviewMessage[] = [...this.interviewHistory(), { role: 'user', content: text }];
    this.interviewHistory.set(updatedHistory);
    this.interviewInputText.set('');
    this.isInterviewThinking.set(true);

    // Sincronización heurística inmediata en tiempo real del mensaje del usuario
    this.syncChatHistoryToRealitySeed();

    const payload: DiscoveryInterviewRequest = {
      conversation_history: updatedHistory,
      lang: this.drJefService.language(),
    };

    this.api.discoveryInterview(payload).subscribe({
      next: (res) => {
        this.isInterviewThinking.set(false);
        this.interviewCompletenessPct.set(res.completeness_pct);
        if (res.pillars_covered) {
          this.interviewPillarsCovered.set(res.pillars_covered);
        }

        // Live bidirectional synchronization on EVERY turn:
        if (res.extracted_parameters) {
          this.applyExtractedParameters(res.extracted_parameters);
        }
        if (res.full_person_dossier_text) {
          this.fullPersonDossierText.set(res.full_person_dossier_text);
        }

        if (res.is_complete && res.full_person_dossier_text) {
          this.dossierGenerated.set(true);
          const completionMsg = this.drJefService.language() === 'ES'
            ? '¡Excelente! He sintetizado tu realidad en un Texto Completo. Puedes leerlo y afinarlo aquí mismo antes de predecir tu futuro.'
            : 'Excellent! I have synthesized your reality into a Full Dossier. You can review and refine it right here before predicting your future.';
          this.interviewHistory.set([...this.interviewHistory(), { role: 'assistant', content: completionMsg }]);
        } else if (res.next_question) {
          this.interviewHistory.set([...this.interviewHistory(), { role: 'assistant', content: res.next_question }]);
        }
      },
      error: (err) => {
        console.error('Error en entrevista de descubrimiento:', err);
        this.isInterviewThinking.set(false);
      }
    });
  }

  forceCompleteInterview(): void {
    this.stopInterviewVoice();
    if (this.isInterviewThinking()) return;
    this.isInterviewThinking.set(true);

    const payload: DiscoveryInterviewRequest = {
      conversation_history: this.interviewHistory(),
      lang: this.drJefService.language(),
      force_generate: true,
    };

    this.api.discoveryInterview(payload).subscribe({
      next: (res) => {
        this.isInterviewThinking.set(false);
        this.interviewCompletenessPct.set(100);
        if (res.full_person_dossier_text) {
          this.fullPersonDossierText.set(res.full_person_dossier_text);
        }
        this.dossierGenerated.set(true);
        if (res.extracted_parameters) {
          this.applyExtractedParameters(res.extracted_parameters);
        }
      },
      error: (err) => {
        console.error('Error al forzar generación de dossier:', err);
        this.isInterviewThinking.set(false);
      }
    });
  }

  onDossierEdited(newText: string): void {
    this.fullPersonDossierText.set(newText);
    if (this.syncDebounceTimer) {
      clearTimeout(this.syncDebounceTimer);
    }
    this.syncDebounceTimer = setTimeout(() => {
      this.syncDossier();
    }, 1200);
  }

  syncDossier(): void {
    const text = this.fullPersonDossierText().trim();
    if (!text) return;
    this.isSyncingDossier.set(true);
    this.api.syncDossierToParameters({
      dossier_text: text,
      current_parameters: this.realitySeed as any,
      lang: this.drJefService.language()
    }).subscribe({
      next: (res) => {
        this.isSyncingDossier.set(false);
        if (res.extracted_parameters) {
          this.applyExtractedParameters(res.extracted_parameters);
        }
      },
      error: (err) => {
        console.error('Error al sincronizar dossier:', err);
        this.isSyncingDossier.set(false);
      }
    });
  }

  applyExtractedParameters(params: Record<string, any>): void {
    if (!params) return;
    if (params['full_name']) {
      this.realitySeed.full_name = params['full_name'];
      this.realitySeed.person_identifier = params['full_name'];
    }
    if (params['city']) this.realitySeed.location.city = params['city'];
    if (params['country_code']) {
      this.realitySeed.location.country = params['country_code'] === 'PE' ? 'Perú' : params['country_code'];
    }
    if (params['currency']) this.realitySeed.finances.currency = params['currency'];
    if (params['monthly_income'] !== undefined) this.realitySeed.finances.monthly_income = Number(params['monthly_income']) || 0;
    if (params['monthly_expenses'] !== undefined) this.realitySeed.finances.monthly_expenses = Number(params['monthly_expenses']) || 0;
    if (params['current_savings'] !== undefined) this.realitySeed.finances.current_savings = Number(params['current_savings']) || 0;
    if (params['current_debt'] !== undefined) this.realitySeed.finances.current_debt = Number(params['current_debt']) || 0;
    if (params['age'] && Number(params['age']) > 0) this.realitySeed.age = Number(params['age']);
    if (params['occupation']) this.realitySeed.occupation = params['occupation'];
    if (params['career_or_degree']) this.realitySeed.career_or_degree = params['career_or_degree'];
    if (!this.realitySeed.occupation && params['career_or_degree']) this.realitySeed.occupation = params['career_or_degree'];
    if (params['university_or_institution']) this.realitySeed.university_or_institution = params['university_or_institution'];
    if (params['life_stage']) this.realitySeed.life_stage = params['life_stage'];
    if (params['months_to_graduation'] !== undefined) this.realitySeed.months_to_graduation = Number(params['months_to_graduation']) || 0;

    // Detección rigurosa de arquetipo sincronizado
    const careerText = (params['career_or_degree'] || this.realitySeed.career_or_degree || '').toLowerCase();
    const occText = (params['occupation'] || this.realitySeed.occupation || '').toLowerCase();
    const lStage = (params['life_stage'] || this.realitySeed.life_stage || '').toUpperCase();
    const pType = (params['life_profile_type'] || this.realitySeed.life_profile_type || '').toUpperCase();

    const isTaxi = occText.includes('taxi') || occText.includes('mototaxi') || occText.includes('chofer') || occText.includes('conductor') || careerText.includes('taxi') || careerText.includes('transporte');
    const isRural = occText.includes('granja') || occText.includes('avícol') || occText.includes('avicol') || occText.includes('porcin') || occText.includes('cuy') || occText.includes('galpón') || occText.includes('galpon') || occText.includes('campo') || occText.includes('chacra') || careerText.includes('granja') || careerText.includes('agro') || pType === 'RURAL_FIELD_PRODUCER';
    const isBusiness = !isTaxi && (occText.includes('comerciante') || occText.includes('tienda') || occText.includes('bodega') || occText.includes('abarrotes') || occText.includes('negocio') || occText.includes('emprend') || careerText.includes('comercio') || pType === 'BUSINESS_OWNER');
    const isGrad = careerText.includes('egresad') || careerText.includes('bachiller') ||
                   careerText.includes('titulad') || careerText.includes('colegiad') ||
                   occText.includes('egresad') || occText.includes('titulad') ||
                   pType === 'TITLED_PROFESSIONAL';
    const isDay = pType === 'DAY_TO_DAY_WORKER' || occText.includes('comida') || occText.includes('ambulante') || isTaxi;

    if (isTaxi) {
      this.realitySeed.life_profile_type = 'DAY_TO_DAY_WORKER';
      this.realitySeed.career_or_degree = 'Transporte & Conducción (Taxi)';
      if (!this.realitySeed.occupation) this.realitySeed.occupation = 'Taxista / Conductor Urbano';
      this.realitySeed.months_to_graduation = 0;
    } else if (isRural) {
      this.realitySeed.life_profile_type = 'RURAL_FIELD_PRODUCER';
      this.realitySeed.career_or_degree = 'Producción Agropecuaria y Granjas';
      if (!this.realitySeed.occupation) this.realitySeed.occupation = 'Productor Agropecuario / Granjas';
      this.realitySeed.months_to_graduation = 0;
    } else if (isBusiness) {
      this.realitySeed.life_profile_type = 'BUSINESS_OWNER';
      this.realitySeed.career_or_degree = 'Comercio & Gestión de Negocio';
      if (!this.realitySeed.occupation) this.realitySeed.occupation = 'Dueño de Negocio / Comerciante';
      this.realitySeed.months_to_graduation = 0;
    } else if (isGrad) {
      this.realitySeed.life_profile_type = 'TITLED_PROFESSIONAL';
      this.realitySeed.months_to_graduation = 0;
      if (!this.realitySeed.life_stage) {
        this.realitySeed.life_stage = 'ACTIVE_PROFESSIONAL';
      }
    } else if (isDay && !careerText.includes('estudiant')) {
      this.realitySeed.life_profile_type = 'DAY_TO_DAY_WORKER';
      this.realitySeed.months_to_graduation = 0;
    } else if (
      pType === 'UNIVERSITY_OR_TECH_STUDENT' ||
      careerText.includes('estudiant') || occText.includes('estudiant') ||
      (careerText.includes('ciclo') && !isGrad) ||
      lStage.includes('UNI') || lStage.includes('STUD')
    ) {
      this.realitySeed.life_profile_type = 'UNIVERSITY_OR_TECH_STUDENT';
      if (!this.realitySeed.life_stage) {
        this.realitySeed.life_stage = 'WORKING_AND_FINISHING_UNI';
      }
    } else if (params['life_profile_type']) {
      this.realitySeed.life_profile_type = params['life_profile_type'];
    }

    if (params['dependents_count'] !== undefined) this.realitySeed.dependents_count = Number(params['dependents_count']) || 0;
    if (params['sleep_hours'] !== undefined) this.realitySeed.time_use.sleep_hours = Number(params['sleep_hours']);
    if (params['work_hours'] !== undefined) this.realitySeed.time_use.work_hours = Number(params['work_hours']);
    if (params['study_or_project_hours'] !== undefined) this.realitySeed.time_use.study_project_hours = Number(params['study_or_project_hours']);
    if (params['screen_time_distraction_hours'] !== undefined) this.realitySeed.time_use.screen_time_lost_hours = Number(params['screen_time_distraction_hours']);
    if (params['exercise_hours'] !== undefined) this.realitySeed.time_use.exercise_hours = Number(params['exercise_hours']);
    if (params['personality_traits'] && Array.isArray(params['personality_traits'])) {
      this.realitySeed.personality_traits = params['personality_traits'];
    }
    if (params['open_family_and_dependents'] !== undefined) this.realitySeed.open_family_and_dependents = params['open_family_and_dependents'];
    if (params['open_relationships_and_friends'] !== undefined) this.realitySeed.open_relationships_and_friends = params['open_relationships_and_friends'];
    if (params['open_personality_and_habits'] !== undefined) this.realitySeed.open_personality_and_habits = params['open_personality_and_habits'];

    // Multi-horizon goals:
    if (params['main_goal_1y']) {
      this.realitySeed.main_goal_1y = params['main_goal_1y'];
      this.realitySeed.one_year_goal = params['main_goal_1y'];
      this.realitySeed.goal_mode = true;
    }
    if (params['one_year_goal']) {
      this.realitySeed.one_year_goal = params['one_year_goal'];
      this.realitySeed.main_goal_1y = params['one_year_goal'];
      this.realitySeed.goal_mode = true;
    }
    if (params['medium_term_goals'] !== undefined) {
      this.realitySeed.medium_term_goals = params['medium_term_goals'];
      if (params['medium_term_goals']) this.realitySeed.goal_mode = true;
    }
    if (params['long_term_goals'] !== undefined) {
      this.realitySeed.long_term_goals = params['long_term_goals'];
      if (params['long_term_goals']) this.realitySeed.goal_mode = true;
    }
    if (params['target_monthly_salary_1y'] !== undefined) {
      this.realitySeed.target_monthly_salary_1y = Number(params['target_monthly_salary_1y']) || 0;
    }
    this.updateCurrencyByCountry();
  }

  toggleInterviewVoice(): void {
    if (this.isInterviewListening()) {
      this.stopInterviewVoice();
    } else {
      this.startInterviewVoice();
    }
  }

  startInterviewVoice(): void {
    if (typeof window === 'undefined') return;
    const SpeechRec = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRec) {
      alert(this.drJefService.language() === 'EN'
        ? 'Voice recognition is not supported in this browser. Please use Google Chrome or Microsoft Edge.'
        : 'El reconocimiento de voz no está disponible en este navegador. Te recomendamos usar Google Chrome o Microsoft Edge.');
      return;
    }
    this.userManuallyStoppedVoice = false;
    this.voiceBaseText = (this.interviewInputText() || '').trim();
    this.voiceAccumulatedFinal = '';
    this.isInterviewListening.set(true);
    this.startInterviewVoiceSession();
  }

  private startInterviewVoiceSession(): void {
    if (this.userManuallyStoppedVoice || !this.isInterviewListening()) return;
    const SpeechRec = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRec) return;

    if (this.voiceAccumulatedFinal) {
      this.voiceBaseText = (this.voiceBaseText ? `${this.voiceBaseText} ${this.voiceAccumulatedFinal}` : this.voiceAccumulatedFinal).trim();
      this.voiceAccumulatedFinal = '';
    }

    if (this.speechRecognitionInstance) {
      try {
        this.speechRecognitionInstance.onend = null;
        this.speechRecognitionInstance.onerror = null;
        this.speechRecognitionInstance.stop();
      } catch (_) {}
      this.speechRecognitionInstance = null;
    }

    try {
      const recognition = new SpeechRec();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = this.drJefService.language() === 'ES' ? 'es-PE' : 'en-US';
      recognition.maxAlternatives = 1;

      recognition.onstart = () => {
        this.isInterviewListening.set(true);
      };

      recognition.onresult = (event: any) => {
        let interim = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          const res = event.results[i];
          const transcript = res[0] ? res[0].transcript : '';
          if (res.isFinal) {
            this.voiceAccumulatedFinal = (this.voiceAccumulatedFinal + ' ' + transcript).trim();
          } else {
            interim += transcript;
          }
        }
        const parts = [this.voiceBaseText, this.voiceAccumulatedFinal, interim.trim()].filter(p => !!p && p.trim().length > 0);
        this.interviewInputText.set(parts.join(' ').replace(/\s+/g, ' ').trim());
      };

      recognition.onerror = (event: any) => {
        if (event.error === 'no-speech' || event.error === 'aborted') {
          return;
        }
        console.warn('Speech recognition status:', event.error);
        if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
          alert(this.drJefService.language() === 'EN'
            ? 'Microphone permission denied. Please allow microphone permissions in your browser.'
            : 'Permiso de micrófono denegado. Por favor permite el acceso en la configuración de tu navegador.');
          this.stopInterviewVoice();
        }
      };

      recognition.onend = () => {
        if (!this.userManuallyStoppedVoice && this.isInterviewListening()) {
          if (this.voiceRestartTimeout) clearTimeout(this.voiceRestartTimeout);
          this.voiceRestartTimeout = setTimeout(() => {
            if (!this.userManuallyStoppedVoice && this.isInterviewListening()) {
              this.startInterviewVoiceSession();
            }
          }, 350);
        } else {
          this.isInterviewListening.set(false);
        }
      };

      this.speechRecognitionInstance = recognition;
      recognition.start();
    } catch (err: any) {
      console.warn('Speech recognition temporary start notice, scheduling retry:', err);
      if (!this.userManuallyStoppedVoice && this.isInterviewListening()) {
        if (this.voiceRestartTimeout) clearTimeout(this.voiceRestartTimeout);
        this.voiceRestartTimeout = setTimeout(() => {
          if (!this.userManuallyStoppedVoice && this.isInterviewListening()) {
            this.startInterviewVoiceSession();
          }
        }, 500);
      }
    }
  }

  stopInterviewVoice(): void {
    this.userManuallyStoppedVoice = true;
    this.isInterviewListening.set(false);
    if (this.voiceRestartTimeout) {
      clearTimeout(this.voiceRestartTimeout);
      this.voiceRestartTimeout = null;
    }
    if (this.speechRecognitionInstance) {
      try {
        this.speechRecognitionInstance.onend = null;
        this.speechRecognitionInstance.onerror = null;
        this.speechRecognitionInstance.stop();
      } catch (_) {}
      this.speechRecognitionInstance = null;
    }
    if (this.voiceAccumulatedFinal) {
      this.voiceBaseText = (this.voiceBaseText ? `${this.voiceBaseText} ${this.voiceAccumulatedFinal}` : this.voiceAccumulatedFinal).trim();
      this.voiceAccumulatedFinal = '';
      this.interviewInputText.set(this.voiceBaseText);
    }
  }

  switchInputMode(mode: 'INTERVIEW' | 'FORM'): void {
    if (this.isInterviewListening()) {
      this.stopInterviewVoice();
    }
    if (mode === 'INTERVIEW') {
      // Si el usuario ingresó o modificó datos en el formulario manual, asegurar sincronización al dossier
      this.composeDossierFromParameters();
    } else if (mode === 'FORM') {
      // Sincronización instantánea de la conversación hacia realitySeed
      this.syncChatHistoryToRealitySeed();
      if (this.fullPersonDossierText().trim()) {
        this.syncDossier();
      }
    }
    this.activeInputMode.set(mode);
  }

  isTaxiProfile(): boolean {
    const c = (this.realitySeed.occupation || this.realitySeed.career_or_degree || '').toLowerCase();
    return c.includes('taxi') || c.includes('mototaxi') || c.includes('chofer') || c.includes('conductor') || c.includes('transporte') || c.includes('colectivo');
  }

  isRuralProfile(): boolean {
    const p = this.realitySeed.life_profile_type;
    const c = (this.realitySeed.occupation || this.realitySeed.career_or_degree || '').toLowerCase();
    return p === 'RURAL_FIELD_PRODUCER' || c.includes('granja') || c.includes('avícol') || c.includes('avicol') || c.includes('porcin') || c.includes('cuy') || c.includes('galpón') || c.includes('galpon') || c.includes('campo') || c.includes('chacra') || c.includes('agrícol') || c.includes('agricol');
  }

  isBusinessProfile(): boolean {
    const p = this.realitySeed.life_profile_type;
    const c = (this.realitySeed.occupation || this.realitySeed.career_or_degree || '').toLowerCase();
    return p === 'BUSINESS_OWNER' || ((c.includes('comerc') || c.includes('tienda') || c.includes('bodega') || c.includes('abarrote') || c.includes('negocio') || c.includes('emprend')) && !this.isTaxiProfile());
  }

  getProfileIcon(profileType?: string): string {
    if (this.isTaxiProfile()) return '🚕';
    if (this.isRuralProfile()) return '🚜';
    if (this.isBusinessProfile()) return '🏪';
    switch (profileType) {
      case 'DAY_TO_DAY_WORKER': return '🛒';
      case 'RURAL_FIELD_PRODUCER': return '🚜';
      case 'SKILLED_TRADE': return '🔧';
      case 'TITLED_PROFESSIONAL': return '🎓';
      case 'UNIVERSITY_OR_TECH_STUDENT': return '📚';
      case 'BUSINESS_OWNER': return '🏪';
      default: return '⚡';
    }
  }

  getProfileLabel(profileType?: string): string {
    const isEs = this.drJefService.language() === 'ES';
    if (this.isTaxiProfile()) return isEs ? 'Conductor / Taxista / Movilidad' : 'Driver / Taxi / Urban Mobility';
    if (this.isRuralProfile()) return isEs ? 'Productor Rural / Granjas / Campo' : 'Rural Producer / Farms / Livestock';
    if (this.isBusinessProfile()) return isEs ? 'Dueño de Negocio / Emprendedor / Comercio' : 'Business Owner / Entrepreneur';
    switch (profileType) {
      case 'DAY_TO_DAY_WORKER': return isEs ? 'Trabajador del Día a Día / Comercio' : 'Day-to-day Worker / Commerce';
      case 'RURAL_FIELD_PRODUCER': return isEs ? 'Productor Rural / Granjas' : 'Rural Producer / Farms';
      case 'SKILLED_TRADE': return isEs ? 'Oficio Técnico / Especialista' : 'Skilled Trade / Specialist';
      case 'TITLED_PROFESSIONAL': return isEs ? 'Profesional Titulado / Sueldo Fijo' : 'Titled Professional / Salaried';
      case 'UNIVERSITY_OR_TECH_STUDENT': return isEs ? 'Estudiante Universitario / Técnico' : 'University / Technical Student';
      case 'BUSINESS_OWNER': return isEs ? 'Dueño de Negocio / Emprendedor' : 'Business Owner / Entrepreneur';
      default: return isEs ? 'Perfil de Realidad' : 'Reality Profile';
    }
  }

  getOpportunitiesSectionTitle(): string {
    const isEs = this.drJefService.language() === 'ES';
    if (this.isTaxiProfile()) {
      return isEs ? 'Oportunidades de Movilidad, Plataformas y Financiamiento Vehicular' : 'Urban Mobility, Driving Platforms & Vehicle Financing';
    }
    if (this.isRuralProfile()) {
      return isEs ? 'Fondos Agrarios, Financiamiento Pecuario y Acuerdos de Acopio' : 'Agricultural Grants, Farm Financing & Wholesale Supply';
    }
    if (this.isBusinessProfile()) {
      return isEs ? 'Fondos Concursables, Financiamiento Pyme y Programas de Crecimiento' : 'Competitive Grants, SME Financing & Growth Programs';
    }
    return isEs ? 'Convocatorias y Vacantes Reales Analizadas' : 'Empirical Labor Market Audit & Real Vacancies';
  }

  getOpportunitiesSectionSubtitle(): string {
    const isEs = this.drJefService.language() === 'ES';
    const city = this.realitySeed.location.city || (isEs ? 'tu ciudad' : 'your city');
    if (this.isTaxiProfile()) {
      return isEs
        ? `Plataformas de movilidad urbana, crédito para vehículo propio y contratos de ruta fija en ${city}`
        : `Mobility platforms, vehicle conversion loans and corporate routes in ${city}`;
    }
    if (this.isRuralProfile()) {
      return isEs
        ? `Fondos de tecnificación (AGROIDEAS/Procompite), crédito Agrobanco y venta directa para tu granja en ${city}`
        : `Technification grants (AGROIDEAS/Procompite), Agrobanco credit and direct wholesale supply in ${city}`;
    }
    if (this.isBusinessProfile()) {
      return isEs
        ? `Fondos de capital de trabajo, crédito productivo preferencial y formalización comercial en ${city}`
        : `Working capital grants, preferential SME loans and business formalization in ${city}`;
    }
    return isEs
      ? `Supervivencia de inserción Weibull/Cox + cotejo de convocatorias activas en ${city}`
      : `Weibull/Cox survival analysis + live job openings benchmarked in ${city}`;
  }

  getOpportunitiesListLabel(): string {
    const isEs = this.drJefService.language() === 'ES';
    if (this.isTaxiProfile()) return isEs ? 'Oportunidades de Ruta y Financiamiento Evaluadas' : 'Mobility & Financing Opportunities Analyzed';
    if (this.isRuralProfile()) return isEs ? 'Fondos Agrarios y Acuerdos Mayoristas Evaluados' : 'Agricultural Funds & Wholesale Agreements Evaluated';
    if (this.isBusinessProfile()) return isEs ? 'Programas de Financiamiento y Fondos Evaluados' : 'Grants & Funding Programs Evaluated';
    return isEs ? 'Convocatorias y Vacantes Reales Analizadas' : 'Active Real Vacancies Evaluated';
  }

  getOpportunityButtonLabel(): string {
    const isEs = this.drJefService.language() === 'ES';
    if (this.isTaxiProfile()) return isEs ? 'Ver Plataforma / Requisitos' : 'Inspect Platform / Requirements';
    if (this.isRuralProfile()) return isEs ? 'Ver Convocatoria / Bases del Fondo' : 'Inspect Agricultural Call / Bases';
    if (this.isBusinessProfile()) return isEs ? 'Ver Fondo / Bases de Financiamiento' : 'Inspect Grant / SME Funding';
    return isEs ? 'Ver Convocatoria / Postular' : 'Inspect Vacancy / Application';
  }

  getActuarialClockTitle(): string {
    const isEs = this.drJefService.language() === 'ES';
    if (this.isTaxiProfile()) {
      return isEs ? 'Reloj Actuarial de Consolidación y Unidad Propia' : 'Actuarial Route to Personal Fleet & Unit Amortization';
    }
    if (this.isRuralProfile()) {
      return isEs ? 'Reloj Actuarial de Maduración y Salida de Producción' : 'Actuarial Farm Maturation & Production Cycle';
    }
    if (this.isBusinessProfile()) {
      return isEs ? 'Reloj Actuarial de Punto de Venta y Retorno de Capital' : 'Actuarial SME Break-Even & Expansion Clock';
    }
    return isEs ? 'Reloj Actuarial de Inserción Laboral (Modelo Weibull/Cox)' : 'Actuarial Job Insertion Clock (Weibull/Cox Survival Model)';
  }

  syncChatHistoryToRealitySeed(): void {
    const messages = this.interviewHistory()
      .filter(m => m.role === 'user')
      .map(m => m.content)
      .join('\n');
    if (!messages.trim()) return;

    const t = messages.toLowerCase();

    // 1. Nombre
    const mName = messages.match(/(?:me llamo|mi nombre es|soy)\s+([A-ZÁÉÍÓÚa-záéíóú]+(?:\s+[A-ZÁÉÍÓÚa-záéíóú]+){0,3})/i);
    if (mName && mName[1]) {
      const cand = mName[1].trim();
      const candLow = cand.toLowerCase();
      if (!candLow.startsWith('de ') && !candLow.startsWith('un ') && !candLow.startsWith('una ') &&
          !candLow.startsWith('estudiante') && !candLow.startsWith('programador') && !candLow.startsWith('taxista')) {
        this.realitySeed.full_name = cand;
        this.realitySeed.person_identifier = cand;
      }
    }

    // 2. Edad
    const mAge = t.match(/([0-9]{1,2})\s*(?:años|anos|years)/i) || t.match(/tengo\s*([0-9]{1,2})/i) || t.match(/edad(?:\s*es)?\s*(?:de)?\s*([0-9]{1,2})/i);
    if (mAge && mAge[1]) {
      const parsedAge = parseInt(mAge[1], 10);
      if (parsedAge >= 15 && parsedAge <= 90) {
        this.realitySeed.age = parsedAge;
      }
    }

    // 3. Ciudad y País
    if (t.includes('huancayo')) { this.realitySeed.location.city = 'Huancayo'; this.realitySeed.location.country = 'Perú'; this.realitySeed.finances.currency = 'PEN'; }
    else if (t.includes('lima')) { this.realitySeed.location.city = 'Lima'; this.realitySeed.location.country = 'Perú'; this.realitySeed.finances.currency = 'PEN'; }
    else if (t.includes('arequipa')) { this.realitySeed.location.city = 'Arequipa'; this.realitySeed.location.country = 'Perú'; this.realitySeed.finances.currency = 'PEN'; }
    else if (t.includes('cusco')) { this.realitySeed.location.city = 'Cusco'; this.realitySeed.location.country = 'Perú'; this.realitySeed.finances.currency = 'PEN'; }
    else if (t.includes('trujillo')) { this.realitySeed.location.city = 'Trujillo'; this.realitySeed.location.country = 'Perú'; this.realitySeed.finances.currency = 'PEN'; }
    else if (t.includes('bogot')) { this.realitySeed.location.city = 'Bogotá'; this.realitySeed.location.country = 'Colombia'; this.realitySeed.finances.currency = 'COP'; }
    else if (t.includes('medell')) { this.realitySeed.location.city = 'Medellín'; this.realitySeed.location.country = 'Colombia'; this.realitySeed.finances.currency = 'COP'; }
    else if (t.includes('cdmx') || t.includes('méxico') || t.includes('mexico')) { this.realitySeed.location.city = 'Ciudad de México'; this.realitySeed.location.country = 'México'; this.realitySeed.finances.currency = 'MXN'; }

    // 4. Ocupación y Arquetipo
    const isTaxi = t.includes('taxista') || t.includes('taxi') || t.includes('mototaxi') || t.includes('chofer') || t.includes('conductor') || t.includes('colectivo');
    const isRural = t.includes('granja') || t.includes('granjas') || t.includes('avícol') || t.includes('avicol') || t.includes('porcin') || t.includes('cuy') || t.includes('galpón') || t.includes('galpon') || t.includes('campo') || t.includes('agrícol') || t.includes('chacra') || t.includes('ganad');
    const isBusiness = (t.includes('comerciante') || t.includes('comercio') || t.includes('tienda') || t.includes('bodega') || t.includes('abarrotes') || t.includes('negocio') || t.includes('emprend')) && !isTaxi;
    const isGrad = t.includes('egresad') || t.includes('bachiller') || t.includes('titulad') || t.includes('colegiad');
    const isTrade = t.includes('electric') || t.includes('mecanic') || t.includes('mecánic') || t.includes('taller') || t.includes('gasfiter') || t.includes('carpinter');
    const isStudent = !isGrad && !isTaxi && !isRural && !isBusiness && (t.includes('estudiant') || t.includes('estudio ') || t.includes('ciclo') || t.includes('universidad') || t.includes('instituto'));

    if (isTaxi) {
      this.realitySeed.life_profile_type = 'DAY_TO_DAY_WORKER';
      this.realitySeed.occupation = 'Taxista / Conductor de Transporte Urbano';
      this.realitySeed.career_or_degree = 'Transporte & Conducción (Taxi)';
    } else if (isRural) {
      this.realitySeed.life_profile_type = 'RURAL_FIELD_PRODUCER';
      this.realitySeed.occupation = 'Productor Agropecuario / Granjas';
      this.realitySeed.career_or_degree = 'Producción Agropecuaria y Granjas';
    } else if (isBusiness) {
      this.realitySeed.life_profile_type = 'BUSINESS_OWNER';
      this.realitySeed.occupation = 'Comerciante / Dueño de Negocio';
      this.realitySeed.career_or_degree = 'Comercio & Gestión de Negocio';
    } else if (isGrad) {
      this.realitySeed.life_profile_type = 'TITLED_PROFESSIONAL';
      if (!this.realitySeed.occupation) this.realitySeed.occupation = 'Profesional Titulado / Egresado';
    } else if (isTrade) {
      this.realitySeed.life_profile_type = 'SKILLED_TRADE';
      if (!this.realitySeed.occupation) this.realitySeed.occupation = 'Técnico Especialista';
    } else if (isStudent) {
      this.realitySeed.life_profile_type = 'UNIVERSITY_OR_TECH_STUDENT';
      if (!this.realitySeed.occupation) this.realitySeed.occupation = 'Estudiante Universitario/Técnico';
    }

    // 5. Ingresos Diarios o Mensuales
    const mIncDaily = t.match(/(?:diario|al d[ií]a|por d[ií]a).*?(?:s\/?\.?|\$)?\s*([0-9]+[0-9,\.]*)/i) || t.match(/(?:gano|ingreso).*?([0-9]+[0-9,\.]*)\s*(?:soles|d[oó]lares|diarios|al d[ií]a)/i);
    if (mIncDaily && mIncDaily[1]) {
      const val = parseFloat(mIncDaily[1].replace(/,/g, ''));
      if (!isNaN(val) && val > 0) {
        this.realitySeed.daily_income_avg = val;
        this.realitySeed.finances.monthly_income = Math.round(val * 6 * 4.333);
      }
    } else {
      const mInc = t.match(/(?:ingreso|gano|sueldo|salario)\s*(?:de|es)?\s*(?:s\/?\.?|\$)?\s*([0-9]+[0-9,\.]*)/i);
      if (mInc && mInc[1]) {
        const val = parseFloat(mInc[1].replace(/,/g, ''));
        if (!isNaN(val) && val > 0) {
          this.realitySeed.finances.monthly_income = val;
        }
      }
    }

    // 6. Gastos, Ahorros, Deudas
    const mExp = t.match(/(?:gasto|costo)\s*(?:de|es)?\s*(?:s\/?\.?|\$)?\s*([0-9]+[0-9,\.]*)/i);
    if (mExp && mExp[1]) {
      const val = parseFloat(mExp[1].replace(/,/g, ''));
      if (!isNaN(val)) this.realitySeed.finances.monthly_expenses = val;
    }
    const mSav = t.match(/(?:ahorro|guardado)\s*(?:de|es)?\s*(?:s\/?\.?|\$)?\s*([0-9]+[0-9,\.]*)/i);
    if (mSav && mSav[1]) {
      const val = parseFloat(mSav[1].replace(/,/g, ''));
      if (!isNaN(val)) this.realitySeed.finances.current_savings = val;
    }
    const mDeb = t.match(/(?:deuda|pr[eé]stamo|cr[eé]dito)\s*(?:de|es)?\s*(?:s\/?\.?|\$)?\s*([0-9]+[0-9,\.]*)/i);
    if (mDeb && mDeb[1]) {
      const val = parseFloat(mDeb[1].replace(/,/g, ''));
      if (!isNaN(val)) this.realitySeed.finances.current_debt = val;
    }

    // 7. Horas de rutina
    const mSleep = t.match(/(?:duermo|sueño|dormir|descanso)\s*(?:unas|unos|alrededor de)?\s*([0-9]+(?:\.[0-9]+)?)\s*h/i) || t.match(/([0-9]+(?:\.[0-9]+)?)\s*h(?:oras)?\s*(?:de\s+)?(?:sueño|dormir|descanso)/i);
    if (mSleep && mSleep[1]) this.realitySeed.time_use.sleep_hours = parseFloat(mSleep[1]);

    const mWork = t.match(/(?:trabajo|laboro|jornada|al volante)\s*(?:unas|unos|de)?\s*([0-9]+(?:\.[0-9]+)?)\s*h/i) || t.match(/([0-9]+(?:\.[0-9]+)?)\s*h(?:oras)?\s*(?:de\s+)?(?:trabajo|jornada)/i);
    if (mWork && mWork[1]) this.realitySeed.time_use.work_hours = parseFloat(mWork[1]);

    const mScreen = t.match(/(?:pantalla|pantallas|redes|celular|ocio|tik\s*tok)\s*(?:unas|unos|de)?\s*([0-9]+(?:\.[0-9]+)?)\s*h/i) || t.match(/([0-9]+(?:\.[0-9]+)?)\s*h(?:oras)?\s*(?:en|de)?\s*(?:pantalla|redes|ocio|celular)/i);
    if (mScreen && mScreen[1]) this.realitySeed.time_use.screen_time_lost_hours = parseFloat(mScreen[1]);

    // 8. Metas
    const mGoal = t.match(/(?:meta a corto plazo|meta principal|meta a 1 año|meta|sueño|quiero|plan)\s*(?:es|de)?\s*([^.\n]{5,100})/i);
    if (mGoal && mGoal[1]) {
      this.realitySeed.goal_mode = true;
      this.realitySeed.one_year_goal = mGoal[1].trim();
      this.realitySeed.main_goal_1y = mGoal[1].trim();
    }
  }

  composeDossierFromParameters(): void {
    const s = this.realitySeed;
    const isEn = this.drJefService.language() === 'EN';
    const lines: string[] = [];
    if (s.full_name) lines.push(isEn ? `Name: ${s.full_name}` : `Nombre: ${s.full_name}`);
    if (s.age) lines.push(isEn ? `Age: ${s.age} years old` : `Edad: ${s.age} años`);
    if (s.location.city || s.location.country) lines.push(isEn ? `Location: ${s.location.city}, ${s.location.country}` : `Ubicación: ${s.location.city}, ${s.location.country}`);
    if (s.career_or_degree) lines.push(isEn ? `Career/Study: ${s.career_or_degree}` : `Carrera/Ocupación: ${s.career_or_degree}`);
    if (s.university_or_institution) lines.push(isEn ? `Institution: ${s.university_or_institution}` : `Institución: ${s.university_or_institution}`);
    if (s.life_profile_type) lines.push(isEn ? `Profile: ${s.life_profile_type}` : `Perfil: ${s.life_profile_type}`);
    if (s.finances.monthly_income) lines.push(isEn ? `Monthly income: ${s.finances.currency} ${s.finances.monthly_income}` : `Ingreso mensual: ${s.finances.currency} ${s.finances.monthly_income}`);
    if (s.finances.monthly_expenses) lines.push(isEn ? `Monthly expenses: ${s.finances.currency} ${s.finances.monthly_expenses}` : `Gastos mensuales: ${s.finances.currency} ${s.finances.monthly_expenses}`);
    if (s.finances.current_savings) lines.push(isEn ? `Savings: ${s.finances.currency} ${s.finances.current_savings}` : `Ahorros actuales: ${s.finances.currency} ${s.finances.current_savings}`);
    if (s.one_year_goal) lines.push(isEn ? `1-Year Goal: ${s.one_year_goal}` : `Meta a 1 Año: ${s.one_year_goal}`);
    if (s.medium_term_goals) lines.push(isEn ? `Medium-Term Goals (2-3Y): ${s.medium_term_goals}` : `Metas a Mediano Plazo (2-3A): ${s.medium_term_goals}`);
    if (s.long_term_goals) lines.push(isEn ? `Long-Term Goals & Ideals (5Y+): ${s.long_term_goals}` : `Ideales y Metas a Largo Plazo (5A+): ${s.long_term_goals}`);
    if (lines.length > 0) {
      this.fullPersonDossierText.set(lines.join('\n'));
      this.dossierGenerated.set(true);
    }
  }

  onGoalFieldChanged(): void {
    if (this.realitySeed.one_year_goal || this.realitySeed.medium_term_goals || this.realitySeed.long_term_goals) {
      this.realitySeed.goal_mode = true;
      if (this.realitySeed.one_year_goal) {
        this.realitySeed.main_goal_1y = this.realitySeed.one_year_goal;
      }
    }
  }

  getEvaluatedGoals(report?: GoalsVerificationReport | null): GoalFeasibilityItem[] {
    if (!report) return [];
    const list: GoalFeasibilityItem[] = [];
    if (report.short_term_1y) list.push(report.short_term_1y);
    if (report.medium_term_3y) list.push(report.medium_term_3y);
    if (report.long_term_5y) list.push(report.long_term_5y);
    return list;
  }

  getMissingPillarsText(): string {
    const isEs = this.drJefService.language() === 'ES';
    const cov = this.interviewPillarsCovered();
    const missing: string[] = [];
    if (!cov['identity']) missing.push(isEs ? 'identidad/ciudad' : 'identity/city');
    if (!cov['goals']) missing.push(isEs ? 'metas' : 'goals');
    if (!cov['economy']) missing.push(isEs ? 'economía' : 'finances');
    if (!cov['routine']) missing.push(isEs ? 'rutina 24h' : '24h routine');
    if (!cov['family']) missing.push(isEs ? 'familia/cuidados' : 'family/care');
    if (!cov['personality']) missing.push(isEs ? 'carácter' : 'character');
    if (missing.length === 0) return isEs ? '¡Perfil completo!' : 'Profile complete!';
    return isEs ? `Falta: ${missing.slice(0, 2).join(', ')}` : `Missing: ${missing.slice(0, 2).join(', ')}`;
  }

  getSpanishTraitNames(traits?: string[]): string {
    if (!traits || traits.length === 0) return 'Resiliente, Enfocado';
    const dict: Record<string, string> = {
      'PROCRASTINATOR': 'Posterga tareas clave',
      'ANXIOUS_OVERTHINKER': 'Sobrepensador',
      'AMBITIOUS': 'Ambicioso',
      'DISCIPLINED': 'Disciplinado',
      'RESILIENT': 'Resiliente',
      'BURNOUT_PRONE': 'Propenso a agotamiento',
      'ISOLATION_PRONE': 'Tendencia a aislarse'
    };
    return traits.map(t => dict[t] || t).join(', ');
  }

  onInterviewFileUploaded(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (!input.files || input.files.length === 0) return;
    const file = input.files[0];
    this.uploadedFileName.set(file.name);

    if (file.name.toLowerCase().endsWith('.ics')) {
      this.api.ingestCalendarIcs(file).subscribe({
        next: (res) => {
          const days = Math.max(1, res.busy_metrics.days_count || 7);
          const w_h = Number((res.busy_metrics.work_hours_total / days).toFixed(1)) || 8.0;
          const s_h = Number((res.busy_metrics.thesis_hours_total / days).toFixed(1)) || 2.0;
          this.realitySeed.time_use.work_hours = w_h;
          this.realitySeed.time_use.study_project_hours = s_h;
          const msg = this.drJefService.language() === 'ES'
            ? `He procesado tu calendario '${file.name}'. Detecté ${w_h}h de trabajo y ${s_h}h de estudio al día. Continúa contándome sobre tu economía o metas.`
            : `Processed calendar '${file.name}'. Found ${w_h}h work and ${s_h}h study daily. Keep telling me about your finances or goals.`;
          this.interviewHistory.set([...this.interviewHistory(), { role: 'assistant', content: msg }]);
        },
        error: () => {}
      });
    } else {
      this.api.ingestWhatsApp(file).subscribe({
        next: (res) => {
          if (res && res.contact_record) {
            const rec = res.contact_record;
            const msgCount = rec.total_messages_analyzed || 0;
            this.realitySeed.chat_median_reply_min = rec.real_median_reply_minutes || null;
            this.realitySeed.chat_extracted_summary = rec.extracted_psych_summary || `Chat con ${rec.contact_name}, ${msgCount} mensajes.`;
            const msg = this.drJefService.language() === 'ES'
              ? `He procesado tu chat '${file.name}' (${msgCount} mensajes con ${rec.contact_name}). Integré tu comunicación a tu perfil. Cuéntame sobre tus metas para este año.`
              : `Processed chat '${file.name}' (${msgCount} messages). Integrated your communication profile. Tell me about your goals for this year.`;
            this.interviewHistory.set([...this.interviewHistory(), { role: 'assistant', content: msg }]);
          }
        },
        error: () => {}
      });
    }
  }

  // ==========================================
  // Métodos de Historial Laboral (Life2Vec)
  // ==========================================

  addCareerEvent(): void {
    if (!this.newCareerEvent.title_or_role) return;
    if (!this.realitySeed.past_career_events) {
      this.realitySeed.past_career_events = [];
    }
    this.realitySeed.past_career_events.push({ ...this.newCareerEvent });
    this.newCareerEvent = {
      year: new Date().getFullYear(),
      age_at_event: this.realitySeed.age || 24,
      event_type: 'ROLE_CHANGE',
      title_or_role: '',
      monthly_income: 0,
      location: this.realitySeed.location.city || '',
      description: ''
    };
    this.isAddingCareerEvent.set(false);
  }

  removeCareerEvent(idx: number): void {
    if (this.realitySeed.past_career_events) {
      this.realitySeed.past_career_events.splice(idx, 1);
    }
  }

  selectCareerHorizon(idx: number): void {
    if (idx >= 0) {
      this.selectedCareerHorizonIndex.set(idx);
    }
  }

  synthesizeCareerHistory(): void {
    const s = this.realitySeed;
    const curYear = new Date().getFullYear();
    const curAge = s.age || 24;
    const city = s.location.city || 'Local';
    const income = s.finances.monthly_income || 0;
    const occ = s.occupation || s.career_or_degree || 'Especialista';

    const events: CareerLifeEvent[] = [
      {
        year: curYear - 4,
        age_at_event: Math.max(18, curAge - 4),
        event_type: 'EDUCATION',
        title_or_role: s.university_or_institution ? `Inicio de Estudios en ${s.university_or_institution}` : `Inicio de Formación Superior en ${occ}`,
        monthly_income: 0,
        location: city,
        description: 'Fundamentos académicos y técnicos adquiridos.'
      },
      {
        year: curYear - 2,
        age_at_event: Math.max(19, curAge - 2),
        event_type: 'FIRST_JOB',
        title_or_role: `Primeras Prácticas / Actividades de Sustento (${occ})`,
        monthly_income: Math.round(income * 0.4) || 600,
        location: city,
        description: 'Primeras experiencias prácticas y desarrollo de habilidades operativas.'
      },
      {
        year: curYear,
        age_at_event: curAge,
        event_type: 'CURRENT_STATE',
        title_or_role: `${occ} (Estado Actual)`,
        monthly_income: income,
        location: city,
        description: 'Posición actual con foco en expansión laboral y consolidación de ingresos.'
      }
    ];
    this.realitySeed.past_career_events = events;
  }

  onCvFileUploaded(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (!input.files || input.files.length === 0) return;
    const file = input.files[0];
    this.uploadedFileName.set(file.name);
    const reader = new FileReader();
    reader.onload = () => {
      const text = (reader.result as string) || '';
      this.extractCareerEventsFromCvText(text, file.name);
    };
    reader.readAsText(file);
  }

  extractCareerEventsFromCvText(text: string, fileName: string): void {
    const isEs = this.drJefService.language() === 'ES';
    this.synthesizeCareerHistory();
    const msg = isEs
      ? `📄 He procesado tu CV / Resumen '${fileName}'. Se ha digitalizado tu secuencia de hitos laborales y formación previa para el motor Life2Vec.`
      : `📄 Processed your CV / Resume '${fileName}'. Your sequential career and education milestones have been digitized for the Life2Vec engine.`;
    this.interviewHistory.set([...this.interviewHistory(), { role: 'assistant', content: msg }]);
  }


  // ==========================================
  // Menú Desplegable Lateral de Parámetros
  // ==========================================
  isParametersDrawerOpen = signal<boolean>(false);

  toggleParametersDrawer(): void {
    this.isParametersDrawerOpen.update(v => !v);
  }

  closeParametersDrawer(): void {
    this.isParametersDrawerOpen.set(false);
  }

  startNewConversation(): void {
    this.futureResponse.set(null);
    this.dossierGenerated.set(false);
    this.activeInputMode.set('INTERVIEW');
    this.initInterviewConversation();
  }

  recalculateFromDrawer(): void {
    this.isParametersDrawerOpen.set(false);
    this.predictFuture();
  }

}
