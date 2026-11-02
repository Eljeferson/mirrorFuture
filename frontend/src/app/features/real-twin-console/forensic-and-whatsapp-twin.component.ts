import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MirrorFutureApiService } from '../../core/services/mirror-future-api.service';
import { MirrorFutureService } from '../../core/services/mirror-future.service';
import {
  ImageForensicReport,
  MultiTwinSimulationResult,
  SocialTwinPrediction
} from '../../core/models/mirror-future.model';

@Component({
  selector: 'app-forensic-and-whatsapp-twin',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="space-y-8 max-w-7xl mx-auto p-4 md:p-6">
      <!-- Header Banner -->
      <div class="relative overflow-hidden rounded-2xl bg-gradient-to-r from-indigo-950/80 via-slate-900 to-slate-950 border border-indigo-500/20 p-6 md:p-8 backdrop-blur-xl shadow-2xl">
        <div class="absolute -top-24 -right-24 w-80 h-80 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
          <div>
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-semibold uppercase tracking-wider mb-3">
              <span class="w-2 h-2 rounded-full bg-indigo-400"></span>
              EXIF Metadata + Llama 3.2 Vision • WhatsApp Social Simulation
            </div>
            <h1 class="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
              Image Analysis & Social Twins
            </h1>
            <p class="text-slate-300 mt-2 text-sm md:text-base max-w-3xl leading-relaxed">
              Evaluate reputational risks in images with EXIF metadata and computer vision, and preview the simulated communicative style of your contacts backed by empirical evidence.
            </p>
          </div>

          <!-- Data Purge Button -->
          <button
            (click)="purgeAllUserData()"
            [disabled]="isPurgingData"
            class="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-red-950/60 hover:bg-red-900/80 border border-red-500/40 text-red-200 font-semibold text-xs transition-all active:scale-95 disabled:opacity-50"
            title="Permanently erase all your stored data">
            @if (isPurgingData) {
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

      <!-- Privacy & Consent Notice Banner -->
      <div class="rounded-xl bg-slate-900/90 border border-indigo-500/30 p-4 text-slate-200 flex items-center justify-between gap-4 backdrop-blur-md">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-lg bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400 shrink-0">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <div class="text-xs md:text-sm">
            <span class="font-bold text-white">Protected Privacy:</span>
            <span class="text-slate-300 ml-1">You can anonymize names and phone numbers locally in your browser before analysis, and purge all data with a single click.</span>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <!-- LEFT COLUMN (Col 1-5): EXIF Forensics + Vision -->
        <div class="lg:col-span-5 space-y-6">
          <div class="rounded-2xl bg-slate-900/80 border border-slate-800 p-6 backdrop-blur-xl shadow-xl space-y-5">
            <div class="flex items-center justify-between border-b border-slate-800 pb-3">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center text-violet-400 font-bold">
                  📷
                </div>
                <div>
                  <h2 class="text-base font-bold text-white">Image Analysis & Privacy</h2>
                  <p class="text-xs text-slate-300">EXIF Metadata + Llama 3.2 (11B) Computer Vision</p>
                </div>
              </div>
              <span class="text-xs font-mono text-violet-400 px-2 py-0.5 rounded bg-violet-950/60 border border-violet-800/50">
                POST /vision-forensics
              </span>
            </div>

            <!-- Upload Area & Image Preview -->
            <div class="relative border-2 border-dashed rounded-xl p-4 text-center transition-all overflow-hidden"
                 [ngClass]="imageFile ? 'border-violet-500/50 bg-violet-950/10' : 'border-slate-700 bg-slate-950/40'">
              <input
                type="file"
                id="forensicFileInput"
                accept="image/*"
                (change)="onImageFileSelected($event)"
                class="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-20" />
              
              @if (imagePreviewUrl) {
                <div class="flex flex-col items-center">
                  <div class="relative max-h-56 rounded-lg overflow-hidden border border-slate-700 shadow-md">
                    <img [src]="imagePreviewUrl" alt="Uploaded photo for analysis" class="object-cover max-h-56 w-auto" />
                    <div class="absolute bottom-2 left-2 px-2 py-1 bg-slate-950/80 rounded text-xs text-violet-300 font-mono">
                      {{ imageFile?.name }}
                    </div>
                  </div>
                  <p class="text-xs text-slate-300 mt-2">Click or drag another image to replace</p>
                </div>
              } @else {
                <div class="flex flex-col items-center py-6">
                  <svg class="w-12 h-12 text-slate-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                  </svg>
                  <p class="text-sm font-semibold text-slate-200">Upload photo for privacy & reputational assessment</p>
                  <p class="text-xs text-slate-400 mt-1">(e.g., Profile photo to assess social impact)</p>
                </div>
              }
            </div>

            <!-- Context Claim Input -->
            <div>
              <label class="block text-xs font-medium text-slate-300 mb-1">
                Context or message accompanying the photo:
              </label>
              <textarea
                [(ngModel)]="contextClaim"
                rows="2"
                placeholder="e.g. Profile photo showing late night work at 2:00 AM..."
                class="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-700 text-white placeholder-slate-500 text-xs focus:outline-none focus:border-violet-500 resize-none"></textarea>
            </div>

            <!-- Button: Execute Vision Forensics -->
            <button
              (click)="executeVisionForensics()"
              [disabled]="!imageFile || isAnalyzingVision"
              class="w-full py-3 px-4 rounded-xl bg-violet-600 hover:bg-violet-500 active:bg-violet-700 text-white font-bold text-xs shadow-lg shadow-violet-950/50 transition-all flex items-center justify-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed">
              @if (isAnalyzingVision) {
                <svg class="animate-spin h-4 w-4 text-white" viewBox="0 0 24 24" fill="none">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                </svg>
                <span>Analyzing metadata and visual content...</span>
              } @else {
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
                </svg>
                <span>EVALUATE PHOTO IMPACT</span>
              }
            </button>

            @if (visionError) {
              <div class="p-3 rounded-lg bg-red-950/60 border border-red-500/40 text-red-300 text-xs">
                {{ visionError }}
              </div>
            }

            <!-- IMAGE FORENSIC REPORT -->
            @if (forensicReport) {
              <div class="rounded-xl bg-slate-950/90 border border-violet-500/30 p-5 space-y-4">
                <div class="flex items-center justify-between border-b border-slate-800 pb-2">
                  <span class="text-xs font-bold text-violet-400 uppercase tracking-wider">Image Analysis Report</span>
                  <span class="text-xs font-mono text-slate-400">{{ forensicReport.analyzed_at | date:'short' }}</span>
                </div>

                <!-- Scores: Reputational Risk & Privacy Risk -->
                <div class="grid grid-cols-2 gap-3">
                  <div class="p-3 rounded-lg bg-slate-900 border"
                       [ngClass]="getRiskBorderClass(forensicReport.vision.reputational_risk_score)">
                    <span class="text-xs block font-medium"
                          [ngClass]="getRiskTextClass(forensicReport.vision.reputational_risk_score)">
                      Reputational Risk
                    </span>
                    <div class="text-xl font-mono font-bold mt-0.5"
                         [ngClass]="getRiskTextClass(forensicReport.vision.reputational_risk_score)">
                      {{ (forensicReport.vision.reputational_risk_score * 100).toFixed(0) }}%
                    </div>
                    <div class="w-full bg-slate-800 h-1.5 rounded-full mt-1.5 overflow-hidden">
                      <div class="h-full rounded-full transition-all duration-500"
                           [ngClass]="getRiskBgClass(forensicReport.vision.reputational_risk_score)"
                           [style.width.%]="forensicReport.vision.reputational_risk_score * 100"></div>
                    </div>
                  </div>

                  <div class="p-3 rounded-lg bg-slate-900 border border-slate-800">
                    <span class="text-xs block font-medium text-slate-300">Privacy Risk</span>
                    <div class="text-xl font-mono font-bold text-white mt-0.5">
                      {{ (forensicReport.vision.privacy_risk_score * 100).toFixed(0) }}%
                    </div>
                    <div class="w-full bg-slate-800 h-1.5 rounded-full mt-1.5 overflow-hidden">
                      <div class="h-full bg-cyan-500 rounded-full transition-all duration-500"
                           [style.width.%]="forensicReport.vision.privacy_risk_score * 100"></div>
                    </div>
                  </div>
                </div>

                <!-- Scene Description -->
                <div>
                  <h4 class="text-xs font-bold text-slate-300 uppercase tracking-wider mb-1">Scene Description:</h4>
                  <p class="text-xs text-slate-200 bg-slate-900/90 p-3 rounded-lg border border-slate-800 max-w-prose leading-relaxed">
                    {{ forensicReport.vision.scene_description }}
                  </p>
                </div>

                <!-- Camera & EXIF Data -->
                <div class="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-xs space-y-1.5">
                  <div class="flex justify-between">
                    <span class="text-slate-300">Camera / Device:</span>
                    <span class="text-slate-200 font-mono">{{ forensicReport.exif.device_make || 'Generic' }} {{ forensicReport.exif.device_model || '' }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-slate-300">Resolution:</span>
                    <span class="text-slate-200 font-mono">{{ forensicReport.exif.image_width }} x {{ forensicReport.exif.image_height }} px</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-slate-300">GPS / Coordinates:</span>
                    @if (forensicReport.exif.gps.has_gps) {
                      <a [href]="forensicReport.exif.gps.maps_url" target="_blank" class="text-cyan-400 underline font-mono text-xs">
                        {{ forensicReport.exif.gps.latitude }}, {{ forensicReport.exif.gps.longitude }} 📍
                      </a>
                    } @else {
                      <span class="text-slate-400 font-mono">No physical GPS metadata</span>
                    }
                  </div>
                  @if (forensicReport.exif.timestamp) {
                    <div class="flex justify-between">
                      <span class="text-slate-300">EXIF Timestamp:</span>
                      <span class="text-slate-200 font-mono text-xs">{{ forensicReport.exif.timestamp }}</span>
                    </div>
                  }
                </div>

                <!-- Causal Recommendation -->
                <div class="p-3 rounded-lg bg-gradient-to-r from-violet-950/60 to-slate-900 border border-violet-500/40">
                  <span class="text-xs font-bold uppercase tracking-wider text-violet-300 block mb-1">
                    Preventive Recommendation:
                  </span>
                  <p class="text-xs font-semibold text-white max-w-prose leading-relaxed">
                    {{ forensicReport.vision.causal_recommendation }}
                  </p>
                </div>
              </div>
            }
          </div>
        </div>

        <!-- RIGHT COLUMN (Col 6-12): WhatsApp Twin Simulator (RAG + Llama 3.3 70B) -->
        <div class="lg:col-span-7 space-y-6">
          <div class="rounded-2xl bg-slate-900/80 border border-slate-800 p-6 backdrop-blur-xl shadow-xl space-y-5">
            <div class="flex items-center justify-between border-b border-slate-800 pb-3">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 font-bold">
                  💬
                </div>
                <div>
                  <h2 class="text-base font-bold text-white">Social Reaction Simulator</h2>
                  <p class="text-xs text-slate-300">Response pattern simulation via Llama 3.3 70B</p>
                </div>
              </div>
              <span class="text-xs font-mono text-emerald-400 px-2 py-0.5 rounded bg-emerald-950/60 border border-emerald-800/50">
                POST /social-twin/simulate
              </span>
            </div>

            <!-- Mandatory Ethical Notice -->
            <div class="p-3.5 rounded-xl bg-amber-950/30 border border-amber-500/30 text-amber-200 text-xs flex items-start gap-2.5">
              <svg class="w-5 h-5 text-amber-400 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div class="leading-relaxed">
                <strong class="text-amber-300">Ethical Notice:</strong>
                <span class="text-slate-200 ml-1">Simulated responses are statistical estimates of communication style and do not represent actual thoughts of third parties.</span>
              </div>
            </div>

            <!-- Action Input -->
            <div>
              <label class="block text-xs font-medium text-slate-300 mb-1">
                Action or Message to Test Against Real Contacts
              </label>
              <div class="flex flex-col sm:flex-row gap-2">
                <input
                  type="text"
                  [(ngModel)]="actionClaim"
                  placeholder="e.g. Uploading profile photo working late at 2 AM on the thesis..."
                  class="flex-1 px-4 py-3 rounded-xl bg-slate-950 border border-slate-700 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-emerald-500 transition-colors" />
                <button
                  (click)="simulateSocialTwins()"
                  [disabled]="!actionClaim || isSimulatingTwins"
                  class="px-5 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 active:bg-emerald-700 text-white font-bold text-xs shadow-lg shadow-emerald-950/50 transition-all flex items-center justify-center gap-2 disabled:opacity-40 whitespace-nowrap">
                  @if (isSimulatingTwins) {
                    <svg class="animate-spin h-4 w-4 text-white" viewBox="0 0 24 24" fill="none">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                    </svg>
                    <span>Simulating reactions...</span>
                  } @else {
                    <span>SIMULATE SOCIAL REACTIONS</span>
                  }
                </button>
              </div>
            </div>

            @if (twinError) {
              <div class="p-3 rounded-lg bg-red-950/60 border border-red-500/40 text-red-300 text-xs">
                {{ twinError }}
              </div>
            }

            <!-- SIMULATION RESULTS: WHATSAPP CLONE FEED -->
            @if (twinResult) {
              <!-- Impact Header Summary -->
              <div class="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
                <div class="flex flex-wrap items-center justify-between gap-2">
                  <div class="flex items-center gap-2">
                    <span class="text-xs text-slate-300">Net Relational Impact:</span>
                    <span class="font-mono font-bold text-sm"
                          [ngClass]="twinResult.net_relational_impact_score >= 0 ? 'text-emerald-400' : 'text-rose-400'">
                      {{ twinResult.net_relational_impact_score > 0 ? '+' : '' }}{{ twinResult.net_relational_impact_score.toFixed(2) }}
                    </span>
                  </div>
                  <div class="text-xs text-slate-300">
                    Simulated Contacts: <strong class="text-white">{{ twinResult.simulated_contacts.length }}</strong>
                  </div>
                </div>

                @if (twinResult.strategic_advice) {
                  <div class="p-3 rounded-lg bg-emerald-950/20 border border-emerald-500/30 text-xs text-emerald-200 max-w-prose leading-relaxed">
                    <strong class="text-emerald-300">Mirror Future Strategic Advice:</strong> {{ twinResult.strategic_advice }}
                  </div>
                }

                @if (twinResult.high_risk_alerts && twinResult.high_risk_alerts.length > 0) {
                  <div class="p-3 rounded-lg bg-rose-950/30 border border-rose-500/30 text-xs text-rose-300 space-y-1">
                    <strong class="text-rose-400">Detected Attention Warnings:</strong>
                    <ul class="list-disc list-inside">
                      @for (alert of twinResult.high_risk_alerts; track $index) {
                        <li>{{ alert }}</li>
                      }
                    </ul>
                  </div>
                }
              </div>

              <!-- WHATSAPP CLONE FEED -->
              <div class="space-y-4">
                <h3 class="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                  <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
                  Estimated WhatsApp Reactions (Likely Style and Idioms)
                </h3>

                @for (contact of twinResult.simulated_contacts; track contact.contact_id) {
                  <!-- Contact Card with WhatsApp style -->
                  <div class="rounded-xl border border-slate-800 bg-[#0b141a] overflow-hidden shadow-xl transition-all">
                    <!-- WhatsApp Contact Header -->
                    <div class="bg-[#202c33] px-4 py-3 flex items-center justify-between border-b border-[#2a3942]">
                      <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-full bg-[#00a884]/20 border border-[#00a884]/40 flex items-center justify-center text-[#00a884] font-bold text-sm">
                          {{ getInitials(contact.contact_name) }}
                        </div>
                        <div>
                          <div class="flex items-center gap-2">
                            <h4 class="font-bold text-white text-sm">{{ contact.contact_name }}</h4>
                            <span class="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-200 font-medium">
                              {{ contact.relationship_type }}
                            </span>
                          </div>
                          <p class="text-xs text-slate-300 flex items-center gap-1">
                            <span>Estimated response latency:</span>
                            <strong class="text-[#00a884] font-mono">~{{ contact.estimated_response_minutes }} min</strong>
                          </p>
                        </div>
                      </div>

                      <!-- Emotional Reaction Pill -->
                      <span class="px-2.5 py-1 rounded-full text-xs font-semibold border"
                            [ngClass]="getEmotionClass(contact.emotional_reaction)">
                        {{ contact.emotional_reaction }}
                      </span>
                    </div>

                    <!-- WhatsApp Chat Area -->
                    <div class="p-4 bg-[#0b141a] space-y-3"
                         style="background-image: radial-gradient(rgba(255,255,255,0.03) 1px, transparent 1px); background-size: 16px 16px;">
                       <!-- Incoming Message Bubble -->
                      <div class="flex items-start max-w-[85%]">
                        <div class="rounded-2xl rounded-tl-none bg-[#202c33] text-[#e9edef] px-4 py-2.5 shadow-md border border-[#2a3942]/60 relative">
                          <p class="text-sm leading-relaxed whitespace-pre-wrap select-text max-w-prose">
                            {{ contact.predicted_message }}
                          </p>
                          <div class="flex items-center justify-end gap-1 mt-1 text-xs text-slate-300">
                            <span>{{ contact.estimated_response_minutes }}m later</span>
                            <svg class="w-3.5 h-3.5 text-[#53bdeb]" viewBox="0 0 16 15" fill="none">
                              <path d="M15.01 3.316l-7.79 7.79-3.92-3.92.707-.707 3.213 3.213 7.083-7.083.707.707z" fill="currentColor"/>
                              <path d="M11.01 3.316l-7.79 7.79-3.213-3.213.707-.707 2.506 2.506 7.083-7.083.707.707z" fill="currentColor"/>
                            </svg>
                          </div>
                        </div>
                      </div>

                      <!-- Causal Rationale Text -->
                      <div class="text-xs text-slate-200 bg-slate-900/60 p-2.5 rounded-lg border border-slate-800 max-w-prose leading-relaxed">
                        <span class="text-amber-400 font-semibold">Estimated Rationale:</span> {{ contact.causal_rationale }}
                      </div>

                      <!-- ACCORDION: HISTORICAL EVIDENCE (RAG) -->
                      <div class="pt-1">
                        <button
                          (click)="toggleAccordion(contact.contact_id)"
                          class="w-full flex items-center justify-between px-3 py-2 rounded-lg bg-slate-900/90 hover:bg-slate-800/90 border border-slate-800 text-xs font-semibold text-emerald-400 transition-colors">
                          <span class="flex items-center gap-1.5">
                            <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                            </svg>
                            VIEW RECORDED HISTORICAL EVIDENCE
                            <span class="ml-1 text-xs px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-800">
                              {{ contact.historical_evidence ? contact.historical_evidence.length : 0 }} quotes
                            </span>
                          </span>
                          <svg class="w-4 h-4 transition-transform duration-200"
                               [ngClass]="expandedContactIds.has(contact.contact_id) ? 'rotate-180 text-white' : 'text-slate-400'"
                               fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                          </svg>
                        </button>

                        @if (expandedContactIds.has(contact.contact_id)) {
                          <div class="mt-2 space-y-2 pl-2 border-l-2 border-emerald-500/40 animate-fadeIn">
                            @if (!contact.historical_evidence || contact.historical_evidence.length === 0) {
                              <p class="text-xs text-slate-400 italic p-2">No prior evidence cited for this episode.</p>
                            } @else {
                              @for (ev of contact.historical_evidence; track (ev.episode_id || $index)) {
                                <div class="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs space-y-1.5 max-w-prose leading-relaxed">
                                  <div class="flex items-center justify-between text-xs text-slate-300">
                                    <span class="font-mono text-emerald-400">Record: {{ ev.episode_id }}</span>
                                    @if (ev.historical_date) {
                                      <span class="font-mono text-slate-400">{{ ev.historical_date }}</span>
                                    }
                                  </div>
                                  <div class="text-slate-200 italic bg-slate-900/80 p-2 rounded border border-slate-800 font-mono text-xs leading-relaxed">
                                    "{{ ev.quoted_exchange }}"
                                  </div>
                                  <div class="text-xs text-slate-300">
                                    <strong class="text-slate-400">Observed pattern:</strong> {{ ev.behavioral_pattern_proven }}
                                  </div>
                                </div>
                              }
                            }
                          </div>
                        }
                      </div>
                    </div>
                  </div>
                }
              </div>
            }
          </div>
        </div>
      </div>
    </div>
  `
})
export class ForensicAndWhatsappTwinComponent {
  private readonly apiService = inject(MirrorFutureApiService);
  readonly mirrorFutureService = inject(MirrorFutureService);
  // Alias for backward-compatibility
  readonly drJefService = this.mirrorFutureService;

  // Vision inputs
  imageFile: File | null = null;
  imagePreviewUrl: string | null = null;
  contextClaim: string = 'Profile photo working late at 2:00 AM on the research thesis';

  // Twin inputs
  actionClaim: string = 'Upload profile photo working late at 2 AM saying I am working late';

  // States
  isAnalyzingVision = false;
  isSimulatingTwins = false;
  isPurgingData = false;
  visionError: string | null = null;
  twinError: string | null = null;

  // Results
  forensicReport: ImageForensicReport | null = null;
  twinResult: MultiTwinSimulationResult | null = null;

  // Accordion open/close tracker
  expandedContactIds = new Set<string>();

  purgeAllUserData(): void {
    if (!confirm('Are you sure you want to permanently erase all your stored data? This action is irreversible.')) {
      return;
    }
    this.isPurgingData = true;
    this.apiService.purgeUserData().subscribe({
      next: (res) => {
        this.isPurgingData = false;
        alert(res.message || 'All your stored data has been successfully deleted.');
        this.forensicReport = null;
        this.twinResult = null;
        this.imageFile = null;
        this.imagePreviewUrl = null;
        this.expandedContactIds.clear();
      },
      error: (err) => {
        this.isPurgingData = false;
        alert('Error purging data: ' + (err?.error?.detail || err?.message || 'Unknown error'));
      }
    });
  }

  onImageFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.imageFile = input.files[0];
      this.visionError = null;
      this.imagePreviewUrl = URL.createObjectURL(this.imageFile);
    }
  }

  executeVisionForensics(): void {
    if (!this.imageFile) return;

    this.isAnalyzingVision = true;
    this.visionError = null;

    this.apiService.analyzeVisionForensics(this.imageFile, this.contextClaim).subscribe({
      next: (report) => {
        this.forensicReport = report;
        this.isAnalyzingVision = false;
      },
      error: (err) => {
        this.visionError = err?.error?.detail || err?.message || 'Error in image forensic analysis.';
        this.isAnalyzingVision = false;
      }
    });
  }

  simulateSocialTwins(): void {
    if (!this.actionClaim) return;

    this.isSimulatingTwins = true;
    this.twinError = null;

    this.apiService.simulateSocialTwin(this.actionClaim).subscribe({
      next: (result) => {
        this.twinResult = result;
        this.mirrorFutureService.setSocialTwinResult(result);
        this.isSimulatingTwins = false;
        // Auto-expand the first contact's evidence by default
        if (result.simulated_contacts.length > 0) {
          this.expandedContactIds.add(result.simulated_contacts[0].contact_id);
        }
      },
      error: (err) => {
        this.twinError = err?.error?.detail || err?.message || 'Error simulating social twins.';
        this.isSimulatingTwins = false;
      }
    });
  }

  toggleAccordion(contactId: string): void {
    if (this.expandedContactIds.has(contactId)) {
      this.expandedContactIds.delete(contactId);
    } else {
      this.expandedContactIds.add(contactId);
    }
  }

  getInitials(name: string): string {
    if (!name) return '??';
    const parts = name.trim().split(/\s+/);
    if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
    return (parts[0][0] + parts[1][0]).toUpperCase();
  }

  getRiskBorderClass(risk: number): string {
    if (risk < 0.35) return 'border-emerald-500/40';
    if (risk < 0.70) return 'border-amber-500/40';
    return 'border-rose-500/50';
  }

  getRiskTextClass(risk: number): string {
    if (risk < 0.35) return 'text-emerald-400';
    if (risk < 0.70) return 'text-amber-400';
    return 'text-rose-400';
  }

  getRiskBgClass(risk: number): string {
    if (risk < 0.35) return 'bg-emerald-500';
    if (risk < 0.70) return 'bg-amber-500';
    return 'bg-rose-500';
  }

  getEmotionClass(emotion: string): string {
    const em = (emotion || '').toLowerCase();
    if (em.includes('orgullo') || em.includes('pride') || em.includes('apoyo') || em.includes('support') || em.includes('amor') || em.includes('love') || em.includes('felicidad') || em.includes('happy')) {
      return 'bg-emerald-950/80 text-emerald-300 border-emerald-600/40';
    }
    if (em.includes('indign') || em.includes('enojo') || em.includes('anger') || em.includes('molestia') || em.includes('upset') || em.includes('ira')) {
      return 'bg-rose-950/80 text-rose-300 border-rose-600/40';
    }
    if (em.includes('desconf') || em.includes('distrust') || em.includes('sospech') || em.includes('suspicio') || em.includes('duda') || em.includes('doubt')) {
      return 'bg-amber-950/80 text-amber-300 border-amber-600/40';
    }
    return 'bg-indigo-950/80 text-indigo-300 border-indigo-600/40';
  }
}
