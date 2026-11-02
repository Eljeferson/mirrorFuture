import { Component, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MirrorFutureService } from '../../core/services/mirror-future.service';
import { FutureSelfOracleV4Component } from '../future-oracle-v4/future-self-oracle-v4.component';

interface EditorialContent {
  logoTitle: string;
  logoSubtitle: string;
  navHome: string;
  navExplore: string;
  navContact: string;
  reality: string;
  paragraph: string;
  leftWord: string;
  rightWord: string;
  ctaButton: string;
  stampText: string;
  verticalText: string;
  bottomSubtitle: string;
  bottomNumber: string;
  modalTitle: string;
  modalP1: string;
  modalP2: string;
  modalP3: string;
  modalClose: string;
  contactTitle: string;
  contactSubtitle: string;
  contactP1: string;
  contactEmail: string;
  contactNote: string;
  contactClose: string;
}

const DICTIONARY: Record<'EN' | 'ES', EditorialContent> = {
  EN: {
    logoTitle: 'MIRROR',
    logoSubtitle: 'Future • Career & Income',
    navHome: 'Home',
    navExplore: 'Career Oracle',
    navContact: 'Contact',
    reality: 'CAREER & FUTURE',
    paragraph: 'The first causal career intelligence oracle: autocompletes your professional trajectory and income via Life2Vec, matches active job openings in your city, and prescribes a verified daily roadmap to reach your long-term goals.',
    leftWord: 'c a r e',
    rightWord: 'e r',
    ctaButton: 'PREDICT MY CAREER FUTURE',
    stampText: 'LIFE2VEC / SALARIES',
    verticalText: 'TRANSITIONS',
    bottomSubtitle: 'Actuarial labor forecasting & verified roadmap',
    bottomNumber: '01',
    modalTitle: 'CAUSAL CAREER & SALARY ARCHITECTURE',
    modalP1: 'Mirror Future leverages a Life2Vec sequential architecture to tokenize your education and career timeline, calculating empirical salary transition probabilities across verified peer cohorts with your exact starting profile.',
    modalP2: 'It performs 384d semantic vector matching against active job openings and public tenders in your city or remote portals, pinpointing missing requirements, actuarial time-to-hire curves (Cox/Weibull survival models), and real take-home net income.',
    modalP3: 'It constructs a 4-phase Strategic Roadmap (Month 1, Months 2-6, Year 1, and Years 3-5) detailing daily habits to shift, concrete milestones to pursue, and critical traps to avoid to unlock rapid hiring, salary escalation, or global remote work.',
    modalClose: 'CLOSE ARCHITECTURE',
    contactTitle: 'CONTACT & RESEARCH',
    contactSubtitle: 'Causal AI Lab & Quantitative Labor Economics',
    contactP1: 'For inquiries regarding causal career modeling, actuarial labor calibration, or quantitative research collaborations, contact our dispatch desk.',
    contactEmail: 'contact@mirrorfuture.ai',
    contactNote: 'Response latency is governed by stochastic scheduling. Inquiries are processed within 24 hours.',
    contactClose: 'CLOSE'
  },
  ES: {
    logoTitle: 'MIRROR',
    logoSubtitle: 'Future • Carrera & Salarios',
    navHome: 'Inicio',
    navExplore: 'Oráculo Laboral',
    navContact: 'Contacto',
    reality: 'CARRERA & FUTURO',
    paragraph: 'El primer oráculo de inteligencia laboral y causal: autocompleta tu trayectoria y salario con Life2Vec, audita vacantes reales abiertas hoy en tu ciudad y prescribe la guía paso a paso de hábitos diarios para alcanzar tus metas e ideales.',
    leftWord: 'f u t u',
    rightWord: 'r o',
    ctaButton: 'PREDECIR MI FUTURO LABORAL',
    stampText: 'LIFE2VEC / SALARIOS',
    verticalText: 'TRANSICIONES',
    bottomSubtitle: 'Predicción actuarial y laboral verificable',
    bottomNumber: '01',
    modalTitle: 'ARQUITECTURA DE PREDICCIÓN LABORAL & CAUSAL',
    modalP1: 'Mirror Future applies the Life2Vec sequential architecture de Life2Vec para tratar tu historial de vida, estudios y trabajo como una secuencia de eventos tokenizados, calculando probabilidades estadísticas de transición salarial frente a cohortes reales con tu mismo perfil y punto de partida.',
    modalP2: 'Realiza matching vectorial (384d) contra ofertas de empleo y convocatorias reales abiertas hoy en tu ciudad y portales remotos, identificando requisitos excluyentes faltantes, tiempos actuariales de contratación (Supervivencia de Cox/Weibull) y sueldo líquido de bolsillo.',
    modalP3: 'Construye una Hoja de Ruta Estratégica en 4 fases (Mes 1, Meses 2-6, Año 1 y Años 3-5) con los hábitos diarios que debes cambiar en tu rutina, los hitos concretos a seguir y las trampas críticas a evitar para consolidar tu inserción, aceleración salarial o trabajo en el exterior.',
    modalClose: 'CERRAR ARQUITECTURA',
    contactTitle: 'CONTACTO & INVESTIGACIÓN',
    contactSubtitle: 'Laboratorio de Inteligencia Causal & Economía Cuantitativa',
    contactP1: 'Para consultas sobre modelos causales, calibración actuarial de mercado o colaboraciones de investigación cuantitativa, contáctanos a través de nuestro despacho.',
    contactEmail: 'contact@mirrorfuture.ai',
    contactNote: 'La latencia de respuesta se rige por despacho estocástico. Las solicitudes se procesan en menos de 24 horas.',
    contactClose: 'CERRAR'
  }
};

@Component({
  selector: 'app-mirror-future-landing',
  standalone: true,
  imports: [CommonModule, FutureSelfOracleV4Component],
  template: `
    <!-- 1. CERO SCROLL Y LIENZO EDITORIAL (100vh x 100vw) -->
    <div
      class="relative w-screen h-screen overflow-hidden select-none bg-gradient-to-br from-[#EAEAEA] via-[#E2E2E2] to-[#D6D6D6] font-sans text-neutral-900">

      <!-- ==================== TOP EDITORIAL BAR ==================== -->
      <header class="absolute top-0 inset-x-0 h-20 px-8 sm:px-12 lg:px-16 flex items-center justify-between z-30 pointer-events-auto">
        <!-- Logo (Arriba Izquierda con tipografía idéntica a FEX Faces) -->
        <div class="flex flex-col select-none cursor-pointer font-brand" (click)="goHome()">
          <span class="font-normal text-2xl sm:text-[27px] text-[#1A1A1A] leading-none tracking-tight">
            {{ t().logoTitle }}
          </span>
          <span class="font-normal text-xs sm:text-[13px] text-[#737373] leading-none mt-1 tracking-normal">
            {{ t().logoSubtitle }}
          </span>
        </div>

        <!-- Menú Superior Derecha + Selector Minimalista [ EN / ES ] -->
        <nav aria-label="Menú editorial superior" class="flex items-center gap-6 sm:gap-10 text-xs font-semibold tracking-[0.2em] uppercase text-neutral-600">
          <button
            type="button"
            (click)="goHome()"
            class="hover:text-black transition-colors cursor-pointer pb-0.5">
            {{ t().navHome }}
          </button>
          <button
            type="button"
            (click)="openExplore()"
            class="hover:text-black transition-colors cursor-pointer pb-0.5">
            {{ t().navExplore }}
          </button>
          <button
            type="button"
            (click)="openContact()"
            class="hover:text-black transition-colors cursor-pointer pb-0.5">
            {{ t().navContact }}
          </button>

          <!-- Selector de Idiomas Reactivo Minimalista [ EN / ES ] -->
          <div class="flex items-center text-xs font-mono tracking-widest pl-2">
            <span class="text-neutral-400 mr-1">[</span>
            <button
              type="button"
              (click)="setLang('EN')"
              [class.text-neutral-950]="drJefService.language() === 'EN'"
              [class.font-black]="drJefService.language() === 'EN'"
              [class.text-neutral-400]="drJefService.language() !== 'EN'"
              class="hover:text-black transition-colors cursor-pointer px-0.5">
              EN
            </button>
            <span class="text-neutral-400 mx-1">/</span>
            <button
              type="button"
              (click)="setLang('ES')"
              [class.text-neutral-950]="drJefService.language() === 'ES'"
              [class.font-black]="drJefService.language() === 'ES'"
              [class.text-neutral-400]="drJefService.language() !== 'ES'"
              class="hover:text-black transition-colors cursor-pointer px-0.5">
              ES
            </button>
            <span class="text-neutral-400 ml-1">]</span>
          </div>
        </nav>
      </header>

      <!-- ==================== BLOQUE EDITORIAL IZQUIERDO ==================== -->
      <!-- Título Blanco + Eco Contorneado Completo + Párrafo (Ubicado estrictamente ARRIBA de las letras gigantes) -->
      <section
        aria-label="Manifiesto Causal"
        class="absolute top-24 sm:top-28 lg:top-32 left-8 sm:left-12 lg:left-16 z-30 max-w-sm select-none pointer-events-auto">
        <div class="relative inline-block select-none font-brand">
          <h1 class="text-3xl sm:text-4xl lg:text-[46px] font-bold tracking-[0.16em] text-white uppercase leading-none">
            {{ t().reality }}
          </h1>
          <!-- Eco contorneado mostrando un poco más de la mitad, tomada desde abajo -->
          <div
            class="text-3xl sm:text-4xl lg:text-[46px] font-bold tracking-[0.16em] uppercase leading-none select-none text-outline-white pointer-events-none reality-outline-bottom">
            {{ t().reality }}
          </div>
        </div>

        <p class="text-xs sm:text-[13px] leading-relaxed text-neutral-700 max-w-[340px] font-normal pt-4 tracking-wide font-sans select-text">
          "{{ t().paragraph }}"
        </p>
      </section>

      <!-- ==================== 3. ESCULTURA CENTRAL SURREALISTA (3D REAL) ==================== -->
      <!-- Escultura fotorrealista 3D de alta definición, cayendo desde top: 0 -->
      <div
        class="absolute left-1/2 -translate-x-1/2 top-0 h-[86vh] sm:h-[88vh] z-20 pointer-events-none flex justify-center">
        <img
          src="/sculpture-3d-clean.png"
          alt="Mirror Future 3D Sculpture"
          class="h-full w-auto object-contain filter drop-shadow-[0_20px_22px_rgba(0,0,0,0.24)]" />
      </div>

      <!-- ==================== PALABRA GIGANTE CENTRAL DIVIDIDA ==================== -->
      <!-- 'r e f l' (izq) y 'c t i o n' (der) o 'p r o y' (izq) y 'c c i ó n' (der) -->
      <!-- Proporción editorial exacta, peso Regular (font-normal), #0F0F0F, top: 52% -->
      
      <!-- Mitad Izquierda de la Palabra Gigante (a la izquierda de la escultura) -->
      <div
        class="absolute top-[52%] -translate-y-1/2 right-[50%] mr-12 sm:mr-16 md:mr-20 lg:mr-24 text-right pointer-events-none z-10 whitespace-nowrap leading-none select-none">
        <span
          style="font-size: clamp(3.8rem, 6.2vw, 6.6rem); letter-spacing: 0.22em; font-family: 'Inter', sans-serif;"
          class="font-normal text-[#0F0F0F] inline-block">
          {{ t().leftWord }}
        </span>
      </div>

      <!-- Mitad Derecha de la Palabra Gigante (a la derecha de la escultura, sin tocar HORIZONS) -->
      <div
        class="absolute top-[52%] -translate-y-1/2 left-[50%] ml-12 sm:ml-16 md:mr-20 lg:ml-24 text-left pointer-events-none z-10 whitespace-nowrap leading-none select-none">
        <span
          style="font-size: clamp(3.8rem, 6.2vw, 6.6rem); letter-spacing: 0.22em; font-family: 'Inter', sans-serif;"
          class="font-normal text-[#0F0F0F] inline-block">
          {{ t().rightWord }}
        </span>
      </div>

      <!-- ==================== BOTÓN PRINCIPAL ==================== -->
      <!-- Ubicado debajo de las letras gigantes izquierdas, forma de píldora limpia sin flecha -->
      <div class="absolute top-[68%] left-8 sm:left-12 lg:left-16 z-30 pointer-events-auto">
        <button
          type="button"
          (click)="openSimulator()"
          class="border border-neutral-800 rounded-full px-10 py-3.5 text-xs font-bold tracking-[0.2em] uppercase text-neutral-900 hover:bg-neutral-900 hover:text-white transition-all shadow-sm active:scale-95 cursor-pointer">
          {{ t().ctaButton }}
        </button>
      </div>

      <!-- ==================== SELLO INFERIOR IZQUIERDO ==================== -->
      <!-- Con línea diagonal fina blanca divisoria / y reflejo contorneado debajo -->
      <div class="absolute bottom-8 sm:bottom-10 left-8 sm:left-12 lg:left-16 z-30 select-none pointer-events-none">
        <div class="relative inline-block">
          <div class="relative flex items-center">
            <span class="text-2xl sm:text-3xl font-bold tracking-wider text-white uppercase leading-none">
              {{ t().stampText }}
            </span>
            <!-- Línea diagonal divisoria fina blanca cruzando el texto a 45 grados -->
            <div class="w-24 h-[1.5px] bg-white -rotate-45 absolute -left-2 top-1/2 pointer-events-none origin-center shadow-sm"></div>
          </div>
          <!-- Eco en contorno blanco transparente -->
          <div
            class="text-2xl sm:text-3xl font-bold tracking-wider uppercase leading-none select-none text-outline-white -mt-0.5">
            {{ t().stampText }}
          </div>
        </div>
      </div>

      <!-- ==================== TEXTO VERTICAL DERECHO ==================== -->
      <!-- Pegado al margen derecho, rotado -90deg, con eco en contorno blanco -->
      <aside
        aria-label="Orientación editorial"
        class="absolute right-6 sm:right-8 lg:right-10 top-1/2 -translate-y-1/2 z-30 select-none pointer-events-none">
        <div class="flex items-center gap-2.5 transform -rotate-90 origin-center whitespace-nowrap">
          <span class="text-2xl sm:text-3xl font-bold tracking-[0.25em] text-white uppercase leading-none">
            {{ t().verticalText }}
          </span>
          <span
            class="text-2xl sm:text-3xl font-bold tracking-[0.25em] uppercase leading-none text-outline-white">
            {{ t().verticalText }}
          </span>
        </div>
      </aside>

      <!-- ==================== BLOQUE INFERIOR DERECHO ==================== -->
      <!-- Subtítulo + Número Grande Contorneado (01) en Sans-Serif Fina Ultraligera -->
      <div class="absolute bottom-8 sm:bottom-10 right-8 sm:right-12 lg:right-16 z-30 select-none text-right pointer-events-none">
        <span class="text-base sm:text-lg font-medium text-neutral-800 tracking-wide block mb-1">
          {{ t().bottomSubtitle }}
        </span>
        <span
          class="text-7xl sm:text-8xl font-extralight text-right leading-none block font-sans text-outline-black">
          {{ t().bottomNumber }}
        </span>
      </div>

      <!-- ==================== MODAL DE CONTACTO EDITORIAL ==================== -->
      @if (showContact()) {
        <div
          class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-black/60 backdrop-blur-md transition-all duration-300 pointer-events-auto"
          (click)="closeContact()">
          <div
            class="max-w-md w-full bg-[#EAEAEB] border border-black/15 rounded-3xl p-6 sm:p-8 shadow-2xl space-y-6 text-zinc-900 animate-in fade-in zoom-in-95 duration-200"
            (click)="$event.stopPropagation()">
            <div class="flex items-center justify-between pb-3 border-b border-black/10">
              <div class="flex items-center gap-2">
                <span class="w-2.5 h-2.5 rounded-full bg-[#FF5500]"></span>
                <span class="text-xs font-mono font-bold tracking-widest uppercase text-black">
                  MIRROR FUTURE &bull; {{ drJefService.language() === 'EN' ? 'CONTACT' : 'CONTACTO' }}
                </span>
              </div>
              <button
                type="button"
                (click)="closeContact()"
                class="w-8 h-8 rounded-full border border-black/10 bg-white hover:bg-black hover:text-white flex items-center justify-center text-xs font-bold transition-all cursor-pointer">
                ✕
              </button>
            </div>

            <div>
              <h2 class="text-2xl font-black tracking-tight text-neutral-900 uppercase">
                {{ t().contactTitle }}
              </h2>
              <p class="text-xs text-neutral-500 font-mono mt-1">
                {{ t().contactSubtitle }}
              </p>
            </div>

            <div class="space-y-4 text-xs sm:text-sm text-neutral-700 leading-relaxed">
              <p>{{ t().contactP1 }}</p>

              <div class="bg-white/80 border border-black/10 rounded-2xl p-4 space-y-1.5">
                <div class="text-[10px] font-mono uppercase tracking-wider text-neutral-500 font-semibold">
                  {{ drJefService.language() === 'EN' ? 'Direct Dispatch Channel' : 'Canal Directo de Despacho' }}
                </div>
                <a
                  href="mailto:contact@mirrorfuture.ai"
                  class="text-sm font-bold text-neutral-900 hover:text-[#FF5500] transition-colors block font-mono">
                  {{ t().contactEmail }}
                </a>
              </div>

              <p class="text-xs text-neutral-500">
                {{ t().contactNote }}
              </p>
            </div>

            <div class="pt-4 border-t border-black/10 flex items-center justify-end">
              <button
                type="button"
                (click)="closeContact()"
                class="px-6 py-2.5 rounded-full bg-neutral-900 text-white text-xs font-bold tracking-widest uppercase hover:bg-black transition-all cursor-pointer">
                {{ t().contactClose }}
              </button>
            </div>
          </div>
        </div>
      }

      <!-- ==================== MODAL DE METODOLOGÍA CAUSAL ==================== -->
      @if (showMethodology()) {
        <div
          class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-black/60 backdrop-blur-md transition-all duration-300 pointer-events-auto">
          <div
            class="max-w-xl w-full bg-[#EAEAEB] border border-black/15 rounded-3xl p-6 sm:p-8 shadow-2xl space-y-6 text-zinc-900 animate-in fade-in zoom-in-95 duration-200">
            <div class="flex items-center justify-between pb-3 border-b border-black/10">
              <div class="flex items-center gap-2">
                <span class="w-2.5 h-2.5 rounded-full bg-[#FF5500]"></span>
                <span class="text-xs font-mono font-bold tracking-widest uppercase text-black">
                  MIRROR FUTURE &bull; LIFE2VEC & SCM
                </span>
              </div>
              <button
                type="button"
                (click)="closeMethodology()"
                class="w-8 h-8 rounded-full border border-black/10 bg-white hover:bg-black hover:text-white flex items-center justify-center text-xs font-bold transition-all cursor-pointer">
                ✕
              </button>
            </div>

            <div>
              <h2 class="text-2xl font-black tracking-tight text-neutral-900 uppercase">
                {{ t().modalTitle }}
              </h2>
              <p class="text-xs text-neutral-500 font-mono mt-1">
                {{ drJefService.language() === 'EN' ? 'Life2Vec Sequential Transitions • 384d Job Vector Matching • Cox Survival Model' : 'Transiciones Secuenciales Life2Vec • Matching Vectorial 384d • Modelo de Supervivencia de Cox' }}
              </p>
            </div>

            <div class="space-y-4 text-xs sm:text-sm text-neutral-700 leading-relaxed">
              <p>{{ t().modalP1 }}</p>
              <p>{{ t().modalP2 }}</p>
              <p>{{ t().modalP3 }}</p>
            </div>

            <div class="pt-4 border-t border-black/10 flex items-center justify-end">
              <button
                type="button"
                (click)="closeMethodology()"
                class="px-6 py-2.5 rounded-full bg-neutral-900 text-white text-xs font-bold tracking-widest uppercase hover:bg-black transition-all cursor-pointer">
                {{ t().modalClose }}
              </button>
            </div>
          </div>
        </div>
      }

      <!-- ==================== 4. CONEXIÓN CON EL MOTOR DE SIMULACIÓN ==================== -->
      <!-- Despliegue con transición suave del panel del Oráculo (FutureSelfOracleV4Component) -->
      @if (showOracle()) {
        <div
          class="fixed inset-0 z-50 overflow-y-auto bg-[#EAEAEB] transition-opacity duration-300 pointer-events-auto">
          <app-future-self-oracle-v4 (closeOracle)="closeSimulator()"></app-future-self-oracle-v4>
        </div>
      }

    </div>
  `
})
export class MirrorFutureLandingComponent {
  private readonly router = inject(Router);
  readonly mirrorFutureService = inject(MirrorFutureService);
  readonly drJefService = this.mirrorFutureService;

  readonly showOracle = signal<boolean>(false);
  readonly showMethodology = signal<boolean>(false);
  readonly showContact = signal<boolean>(false);

  // Contenido editorial reactivo sincronizado con el idioma seleccionado
  readonly t = computed(() => {
    const lang = this.drJefService.language();
    return DICTIONARY[lang] || DICTIONARY.EN;
  });

  setLang(lang: 'EN' | 'ES'): void {
    this.drJefService.setLanguage(lang);
  }

  goHome(): void {
    this.showOracle.set(false);
    this.showMethodology.set(false);
    this.showContact.set(false);
  }

  openSimulator(): void {
    this.showContact.set(false);
    this.showMethodology.set(false);
    this.showOracle.set(true);
  }

  openExplore(): void {
    this.openSimulator();
  }

  closeSimulator(): void {
    this.showOracle.set(false);
  }

  openContact(): void {
    this.showOracle.set(false);
    this.showMethodology.set(false);
    this.showContact.set(true);
  }

  closeContact(): void {
    this.showContact.set(false);
  }

  openMethodology(): void {
    this.showContact.set(false);
    this.showMethodology.set(true);
  }

  closeMethodology(): void {
    this.showMethodology.set(false);
  }
}
