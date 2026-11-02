import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive, Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';
import { MirrorFutureService } from './core/services/mirror-future.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive],
  template: `
    <div
      [class.w-screen]="isLandingPage()"
      [class.h-screen]="isLandingPage()"
      [class.overflow-hidden]="isLandingPage()"
      [class.min-h-screen]="!isLandingPage()"
      [class.flex]="!isLandingPage()"
      [class.flex-col]="!isLandingPage()"
      class="bg-[#EAEAEB] text-zinc-900 font-sans selection:bg-[#FF5500] selection:text-white transition-colors duration-200">
      
      <!-- Top Navigation Bar (Visible across application views, excluded from full-screen landing) -->
      @if (!isLandingPage()) {
        <header class="sticky top-0 z-50 bg-[#EAEAEB]/90 backdrop-blur-xl border-b border-black/10">
          <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex items-center justify-between h-16 gap-3">
              
              <!-- Brand Identity: MIRROR FUTURE -->
              <div class="flex items-center gap-3 shrink-0">
                <a routerLink="/" class="flex items-center gap-2.5 group">
                  <div class="w-9 h-9 rounded-xl bg-black text-white flex items-center justify-center font-black text-sm shadow-sm group-hover:bg-[#FF5500] transition-colors">
                    MF
                  </div>
                  <div class="font-brand">
                    <div class="flex items-center gap-2">
                      <span class="font-normal text-lg tracking-tight text-[#1A1A1A]">MIRROR FUTURE</span>
                      <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-[#FF5500]/15 text-[#FF5500] border border-[#FF5500]/30 font-bold">
                        V4 CAUSAL
                      </span>
                    </div>
                    <p class="text-[10px] text-zinc-500 font-normal">
                      {{ mirrorFutureService.language() === 'EN' ? 'Career & Income Intelligence • Life2Vec' : 'Career & Income Intelligence • Life2Vec' }}
                    </p>
                  </div>
                </a>
              </div>

              <!-- Navigation Links -->
              <nav class="hidden lg:flex items-center gap-1 bg-white/80 p-1.5 rounded-2xl border border-black/10 shadow-sm backdrop-blur-md">
                <a
                  routerLink="/oracle"
                  routerLinkActive="bg-black text-white shadow-sm"
                  class="px-3.5 py-1.5 rounded-xl text-xs font-bold text-zinc-700 hover:text-black transition-all flex items-center gap-1.5">
                  <span class="w-2 h-2 rounded-full bg-[#FF5500]"></span>
                  {{ mirrorFutureService.language() === 'EN' ? 'Career Oracle' : 'Career Oracle' }}
                </a>

                <a
                  routerLink="/ingestion"
                  routerLinkActive="bg-black text-white shadow-sm"
                  class="px-3.5 py-1.5 rounded-xl text-xs font-semibold text-zinc-600 hover:text-black transition-all flex items-center gap-1.5">
                  <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                  {{ mirrorFutureService.language() === 'EN' ? 'Forensic Ingestion' : 'Forensic Ingestion' }}
                </a>

                <a
                  routerLink="/twins-forensics"
                  routerLinkActive="bg-black text-white shadow-sm"
                  class="px-3.5 py-1.5 rounded-xl text-xs font-semibold text-zinc-600 hover:text-black transition-all flex items-center gap-1.5">
                  <span class="w-1.5 h-1.5 rounded-full bg-violet-500"></span>
                  {{ mirrorFutureService.language() === 'EN' ? 'Vision & Twins' : 'Vision & Twins' }}
                </a>

                <a
                  routerLink="/actuators-oracle"
                  routerLinkActive="bg-black text-white shadow-sm"
                  class="px-3.5 py-1.5 rounded-xl text-xs font-semibold text-zinc-600 hover:text-black transition-all flex items-center gap-1.5">
                  <span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
                  {{ mirrorFutureService.language() === 'EN' ? 'ICS Actuators' : 'ICS Actuators' }}
                </a>

                <a
                  routerLink="/multiverse-3d"
                  routerLinkActive="bg-black text-white shadow-sm"
                  class="px-3.5 py-1.5 rounded-xl text-xs font-semibold text-zinc-600 hover:text-black transition-all flex items-center gap-1.5">
                  <span class="w-1.5 h-1.5 rounded-full bg-cyan-500"></span>
                  {{ mirrorFutureService.language() === 'EN' ? '3D Multiverse' : '3D Multiverse' }}
                </a>
              </nav>

              <!-- Actions: Language Selector & API Status -->
              <div class="flex items-center gap-2 shrink-0">
                <!-- Language Selector [ EN / ES ] -->
                <div class="flex items-center gap-1 bg-white px-2.5 py-1 rounded-xl border border-black/10 shadow-xs text-xs font-mono">
                  <button
                    type="button"
                    (click)="mirrorFutureService.setLanguage('EN')"
                    [class.font-black]="mirrorFutureService.language() === 'EN'"
                    [class.text-black]="mirrorFutureService.language() === 'EN'"
                    [class.text-zinc-400]="mirrorFutureService.language() !== 'EN'"
                    class="hover:text-black transition-colors cursor-pointer px-1">
                    EN
                  </button>
                  <span class="text-zinc-300">/</span>
                  <button
                    type="button"
                    (click)="mirrorFutureService.setLanguage('ES')"
                    [class.font-black]="mirrorFutureService.language() === 'ES'"
                    [class.text-black]="mirrorFutureService.language() === 'ES'"
                    [class.text-zinc-400]="mirrorFutureService.language() !== 'ES'"
                    class="hover:text-black transition-colors cursor-pointer px-1">
                    ES
                  </button>
                </div>

                <div class="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white border border-black/10 text-xs shadow-sm">
                  <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                  <span class="text-zinc-700 font-mono text-[11px] font-semibold">
                    Causal Engine :8000
                  </span>
                </div>
              </div>
            </div>

            <!-- Mobile Navigation Sub-bar -->
            <div class="flex lg:hidden items-center justify-around py-2 border-t border-black/10 text-xs overflow-x-auto gap-2">
              <a routerLink="/oracle" routerLinkActive="bg-black text-white rounded-lg px-2.5 font-bold" class="text-zinc-700 py-1 whitespace-nowrap">
                🔮 Oracle
              </a>
              <a routerLink="/ingestion" routerLinkActive="bg-black text-white rounded-lg px-2.5 font-bold" class="text-zinc-600 py-1 whitespace-nowrap">
                Ingestion
              </a>
              <a routerLink="/twins-forensics" routerLinkActive="bg-black text-white rounded-lg px-2.5 font-bold" class="text-zinc-600 py-1 whitespace-nowrap">
                Twins
              </a>
              <a routerLink="/actuators-oracle" routerLinkActive="bg-black text-white rounded-lg px-2.5 font-bold" class="text-zinc-600 py-1 whitespace-nowrap">
                Actuators
              </a>
              <a routerLink="/multiverse-3d" routerLinkActive="bg-black text-white rounded-lg px-2.5 font-bold" class="text-zinc-600 py-1 whitespace-nowrap">
                3D
              </a>
            </div>
          </div>
        </header>
      }

      <!-- Main Content Area -->
      <main [class.flex-1]="!isLandingPage()" [class.py-4]="!isLandingPage()" [class.md:py-6]="!isLandingPage()" [class.w-full]="isLandingPage()" [class.h-full]="isLandingPage()" [class.overflow-hidden]="isLandingPage()">
        <router-outlet></router-outlet>
      </main>

      <!-- Footer -->
      @if (!isLandingPage()) {
        <footer class="border-t border-black/10 bg-[#E2E2E5] py-8 text-center text-xs text-zinc-500">
          <div class="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
            <div class="flex items-center gap-2">
              <span class="text-black font-bold">MIRROR FUTURE &bull; Faces of Destiny</span>
              <span>&bull;</span>
              <span class="text-zinc-600 font-mono">
                Stochastic Simulation NumPy + Meta Llama 3.3 (70B)
              </span>
            </div>
            <div class="text-[11px] text-zinc-500">
              Causal Physics • 1 Month, 6 Months, 1 Year • Zero Mysticism, 100% Empirical
            </div>
          </div>
        </footer>
      }
    </div>
  `
})
export class AppComponent {
  private readonly router = inject(Router);
  readonly mirrorFutureService = inject(MirrorFutureService);
  // Alias for backward compatibility with templates
  readonly drJefService = this.mirrorFutureService;
  title = 'Mirror Future';
  readonly isLanding = signal<boolean>(true);

  constructor() {
    this.router.events.pipe(
      filter((e): e is NavigationEnd => e instanceof NavigationEnd)
    ).subscribe((event) => {
      const path = (event.urlAfterRedirects || event.url).split('?')[0].split('#')[0];
      this.isLanding.set(path === '/' || path === '');
    });
  }

  isLandingPage(): boolean {
    const raw = this.router.url.split('?')[0].split('#')[0];
    return raw === '/' || raw === '';
  }
}
