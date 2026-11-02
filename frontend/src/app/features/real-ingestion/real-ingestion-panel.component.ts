import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DrJefApiService } from '../../core/services/dr-jef-api.service';
import { DrJefService } from '../../core/services/dr-jef.service';
import {
  IngestWhatsAppResponse,
  IngestCalendarResponse,
  IngestGitHubResponse,
  SyncTelemetryResponse
} from '../../core/models/dr-jef.model';

@Component({
  selector: 'app-real-ingestion-panel',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="space-y-8 max-w-7xl mx-auto p-4 md:p-6">
      <!-- Header Banner -->
      <div class="relative overflow-hidden rounded-2xl bg-gradient-to-r from-emerald-950/80 via-slate-900 to-slate-950 border border-emerald-500/20 p-6 md:p-8 backdrop-blur-xl shadow-2xl">
        <div class="absolute -top-24 -right-24 w-80 h-80 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
          <div>
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-3">
              <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
              {{ drJefService.language() === 'EN' ? 'Real Production Ingestion • Zero Mocks' : 'Ingesta de Producción Real • Cero Mocks' }}
            </div>
            <h1 class="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
              {{ drJefService.language() === 'EN' ? 'Telemetry Ingestion & Forensic Extraction' : 'Ingesta de Telemetría & Extracción Forense' }}
            </h1>
            <p class="text-slate-300 mt-2 text-sm md:text-base max-w-3xl leading-relaxed">
              {{ drJefService.language() === 'EN' ? 'Feed the MIRROR FUTURE causal engine with real empirical records: WhatsApp chat exports (.txt/.zip), Google Calendar schedules (.ics), and GitHub development telemetry.' : 'Alimenta el motor causal MIRROR FUTURE con registros empíricos reales: exportaciones de chat de WhatsApp (.txt/.zip), agenda de Google Calendar (.ics) y telemetría de desarrollo de GitHub.' }}
            </p>
          </div>
          
          <div class="flex flex-wrap items-center gap-3">
            <button
              (click)="syncAllTelemetry()"
              [disabled]="isSyncingTelemetry"
              class="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-semibold text-sm shadow-lg shadow-emerald-900/30 transition-all active:scale-95 disabled:opacity-50 disabled:pointer-events-none">
              @if (isSyncingTelemetry) {
                <svg class="animate-spin h-4 w-4 text-white" viewBox="0 0 24 24" fill="none">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                </svg>
                <span>{{ drJefService.language() === 'EN' ? 'Syncing Telemetry...' : 'Sincronizando Telemetría...' }}</span>
              } @else {
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
                <span>{{ drJefService.language() === 'EN' ? 'SYNC GLOBAL TELEMETRY' : 'SINCRONIZAR TELEMETRÍA GLOBAL' }}</span>
              }
            </button>

            <!-- Botón Borrado Seguro -->
            <button
              (click)="purgeAllUserData()"
              [disabled]="isPurgingData"
              class="inline-flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-red-950/60 hover:bg-red-900/80 border border-red-500/40 text-red-200 font-semibold text-sm transition-all active:scale-95 disabled:opacity-50"
              title="Permanently erase all your stored data">
              @if (isPurgingData) {
                <svg class="animate-spin h-4 w-4 text-red-300" viewBox="0 0 24 24" fill="none">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                </svg>
                <span>Purging...</span>
              } @else {
                <svg class="w-4 h-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                <span>Purge All My Data</span>
              }
            </button>
          </div>
        </div>
      </div>

      <!-- Banner de Privacidad y Consentimiento -->
      <div class="rounded-xl bg-slate-900/90 border border-emerald-500/30 p-4 text-slate-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 backdrop-blur-md">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shrink-0">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <div class="text-xs md:text-sm">
            <span class="font-bold text-white">Privacy Protected:</span>
            <span class="text-slate-300 ml-1">You can anonymize names and phone numbers locally in your browser before analysis, and erase all your data with one click.</span>
          </div>
        </div>

        <label class="inline-flex items-center gap-2 cursor-pointer text-xs font-medium text-emerald-300 bg-emerald-950/40 px-3 py-1.5 rounded-lg border border-emerald-500/30 select-none">
          <input type="checkbox" [(ngModel)]="anonymizeLocally" class="w-4 h-4 rounded accent-emerald-500 cursor-pointer" />
          <span>Anonymize in my browser before upload</span>
        </label>
      </div>

      <!-- Purge feedback alert -->
      @if (purgeSuccessMessage) {
        <div class="rounded-xl bg-red-950/50 border border-red-500/40 p-4 text-red-200 flex items-center gap-3">
          <svg class="w-5 h-5 text-red-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          <span class="text-sm font-semibold">{{ purgeSuccessMessage }}</span>
        </div>
      }

      <!-- Sync feedback alert -->
      @if (syncResponse) {
        <div class="rounded-xl bg-emerald-950/40 border border-emerald-500/30 p-4 text-emerald-300 flex items-start gap-3 backdrop-blur-md">
          <svg class="w-5 h-5 text-emerald-400 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <div class="text-sm">
            <p class="font-semibold text-white">Telemetría de Usuario Sincronizada con Supabase</p>
            <p class="text-slate-300 mt-1">
              Perfil: <strong class="text-emerald-300">{{ syncResponse.user_real_profile.full_name }}</strong> &bull;
              Alias: <strong class="text-emerald-300">{{ syncResponse.user_real_profile.whatsapp_alias }}</strong> &bull;
              Horas Ocupadas/Semana: <strong class="text-emerald-300">{{ syncResponse.user_real_profile.real_calendar_busy_hours_week }}h</strong> &bull;
              Horas Tesis/Día: <strong class="text-emerald-300">{{ syncResponse.user_real_profile.real_study_thesis_hours_day }}h</strong>
            </p>
          </div>
        </div>
      }

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <!-- SECCIÓN 1: WhatsApp Ingestion (Col 1-7) -->
        <div class="lg:col-span-7 space-y-6">
          <div class="rounded-2xl bg-slate-900/80 border border-slate-800 p-6 backdrop-blur-xl shadow-xl">
            <div class="flex items-center justify-between pb-4 border-b border-slate-800">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 font-bold">
                  WA
                </div>
                <div>
                  <h2 class="text-lg font-bold text-white">1. Ingesta Forense de WhatsApp</h2>
                  <p class="text-xs text-slate-400">Archivos reales .txt o .zip (Android e iOS, 12h/24h)</p>
                </div>
              </div>
              <span class="text-xs font-mono text-emerald-400 px-2.5 py-1 rounded-md bg-emerald-950/60 border border-emerald-800/50">
                POST /api/ingest/whatsapp
              </span>
            </div>

            <div class="mt-6 space-y-5">
              <!-- Upload Area -->
              <div class="relative border-2 border-dashed rounded-xl p-6 text-center transition-all"
                   [ngClass]="whatsappFile ? 'border-emerald-500/50 bg-emerald-950/10' : 'border-slate-700 hover:border-slate-600 bg-slate-950/40'">
                <input 
                  type="file" 
                  id="whatsappFileInput"
                  accept=".txt,.zip"
                  (change)="onWhatsAppFileSelected($event)"
                  class="absolute inset-0 w-full h-full opacity-0 cursor-pointer" />
                
                <div class="flex flex-col items-center">
                  <svg class="w-12 h-12 mb-3" [ngClass]="whatsappFile ? 'text-emerald-400' : 'text-slate-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                  </svg>
                  @if (whatsappFile) {
                    <p class="text-sm font-semibold text-emerald-300">{{ whatsappFile.name }}</p>
                    <p class="text-xs text-slate-300 mt-1">{{ (whatsappFile.size / 1024).toFixed(1) }} KB &bull; Archivo listo para parseo</p>
                    @if (anonymizedNote) {
                      <div class="mt-2 text-xs text-emerald-300 bg-emerald-950/80 border border-emerald-500/30 px-3 py-1.5 rounded-lg flex items-center justify-center gap-1.5">
                        <svg class="w-4 h-4 text-emerald-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                        </svg>
                        <span>{{ anonymizedNote }}</span>
                      </div>
                    }
                  } @else {
                    <p class="text-sm font-semibold text-slate-200">Arrastra tu exportación de WhatsApp aquí o haz clic</p>
                    <p class="text-xs text-slate-400 mt-1">Soporta .txt y .zip descargados directamente de la app</p>
                  }
                </div>
              </div>

              <!-- Metadata Controls -->
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label class="block text-xs font-medium text-slate-300 mb-1">Nombre o Alias del Contacto</label>
                  <input
                    type="text"
                    [(ngModel)]="contactName"
                    placeholder="Ej. Princesa, Dra. Gómez, Carlos"
                    class="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-700 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-emerald-500 transition-colors" />
                </div>
                <div>
                  <label class="block text-xs font-medium text-slate-300 mb-1">Tu Nombre / Alias en el Chat</label>
                  <input
                    type="text"
                    [(ngModel)]="userName"
                    placeholder="Tú"
                    class="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-700 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-emerald-500 transition-colors" />
                </div>
                <div>
                  <label class="block text-xs font-medium text-slate-300 mb-1">Tipo de Relación</label>
                  <select
                    [(ngModel)]="relationshipType"
                    class="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-700 text-white text-sm focus:outline-none focus:border-emerald-500 transition-colors">
                    <option value="FRIEND">Amigo/a (FRIEND)</option>
                    <option value="FAMILY">Familia (FAMILY)</option>
                    <option value="WORK">Trabajo / Tesis (WORK)</option>
                    <option value="ROMANTIC">Pareja (ROMANTIC)</option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-medium text-slate-300 mb-1">
                    Nivel de Cercanía: <span class="text-emerald-400 font-bold">{{ closenessLevel }}</span>
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    [(ngModel)]="closenessLevel"
                    class="w-full accent-emerald-500 h-2 bg-slate-950 rounded-lg cursor-pointer" />
                </div>
              </div>

              <!-- Submit WhatsApp Button -->
              <button
                (click)="submitWhatsAppIngestion()"
                [disabled]="!whatsappFile || isIngestingWhatsApp"
                class="w-full py-3 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 active:bg-emerald-700 text-white font-bold text-sm shadow-lg shadow-emerald-950/50 transition-all flex items-center justify-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed">
                @if (isIngestingWhatsApp) {
                  <svg class="animate-spin h-5 w-5 text-white" viewBox="0 0 24 24" fill="none">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                  </svg>
                  <span>Parseando y Vectorizando Chat (pgvector 384d)...</span>
                } @else {
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                  </svg>
                  <span>INGESTAR Y EXTRAER PERFIL MATEMÁTICO REAL</span>
                }
              </button>

              @if (whatsappError) {
                <div class="p-3 rounded-lg bg-red-950/60 border border-red-500/40 text-red-300 text-xs">
                  <strong>Error de Ingesta:</strong> {{ whatsappError }}
                </div>
              }
            </div>
          </div>

          <!-- RESULTADOS DE WHATSAPP: Métricas Reales -->
          @if (whatsappResult) {
            <div class="rounded-2xl bg-slate-900/90 border border-emerald-500/30 p-6 backdrop-blur-xl shadow-2xl space-y-6">
              <div class="flex items-center justify-between border-b border-slate-800 pb-3">
                <div class="flex items-center gap-2">
                  <span class="w-3 h-3 rounded-full bg-emerald-400"></span>
                  <h3 class="font-bold text-white text-base">
                    Métricas Reales Extraídas: {{ whatsappResult.contact_record.contact_name }}
                  </h3>
                </div>
                <span class="text-xs font-semibold px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  {{ whatsappResult.contact_record.relationship_type }}
                </span>
              </div>

              <!-- 4 Big Metric Cards -->
              <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <!-- Total Messages -->
                <div class="bg-slate-950/80 p-4 rounded-xl border border-slate-800">
                  <span class="text-xs text-slate-300 block mb-1">Total Mensajes</span>
                  <div class="text-2xl font-black text-white font-mono">
                    {{ whatsappResult.contact_record.total_messages_analyzed }}
                  </div>
                  <span class="text-xs text-slate-400">Historial completo</span>
                </div>

                <!-- Real Median Reply Minutes -->
                <div class="bg-slate-950/80 p-4 rounded-xl border border-emerald-500/30">
                  <span class="text-xs text-emerald-400 block mb-1">Mediana de Respuesta</span>
                  <div class="text-2xl font-black text-emerald-400 font-mono">
                    {{ whatsappResult.contact_record.real_median_reply_minutes }} <span class="text-xs font-normal text-slate-400">min</span>
                  </div>
                  <span class="text-xs text-slate-400">Tiempo de respuesta</span>
                </div>

                <!-- User Initiates Pct -->
                <div class="bg-slate-950/80 p-4 rounded-xl border border-cyan-500/30">
                  <span class="text-xs text-cyan-400 block mb-1">% Inicios de Chat</span>
                  <div class="text-2xl font-black text-cyan-400 font-mono">
                    {{ whatsappResult.contact_record.user_initiates_pct }}%
                  </div>
                  <span class="text-xs text-slate-400">Iniciativas propias</span>
                </div>

                <!-- Vectorized Episodes -->
                <div class="bg-slate-950/80 p-4 rounded-xl border border-purple-500/30">
                  <span class="text-xs text-purple-400 block mb-1">Episodios RAG (384d)</span>
                  <div class="text-2xl font-black text-purple-400 font-mono">
                    {{ whatsappResult.episodes_vectorized }}
                  </div>
                  <span class="text-xs text-slate-400">{{ whatsappResult.vector_storage_status }}</span>
                </div>
              </div>

              <!-- Top Words Reales -->
              <div>
                <h4 class="text-xs font-bold uppercase tracking-wider text-slate-300 mb-2 flex items-center gap-2">
                  <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z"></path>
                  </svg>
                  Top Palabras y Modismos Reales Característicos
                </h4>
                <div class="flex flex-wrap gap-2">
                  @for (w of whatsappResult.contact_record.real_lexical_profile.top_words.slice(0, 15); track w.word) {
                    <div class="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-200 flex items-center gap-2">
                      <span class="font-medium text-emerald-300">{{ w.word }}</span>
                      <span class="text-xs font-mono text-slate-300 bg-slate-900 px-1.5 py-0.5 rounded">{{ w.count }}x ({{ w.percentage }}%)</span>
                    </div>
                  }
                </div>
              </div>

              <!-- Top Emojis Reales -->
              <div>
                <h4 class="text-xs font-bold uppercase tracking-wider text-slate-300 mb-2 flex items-center gap-2">
                  <span>Top Emojis Más Utilizados en los Chats</span>
                </h4>
                <div class="flex flex-wrap gap-3">
                  @for (e of whatsappResult.contact_record.real_lexical_profile.top_emojis.slice(0, 10); track e.emoji) {
                    <div class="px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 flex items-center gap-2 shadow-inner">
                      <span class="text-xl">{{ e.emoji }}</span>
                      <div class="text-left">
                        <span class="block text-xs font-mono font-bold text-white">{{ e.count }}</span>
                        <span class="block text-xs text-slate-400 font-mono">{{ e.percentage }}%</span>
                      </div>
                    </div>
                  }
                </div>
              </div>

              <!-- Estilo Sintáctico y Tono -->
              <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-3 border-t border-slate-800 text-xs">
                <div>
                  <span class="text-slate-300 block">Estilo Sintáctico:</span>
                  <span class="font-mono text-slate-200 font-semibold">{{ whatsappResult.contact_record.real_lexical_profile.syntax_style }}</span>
                </div>
                <div>
                  <span class="text-slate-300 block">Tono Evaluado:</span>
                  <span class="font-mono text-emerald-300 font-semibold">{{ whatsappResult.contact_record.real_lexical_profile.tone }}</span>
                </div>
                <div>
                  <span class="text-slate-300 block">Promedio Palabras/Msg:</span>
                  <span class="font-mono text-slate-200 font-semibold">{{ whatsappResult.contact_record.real_lexical_profile.avg_words_per_message }}</span>
                </div>
              </div>
            </div>
          }
        </div>

        <!-- SECCIÓN 2 & 3: Calendar (.ics) & GitHub (Col 8-12) -->
        <div class="lg:col-span-5 space-y-6">
          <!-- CALENDARIO GOOGLE (.ICS) -->
          <div class="rounded-2xl bg-slate-900/80 border border-slate-800 p-6 backdrop-blur-xl shadow-xl">
            <div class="flex items-center justify-between pb-4 border-b border-slate-800">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 font-bold">
                  ICS
                </div>
                <div>
                  <h2 class="text-base font-bold text-white">2. Google Calendar (.ics)</h2>
                  <p class="text-xs text-slate-300">Parseo de bloques VEVENT reales</p>
                </div>
              </div>
              <span class="text-xs font-mono text-amber-400 px-2 py-0.5 rounded bg-amber-950/60 border border-amber-800/50">
                POST /calendar-ics
              </span>
            </div>

            <div class="mt-4 space-y-4">
              <div class="relative border-2 border-dashed rounded-xl p-4 text-center"
                   [ngClass]="calendarFile ? 'border-amber-500/50 bg-amber-950/10' : 'border-slate-700 bg-slate-950/40'">
                <input
                  type="file"
                  id="calendarFileInput"
                  accept=".ics"
                  (change)="onCalendarFileSelected($event)"
                  class="absolute inset-0 w-full h-full opacity-0 cursor-pointer" />
                <div class="flex flex-col items-center">
                  <svg class="w-8 h-8 mb-2" [ngClass]="calendarFile ? 'text-amber-400' : 'text-slate-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                  </svg>
                  @if (calendarFile) {
                    <p class="text-xs font-semibold text-amber-300">{{ calendarFile.name }}</p>
                    <p class="text-xs text-slate-400">{{ (calendarFile.size / 1024).toFixed(1) }} KB</p>
                  } @else {
                    <p class="text-xs font-semibold text-slate-300">Seleccionar archivo .ics exportado</p>
                  }
                </div>
              </div>

              <button
                (click)="submitCalendarIngestion()"
                [disabled]="!calendarFile || isIngestingCalendar"
                class="w-full py-2.5 px-4 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-bold text-xs shadow-md transition-all flex items-center justify-center gap-2 disabled:opacity-40">
                @if (isIngestingCalendar) {
                  <span>Parseando eventos del calendario...</span>
                } @else {
                  <span>PROCESAR CALENDARIO (.ICS)</span>
                }
              </button>

              @if (calendarResult) {
                <div class="p-4 rounded-xl bg-slate-950/90 border border-amber-500/30 text-xs space-y-3">
                  <div class="flex justify-between items-center text-slate-300">
                    <span>Eventos Parseados:</span>
                    <strong class="text-amber-400 font-mono text-sm">{{ calendarResult.total_events_parsed }}</strong>
                  </div>
                  <div class="flex justify-between items-center text-slate-300">
                    <span>Horas Ocupadas Totales:</span>
                    <strong class="text-white font-mono">{{ calendarResult.busy_metrics.total_busy_hours }} hrs</strong>
                  </div>
                  <div class="flex justify-between items-center text-slate-300">
                    <span>Horas Tesis Dedicadas:</span>
                    <strong class="text-emerald-400 font-mono">{{ calendarResult.busy_metrics.thesis_hours_total }} hrs</strong>
                  </div>
                </div>
              }
            </div>
          </div>

          <!-- GITHUB TELEMETRY -->
          <div class="rounded-2xl bg-slate-900/80 border border-slate-800 p-6 backdrop-blur-xl shadow-xl">
            <div class="flex items-center justify-between pb-4 border-b border-slate-800">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-400 font-bold">
                  GH
                </div>
                <div>
                  <h2 class="text-base font-bold text-white">3. Telemetría GitHub Events</h2>
                  <p class="text-xs text-slate-300">Commits y ritmo nocturno en tiempo real</p>
                </div>
              </div>
              <span class="text-xs font-mono text-sky-400 px-2 py-0.5 rounded bg-sky-950/60 border border-sky-800/50">
                POST /ingest/github
              </span>
            </div>

            <div class="mt-4 space-y-4">
              <div>
                <label class="block text-xs font-medium text-slate-300 mb-1">Usuario Público de GitHub</label>
                <div class="flex gap-2">
                  <input
                    type="text"
                    [(ngModel)]="githubUsername"
                    placeholder="Ej. torvalds o tu usuario"
                    class="flex-1 px-3 py-2 rounded-lg bg-slate-950 border border-slate-700 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-sky-500" />
                  <button
                    (click)="submitGitHubIngestion()"
                    [disabled]="!githubUsername || isIngestingGitHub"
                    class="px-4 py-2 rounded-lg bg-sky-600 hover:bg-sky-500 text-white font-bold text-xs shadow-md disabled:opacity-40 transition-colors">
                    @if (isIngestingGitHub) {
                      <span>Consultando...</span>
                    } @else {
                      <span>CONSULTAR</span>
                    }
                  </button>
                </div>
              </div>

              @if (githubResult) {
                <div class="p-4 rounded-xl bg-slate-950/90 border border-sky-500/30 text-xs space-y-3">
                  <div class="flex justify-between items-center text-slate-300">
                    <span>Usuario:</span>
                    <strong class="text-sky-300 font-mono">{{ githubResult.username }}</strong>
                  </div>
                  <div class="flex justify-between items-center text-slate-300">
                    <span>Commits Recientes:</span>
                    <strong class="text-white font-mono text-sm">{{ githubResult.github_metrics.total_commits }}</strong>
                  </div>
                  <div class="flex justify-between items-center text-slate-300">
                    <span>Commits de Tesis:</span>
                    <strong class="text-emerald-400 font-mono">{{ githubResult.github_metrics.thesis_commits_count }}</strong>
                  </div>
                  <div class="flex justify-between items-center text-slate-300">
                    <span>% Nocturno (10pm-6am):</span>
                    <strong class="text-amber-400 font-mono">{{ githubResult.github_metrics.nocturnal_commits_pct }}%</strong>
                  </div>
                </div>
              }
            </div>
          </div>
        </div>
      </div>
    </div>
  `
})
export class RealIngestionPanelComponent {
  readonly drJefService = inject(DrJefService);
  private readonly apiService = inject(DrJefApiService);

  // Form inputs
  whatsappFile: File | null = null;
  contactName: string = '';
  userName: string = 'Tú';
  relationshipType: string = 'FRIEND';
  closenessLevel: number = 0.8;
  anonymizeLocally: boolean = true;
  anonymizedNote: string | null = null;

  calendarFile: File | null = null;
  githubUsername: string = 'octocat';

  // Loading states
  isIngestingWhatsApp = false;
  isIngestingCalendar = false;
  isIngestingGitHub = false;
  isSyncingTelemetry = false;
  isPurgingData = false;

  // Results
  whatsappResult: IngestWhatsAppResponse | null = null;
  whatsappError: string | null = null;
  calendarResult: IngestCalendarResponse | null = null;
  githubResult: IngestGitHubResponse | null = null;
  syncResponse: SyncTelemetryResponse | null = null;
  purgeSuccessMessage: string | null = null;

  async onWhatsAppFileSelected(event: Event): Promise<void> {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      const file = input.files[0];
      this.whatsappError = null;
      this.anonymizedNote = null;

      if (!this.contactName) {
        // Infiere del nombre del archivo si contiene "Chat de WhatsApp con XYZ.txt"
        const fname = file.name;
        const match = fname.match(/Chat de WhatsApp con (.+?)(\.txt|\.zip)/i);
        if (match && match[1]) {
          this.contactName = match[1].trim();
        }
      }

      if (this.anonymizeLocally && file.name.endsWith('.txt')) {
        try {
          const rawText = await file.text();
          const phoneRegex = /(\+?\d{1,4}[\s-]?)?(\(?\d{2,4}\)?[\s-]?)?\d{3,4}[\s-]?\d{3,4}/g;
          const emailRegex = /[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+/g;
          const sanitizedText = rawText
            .replace(phoneRegex, '[DATO_ANONIMIZADO]')
            .replace(emailRegex, '[DATO_ANONIMIZADO]');
          this.whatsappFile = new File([sanitizedText], file.name, { type: 'text/plain' });
          this.anonymizedNote = 'Archivo anonimizado en tu navegador (teléfonos y correos ocultados antes del envío).';
        } catch (e) {
          console.warn('No se pudo sanitizar localmente, usando archivo original', e);
          this.whatsappFile = file;
        }
      } else {
        this.whatsappFile = file;
      }
    }
  }

  purgeAllUserData(): void {
    if (!confirm('Are you sure you want to permanently erase all episode data, contacts, and telemetry? This action is irreversible.')) {
      return;
    }
    this.isPurgingData = true;
    this.purgeSuccessMessage = null;
    this.apiService.purgeUserData().subscribe({
      next: (res) => {
        this.isPurgingData = false;
        this.purgeSuccessMessage = res.message || 'All your saved data has been successfully erased.';
        this.whatsappResult = null;
        this.calendarResult = null;
        this.githubResult = null;
        this.syncResponse = null;
        this.whatsappFile = null;
        this.calendarFile = null;
        this.anonymizedNote = null;
      },
      error: (err) => {
        this.isPurgingData = false;
        alert('Error purging data: ' + (err?.error?.detail || err?.message || 'Unknown error'));
      }
    });
  }

  onCalendarFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.calendarFile = input.files[0];
    }
  }

  submitWhatsAppIngestion(): void {
    if (!this.whatsappFile) return;

    this.isIngestingWhatsApp = true;
    this.whatsappError = null;

    this.apiService.ingestWhatsApp(
      this.whatsappFile,
      this.relationshipType,
      this.closenessLevel,
      this.userName,
      this.contactName ? this.contactName : undefined
    ).subscribe({
      next: (res) => {
        this.whatsappResult = res;
        this.isIngestingWhatsApp = false;
      },
      error: (err) => {
        this.whatsappError = err?.error?.detail || err?.message || 'Unexpected error during ingestion.';
        this.isIngestingWhatsApp = false;
      }
    });
  }

  submitCalendarIngestion(): void {
    if (!this.calendarFile) return;

    this.isIngestingCalendar = true;
    this.apiService.ingestCalendarIcs(this.calendarFile).subscribe({
      next: (res) => {
        this.calendarResult = res;
        this.isIngestingCalendar = false;
      },
      error: (err) => {
        console.error('Error al ingestar calendario', err);
        this.isIngestingCalendar = false;
      }
    });
  }

  submitGitHubIngestion(): void {
    if (!this.githubUsername) return;

    this.isIngestingGitHub = true;
    this.apiService.ingestGitHub(this.githubUsername).subscribe({
      next: (res) => {
        this.githubResult = res;
        this.isIngestingGitHub = false;
      },
      error: (err) => {
        console.error('Error al consultar GitHub', err);
        this.isIngestingGitHub = false;
      }
    });
  }

  syncAllTelemetry(): void {
    this.isSyncingTelemetry = true;
    this.apiService.syncUserTelemetry(
      'Primary Researcher',
      this.userName || 'User',
      'PhD in AI / Advanced Career Track',
      this.githubUsername,
      this.calendarFile
    ).subscribe({
      next: (res) => {
        this.syncResponse = res;
        this.isSyncingTelemetry = false;
      },
      error: (err) => {
        console.error('Error sincronizando telemetría', err);
        this.isSyncingTelemetry = false;
      }
    });
  }
}
