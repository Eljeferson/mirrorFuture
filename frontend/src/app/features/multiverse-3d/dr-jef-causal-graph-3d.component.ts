import {
  Component,
  ElementRef,
  ViewChild,
  AfterViewInit,
  OnDestroy,
  HostListener,
  inject,
  input,
  output,
  effect,
  signal,
  computed,
  untracked,
  ChangeDetectionStrategy,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import * as THREE from 'three';
import {
  MonteCarloCurves,
  SocialTwinPrediction,
  TrajectoryPercentileBranch,
  TrajectoryPercentilePoint,
} from '../../core/models/dr-jef.model';
import { DrJefService } from '../../core/services/dr-jef.service';

interface ContactNode3D {
  mesh: THREE.Group;
  contact: SocialTwinPrediction;
  radialDistance: number;
  baseColor: THREE.Color;
  targetPos: THREE.Vector3;
}

@Component({
  selector: 'app-dr-jef-causal-graph-3d',
  standalone: true,
  imports: [CommonModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="relative w-full h-[640px] lg:h-[720px] bg-slate-950 rounded-2xl overflow-hidden border border-slate-800 shadow-2xl flex flex-col select-none font-sans">
      
      <!-- TOP HUD: Mirror Future Engine & Telemetry -->
      <div class="absolute top-0 left-0 right-0 z-20 flex flex-wrap items-center justify-between gap-3 px-5 py-3 bg-gradient-to-b from-slate-950/95 via-slate-950/80 to-transparent backdrop-blur-md border-b border-slate-800/60">
        <div class="flex items-center gap-3">
          <div class="relative flex items-center justify-center w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-400">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <span class="text-xs font-black tracking-widest uppercase text-amber-400 bg-amber-950/60 px-2 py-0.5 rounded border border-amber-500/30">
                MIRROR FUTURE ENGINE
              </span>
              <span class="text-xs text-slate-300 font-mono">Life Simulator</span>
            </div>
            <h1 class="text-sm md:text-base font-bold text-slate-100 tracking-tight">
              1,000 Life Projections × 180 Days
            </h1>
          </div>
        </div>

        <!-- Human Guide Legend Banner -->
        <div class="hidden xl:flex items-center gap-2 text-xs px-3 py-1.5 rounded-xl bg-slate-900/90 border border-slate-700/80 text-slate-300">
          <span class="text-amber-400 font-bold">Visual Guide:</span>
          <span>Green/Gold Line (Top) = Higher savings & energy | Red Line (Bottom) = Debt & exhaustion from lack of sleep</span>
        </div>

        <!-- Trajectory Branch Switcher -->
        <div class="flex items-center gap-1.5 bg-slate-900/90 p-1 rounded-xl border border-slate-800">
          <button
            type="button"
            (click)="toggleBranch('all')"
            [class]="branch() === 'all' ? 'bg-slate-700 text-white shadow-sm' : 'text-slate-300 hover:text-white'"
            class="px-2.5 py-1 text-xs font-semibold rounded-lg transition-all"
          >
            All
          </button>
          <button
            type="button"
            (click)="toggleBranch('p90')"
            [class]="branch() === 'p90' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' : 'text-slate-300 hover:text-amber-300'"
            class="px-2.5 py-1 text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5"
          >
            <span class="w-2 h-2 rounded-full bg-[#F59E0B]"></span>
            Optimal Scenario
          </button>
          <button
            type="button"
            (click)="toggleBranch('p50')"
            [class]="branch() === 'p50' ? 'bg-blue-500/20 text-blue-300 border border-blue-500/40' : 'text-slate-300 hover:text-blue-300'"
            class="px-2.5 py-1 text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5"
          >
            <span class="w-2 h-2 rounded-full bg-[#3B82F6]"></span>
            Probable Scenario
          </button>
          <button
            type="button"
            (click)="toggleBranch('p10')"
            [class]="branch() === 'p10' ? 'bg-red-500/20 text-red-300 border border-red-500/40' : 'text-slate-300 hover:text-red-300'"
            class="px-2.5 py-1 text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5"
          >
            <span class="w-2 h-2 rounded-full bg-[#EF4444]"></span>
            Risk Scenario
          </button>
        </div>

        <!-- Camera Presets -->
        <div class="hidden sm:flex items-center gap-1 bg-slate-900/80 p-1 rounded-xl border border-slate-800">
          <button
            type="button"
            (click)="setCameraView('default')"
            class="px-2 py-1 text-xs text-slate-300 hover:bg-slate-800 rounded-md transition"
            title="Isometric Causal View"
          >
            Isometric
          </button>
          <button
            type="button"
            (click)="setCameraView('top')"
            class="px-2 py-1 text-xs text-slate-300 hover:bg-slate-800 rounded-md transition"
            title="Radial Contact Network"
          >
            Social Graph
          </button>
          <button
            type="button"
            (click)="setCameraView('side')"
            class="px-2 py-1 text-xs text-slate-300 hover:bg-slate-800 rounded-md transition"
            title="Time Evolution of Trajectories"
          >
            Trajectory
          </button>
          <button
            type="button"
            (click)="toggleAutoRotate()"
            [class]="isAutoRotating() ? 'text-amber-400 bg-amber-500/10' : 'text-slate-400 hover:bg-slate-800'"
            class="p-1 rounded-md transition"
            title="Toggle Auto-Rotation"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
      </div>

      <!-- WebGL Three.js Canvas Container -->
      <div #canvasContainer class="w-full flex-1 cursor-grab active:cursor-grabbing relative">
        <!-- Crosshair / Center Pointer Hint -->
        <div class="pointer-events-none absolute inset-0 flex items-center justify-center opacity-10">
          <div class="w-32 h-32 border border-slate-400 rounded-full"></div>
          <div class="w-64 h-64 border border-dashed border-slate-500 rounded-full"></div>
        </div>
      </div>

      <!-- BOTTOM OVERLAY: Leyenda de Ramas & Slider Temporal -->
      <div class="absolute bottom-0 left-0 right-0 z-20 p-4 bg-gradient-to-t from-slate-950/95 via-slate-950/80 to-transparent backdrop-blur-sm border-t border-slate-800/60 flex flex-col md:flex-row items-center justify-between gap-4">
        
        <!-- Interactive 180-Day Scrubber -->
        <div class="w-full md:w-80 flex items-center gap-3 bg-slate-900/80 px-3 py-2 rounded-xl border border-slate-800">
          <span class="text-xs font-mono font-bold text-amber-400 whitespace-nowrap">Day {{ currentDay() }}</span>
          <input
            type="range"
            min="0"
            max="179"
            [value]="currentDay()"
            (input)="onDaySliderInput($event)"
            class="w-full accent-amber-500 bg-slate-700 h-1.5 rounded-lg cursor-pointer"
          />
          <span class="text-xs font-mono text-slate-500 whitespace-nowrap">180D</span>
        </div>

        <!-- Legend Badges -->
        <div class="flex flex-wrap items-center justify-center gap-2 text-xs">
          <div class="flex items-center gap-1.5 px-2.5 py-1 bg-amber-950/40 border border-amber-500/30 rounded-lg text-amber-300">
            <span class="w-2.5 h-2.5 rounded-full bg-[#F59E0B] shadow-[0_0_8px_#F59E0B]"></span>
            <span class="font-semibold">Optimal Scenario:</span>
            <span>Maximum progress & goals achieved</span>
          </div>

          <div class="flex items-center gap-1.5 px-2.5 py-1 bg-blue-950/40 border border-blue-500/30 rounded-lg text-blue-300">
            <span class="w-2.5 h-2.5 rounded-full bg-[#3B82F6] shadow-[0_0_8px_#3B82F6]"></span>
            <span class="font-semibold">Probable Scenario:</span>
            <span>At your current pace</span>
          </div>

          <div class="flex items-center gap-1.5 px-2.5 py-1 bg-red-950/40 border border-red-500/30 rounded-lg text-red-300">
            <span class="w-2.5 h-2.5 rounded-full bg-[#EF4444] shadow-[0_0_8px_#EF4444]"></span>
            <span class="font-semibold">Risk Scenario:</span>
            <span>Exhaustion if sleep & rest are neglected</span>
          </div>
        </div>

        <!-- Hint -->
        <div class="hidden lg:flex items-center gap-1.5 text-xs text-slate-300">
          <svg class="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122" />
          </svg>
          <span>Click any contact or node to inspect</span>
        </div>
      </div>

      <!-- SIDEBAR INSPECTOR: Detalle de Contacto o Hito Seleccionado -->
      @if (hoveredContact() || activeContact()) {
        @let c = activeContact() || hoveredContact();
        <div class="absolute top-20 right-4 z-30 w-80 md:w-96 max-h-[calc(100%-160px)] overflow-y-auto bg-slate-900/95 border border-slate-700/80 rounded-2xl p-4 shadow-2xl backdrop-blur-xl animate-in fade-in slide-in-from-right duration-200 text-slate-200">
          <div class="flex items-start justify-between gap-2 pb-3 border-b border-slate-800">
            <div>
              <div class="flex items-center gap-2">
                <span class="text-xs px-2 py-0.5 rounded font-mono font-semibold"
                  [ngClass]="{
                    'bg-red-500/20 text-red-400 border border-red-500/30': c?.emotional_reaction?.includes('Indignación') || c?.emotional_reaction?.includes('Desconfianza'),
                    'bg-amber-500/20 text-amber-400 border border-amber-500/30': c?.emotional_reaction?.includes('Expectativa') || c?.emotional_reaction?.includes('Presión'),
                    'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30': c?.emotional_reaction?.includes('Aprobación'),
                    'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30': c?.emotional_reaction?.includes('Apoyo') || c?.emotional_reaction?.includes('Sarcasmo')
                  }">
                  {{ c?.emotional_reaction }}
                </span>
                <span class="text-xs text-slate-300 uppercase tracking-wider">{{ c?.relationship_type }}</span>
              </div>
              <h2 class="text-base font-bold text-white mt-1">{{ c?.contact_name }}</h2>
            </div>
            <button
              type="button"
              (click)="clearActiveContact()"
              class="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800"
            >
              &times;
            </button>
          </div>

          <!-- Metricas de Distancia y Confianza -->
          <div class="grid grid-cols-2 gap-2 my-3 font-mono text-xs">
            <div class="p-2.5 rounded-xl bg-slate-800/60 border border-slate-700/50">
              <span class="text-slate-300 block text-xs uppercase font-medium">Response Latency</span>
              <span class="text-amber-400 font-bold text-sm">{{ c?.estimated_response_minutes }} min</span>
              <span class="text-xs text-slate-400 block">Radial Distance</span>
            </div>
            <div class="p-2.5 rounded-xl bg-slate-800/60 border border-slate-700/50">
              <span class="text-slate-300 block text-xs uppercase font-medium">Estimated Confidence</span>
              <span class="text-emerald-400 font-bold text-sm">{{ ((c?.confidence_score ?? 0) * 100).toFixed(0) }}%</span>
              <span class="text-xs text-slate-400 block">Color Saturation</span>
            </div>
          </div>

          <!-- Mensaje Predecido con estilo léxico -->
          <div class="mb-3">
            <span class="text-xs font-semibold text-slate-300 uppercase tracking-wider block mb-1">Predicted Response:</span>
            <div class="p-3 rounded-xl bg-slate-950/70 border border-slate-800 text-xs text-slate-200 italic max-w-prose leading-relaxed">
              "{{ c?.predicted_message }}"
            </div>
          </div>

          <!-- Razón Causal -->
          <div class="mb-3">
            <span class="text-xs font-semibold text-slate-300 uppercase tracking-wider block mb-1">Causal Diagnosis:</span>
            <p class="text-xs text-slate-200 max-w-prose leading-relaxed bg-slate-800/40 p-2.5 rounded-xl border border-slate-800">
              {{ c?.causal_rationale }}
            </p>
          </div>

          <!-- Citas de Evidencia Histórica -->
          @if (c?.historical_evidence && c!.historical_evidence.length > 0) {
            <div>
              <span class="text-xs font-semibold text-slate-300 uppercase tracking-wider block mb-1">Recorded Prior Evidence:</span>
              @for (ev of c!.historical_evidence; track (ev.episode_id || $index)) {
                <div class="p-2.5 bg-slate-950/50 rounded-lg border border-slate-800/80 text-xs space-y-1 mb-1.5 max-w-prose leading-relaxed">
                  <div class="text-amber-400/90 font-mono text-xs">Date: {{ ev.historical_date || 'Historical' }}</div>
                  <div class="text-slate-200">"{{ ev.quoted_exchange }}"</div>
                  <div class="text-slate-400 text-xs italic">&rarr; {{ ev.behavioral_pattern_proven }}</div>
                </div>
              }
            </div>
          }
        </div>
      }
    </div>
  `,
})
export class DrJefCausalGraph3dComponent implements AfterViewInit, OnDestroy {
  @ViewChild('canvasContainer', { static: true })
  private containerRef!: ElementRef<HTMLDivElement>;

  readonly drJefService = inject(DrJefService);

  // Inputs
  curves = input<MonteCarloCurves | null>(null);
  contacts = input<SocialTwinPrediction[]>([]);
  branch = input<TrajectoryPercentileBranch | 'all'>('all');
  selectedDay = input<number>(90);

  // Outputs
  contactSelected = output<SocialTwinPrediction | null>();
  branchSelected = output<TrajectoryPercentileBranch | 'all'>();
  dayChanged = output<number>();

  // State
  currentDay = signal<number>(90);
  hoveredContact = signal<SocialTwinPrediction | null>(null);
  activeContact = signal<SocialTwinPrediction | null>(null);
  isAutoRotating = signal<boolean>(false);

  // Three.js Core Objects
  private scene!: THREE.Scene;
  private camera!: THREE.PerspectiveCamera;
  private renderer!: THREE.WebGLRenderer;
  private animationFrameId: number | null = null;
  private timer = new THREE.Timer();

  // Three.js Groups
  private centralNodeGroup = new THREE.Group();
  private contactsGroup = new THREE.Group();
  private trajectoriesGroup = new THREE.Group();
  private gridGroup = new THREE.Group();
  private pulseParticlesGroup = new THREE.Group();

  // Internal Data Structure for 3D Interaction
  private contactNodesList: ContactNode3D[] = [];
  private interactiveMeshes: THREE.Object3D[] = [];
  private raycaster = new THREE.Raycaster();
  private mouse = new THREE.Vector2(-999, -999);

  // Camera Orbit Controls State
  private isMouseDown = false;
  private mousePreviousPosition = { x: 0, y: 0 };
  private cameraTarget = new THREE.Vector3(25, 0, 0);
  private cameraSpherical = { radius: 110, theta: THREE.MathUtils.degToRad(35), phi: THREE.MathUtils.degToRad(65) };

  constructor() {
    // React to inputs changes
    effect(() => {
      const c = this.curves();
      if (c && this.scene) {
        this.rebuildTrajectories(c);
      }
    });

    effect(() => {
      const list = this.contacts();
      if (list && this.scene) {
        this.rebuildContacts(list);
      }
    });

    effect(() => {
      const b = this.branch();
      if (this.scene) {
        this.updateBranchVisibility(b);
      }
    });

    effect(() => {
      const d = this.selectedDay();
      untracked(() => {
        this.currentDay.set(d);
      });
      this.updateDayMarker(d);
    }, { allowSignalWrites: true });
  }

  ngAfterViewInit(): void {
    this.initThree();
    this.createCausalOriginNode();
    this.createCosmicEnvironment();
    this.animate();

    // Trigger initial population from inputs or service
    if (this.curves()) {
      this.rebuildTrajectories(this.curves()!);
    }
    if (this.contacts().length > 0) {
      this.rebuildContacts(this.contacts());
    }

    this.setupPointerEvents();
  }

  ngOnDestroy(): void {
    if (this.animationFrameId !== null) {
      cancelAnimationFrame(this.animationFrameId);
    }
    this.timer?.dispose();
    this.renderer?.dispose();
  }

  // =========================================================================
  // Three.js Scene Setup & Initialization
  // =========================================================================

  private initThree(): void {
    const container = this.containerRef.nativeElement;
    const width = container.clientWidth || 800;
    const height = container.clientHeight || 600;

    // Scene
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x030712); // Tailwind slate-950
    this.scene.fog = new THREE.FogExp2(0x030712, 0.0035);

    // Camera
    this.camera = new THREE.PerspectiveCamera(50, width / height, 0.5, 1000);
    this.updateCameraFromSpherical();

    // Renderer
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.25;

    container.appendChild(this.renderer.domElement);

    // Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
    this.scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0xffeedd, 1.2);
    dirLight1.position.set(50, 80, 50);
    this.scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0x38bdf8, 0.8);
    dirLight2.position.set(-60, -40, -50);
    this.scene.add(dirLight2);

    // Add major groups to scene
    this.scene.add(this.centralNodeGroup);
    this.scene.add(this.contactsGroup);
    this.scene.add(this.trajectoriesGroup);
    this.scene.add(this.gridGroup);
    this.scene.add(this.pulseParticlesGroup);
  }

  // =========================================================================
  // 1. Nodo Central ('TÚ - AHORA')
  // =========================================================================

  private createCausalOriginNode(): void {
    this.centralNodeGroup.clear();

    // Core Glowing Sphere
    const coreGeom = new THREE.SphereGeometry(3.2, 32, 32);
    const coreMat = new THREE.MeshStandardMaterial({
      color: 0x38bdf8,
      emissive: 0x0284c7,
      emissiveIntensity: 1.2,
      roughness: 0.15,
      metalness: 0.8,
    });
    const coreMesh = new THREE.Mesh(coreGeom, coreMat);
    coreMesh.name = 'origin-core';
    this.centralNodeGroup.add(coreMesh);

    // Outer Wireframe Holographic Shell
    const shellGeom = new THREE.IcosahedronGeometry(4.4, 2);
    const shellMat = new THREE.MeshBasicMaterial({
      color: 0x7dd3fc,
      wireframe: true,
      transparent: true,
      opacity: 0.45,
    });
    const shellMesh = new THREE.Mesh(shellGeom, shellMat);
    shellMesh.name = 'origin-shell';
    this.centralNodeGroup.add(shellMesh);

    // Orbiting Ring
    const ringGeom = new THREE.RingGeometry(5.2, 5.6, 48);
    const ringMat = new THREE.MeshBasicMaterial({
      color: 0x38bdf8,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.6,
    });
    const ringMesh = new THREE.Mesh(ringGeom, ringMat);
    ringMesh.rotation.x = Math.PI / 2;
    ringMesh.name = 'origin-ring';
    this.centralNodeGroup.add(ringMesh);

    // 3D Sprite Label: "TÚ - AHORA"
    const labelSprite = this.createTextSprite('TÚ - AHORA', '#38BDF8', 12);
    labelSprite.position.set(0, 6.2, 0);
    this.centralNodeGroup.add(labelSprite);

    this.interactiveMeshes.push(coreMesh);
  }

  // =========================================================================
  // 2. Nodos de Contactos Reales (simulated_contacts)
  // Radial distance proportional to estimated_response_minutes
  // Color reflects emotional_reaction & confidence_score
  // =========================================================================

  private rebuildContacts(contactsList: SocialTwinPrediction[]): void {
    this.contactsGroup.clear();
    this.contactNodesList = [];
    // Keep only non-contact interactive meshes
    this.interactiveMeshes = this.interactiveMeshes.filter(m => m.name === 'origin-core');

    if (!contactsList || contactsList.length === 0) return;

    const count = contactsList.length;

    contactsList.forEach((c, idx) => {
      const group = new THREE.Group();

      // Radial distance proportional to latency (log-scaled to keep visualization compact and intuitive)
      // 10 min -> ~16 units, 45 min -> ~28 units, 180 min -> ~46 units, 240 min -> ~52 units
      const minMinutes = 5;
      const effectiveMinutes = Math.max(minMinutes, c.estimated_response_minutes);
      const radialDist = 14 + Math.log(effectiveMinutes / minMinutes + 1) * 9.5;

      // Angular distribution in the X-Z plane around origin
      const angle = (idx / count) * Math.PI * 2 + 0.35;
      const x = Math.cos(angle) * radialDist;
      const z = Math.sin(angle) * radialDist;
      // Slight vertical offset for organic multiverse clustering
      const y = Math.sin(idx * 1.8) * 4.5;

      const nodePos = new THREE.Vector3(x, y, z);
      group.position.copy(nodePos);

      // Color mapping from emotion & confidence score
      const colorHex = this.resolveReactionColor(c.emotional_reaction);
      const baseColor = new THREE.Color(colorHex);
      const emissiveIntensity = 0.4 + (c.confidence_score ?? 0.8) * 0.8;

      // Contact Sphere
      const sphereGeom = new THREE.SphereGeometry(2.2, 24, 24);
      const sphereMat = new THREE.MeshStandardMaterial({
        color: baseColor,
        emissive: baseColor,
        emissiveIntensity: emissiveIntensity,
        roughness: 0.25,
        metalness: 0.6,
      });
      const sphereMesh = new THREE.Mesh(sphereGeom, sphereMat);
      sphereMesh.name = `contact-mesh-${c.contact_id}`;
      (sphereMesh as any).userData = { contact: c };
      group.add(sphereMesh);
      this.interactiveMeshes.push(sphereMesh);

      // Glowing outer halo
      const haloGeom = new THREE.RingGeometry(2.6, 2.9, 32);
      const haloMat = new THREE.MeshBasicMaterial({
        color: baseColor,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.5,
      });
      const haloMesh = new THREE.Mesh(haloGeom, haloMat);
      haloMesh.lookAt(this.camera.position);
      group.add(haloMesh);

      // Text Sprite Label: Contact Name + Response Minutes
      const labelText = `${c.contact_name} (+${c.estimated_response_minutes}m)`;
      const sprite = this.createTextSprite(labelText, colorHex, 9);
      sprite.position.set(0, 3.8, 0);
      group.add(sprite);

      // Radial Connection Line to Origin ('TÚ - AHORA')
      const lineGeom = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0, 0, 0),
        nodePos,
      ]);
      const lineMat = new THREE.LineDashedMaterial({
        color: baseColor,
        dashSize: 1.5,
        gapSize: 0.8,
        transparent: true,
        opacity: 0.35,
      });
      const line = new THREE.Line(lineGeom, lineMat);
      line.computeLineDistances();
      this.contactsGroup.add(line);

      this.contactsGroup.add(group);
      this.contactNodesList.push({
        mesh: group,
        contact: c,
        radialDistance: radialDist,
        baseColor: baseColor,
        targetPos: nodePos,
      });
    });
  }

  // =========================================================================
  // 3. Render 3D de las 3 Ramas de Trayectoria Monte Carlo (curves)
  // P90: Golden Branch / Optimal Mirror Future Branch (#F59E0B)
  // P50: Probable Branch / Rama Probable (#3B82F6)
  // P10: Burnout Branch / Rama Roja Burnout (#EF4444)
  // =========================================================================

  private rebuildTrajectories(curves: MonteCarloCurves): void {
    this.trajectoriesGroup.clear();

    if (!curves || !curves.thesis_progress || curves.thesis_progress.length === 0) return;

    const daysCount = curves.thesis_progress.length;
    // Map 180 days along positive X axis (0 to ~90 units)
    const scaleX = 95 / daysCount;

    const pointsP90: THREE.Vector3[] = [];
    const pointsP50: THREE.Vector3[] = [];
    const pointsP10: THREE.Vector3[] = [];

    for (let i = 0; i < daysCount; i += 2) {
      const day = i;
      const thesis = curves.thesis_progress[day];
      const fatigue = curves.fatigue[day];
      const burnout = curves.burnout_risk[day];

      const x = day * scaleX;

      // P90: Golden Branch: High elevation in thesis units, controlled fatigue
      // Y represents net positive synthesis (Thesis progress / 15 - Fatigue / 10)
      const yP90 = (thesis.p90 / 12.0) - (fatigue.p10 / 18.0) + 2.0;
      const zP90 = -8.0 + Math.sin(day * 0.05) * 2.5;
      pointsP90.push(new THREE.Vector3(x, yP90, zP90));

      // P50: Probable Branch: Plateau around day 60-90
      const yP50 = (thesis.p50 / 14.0) - (fatigue.p50 / 12.0);
      const zP50 = 0.0 + Math.cos(day * 0.04) * 3.0;
      pointsP50.push(new THREE.Vector3(x, yP50, zP50));

      // P10: Burnout Branch: Severe dive downwards as burnout risk spikes
      const yP10 = (thesis.p10 / 18.0) - (fatigue.p90 / 8.0) - (burnout.p90 * 12.0);
      const zP10 = 10.0 + Math.sin(day * 0.06) * 4.0;
      pointsP10.push(new THREE.Vector3(x, yP10, zP10));
    }

    // 1. Build P90 Optimal Mirror Future Branch (#F59E0B)
    this.createBranchTube(pointsP90, 0xF59E0B, 'branch-p90', 0.9, 1.4);

    // 2. Build P50 Rama Probable (#3B82F6)
    this.createBranchTube(pointsP50, 0x3B82F6, 'branch-p50', 0.8, 1.1);

    // 3. Build P10 Rama Roja Burnout (#EF4444)
    this.createBranchTube(pointsP10, 0xEF4444, 'branch-p10', 0.85, 1.2);

    // Milestone Waypoint Markers
    this.createMilestoneMarker(48, pointsP50, 'Día 48: Zona de Estancamiento y Fatiga', '#3B82F6');
    this.createMilestoneMarker(120, pointsP90, 'Día 120: Hito de Avance y Aprobación (88%)', '#F59E0B');
    this.createMilestoneMarker(178, pointsP90, 'Día 180: Meta Cumplida', '#F59E0B');
    this.createMilestoneMarker(128, pointsP10, 'Día 128: Riesgo de Agotamiento Extremo', '#EF4444');
  }

  private createBranchTube(
    points: THREE.Vector3[],
    colorHex: number,
    name: string,
    opacity: number,
    radius: number
  ): void {
    if (points.length < 2) return;

    const curve = new THREE.CatmullRomCurve3(points);
    const tubeGeom = new THREE.TubeGeometry(curve, 120, radius, 12, false);
    const tubeMat = new THREE.MeshStandardMaterial({
      color: colorHex,
      emissive: colorHex,
      emissiveIntensity: 0.7,
      roughness: 0.2,
      metalness: 0.7,
      transparent: true,
      opacity: opacity,
    });
    const tubeMesh = new THREE.Mesh(tubeGeom, tubeMat);
    tubeMesh.name = name;
    this.trajectoriesGroup.add(tubeMesh);

    // Add glowing guide line in the center of the tube
    const linePoints = curve.getPoints(180);
    const lineGeom = new THREE.BufferGeometry().setFromPoints(linePoints);
    const lineMat = new THREE.LineBasicMaterial({
      color: 0xffffff,
      transparent: true,
      opacity: 0.65,
    });
    const centerLine = new THREE.Line(lineGeom, lineMat);
    centerLine.name = `${name}-core-line`;
    this.trajectoriesGroup.add(centerLine);
  }

  private createMilestoneMarker(
    dayIndex: number,
    trajectoryPoints: THREE.Vector3[],
    text: string,
    colorHex: string
  ): void {
    const ptIdx = Math.min(Math.floor(dayIndex / 2), trajectoryPoints.length - 1);
    if (ptIdx < 0) return;
    const pos = trajectoryPoints[ptIdx];

    const markerGroup = new THREE.Group();
    markerGroup.position.copy(pos);

    // Ring marker
    const ringGeom = new THREE.RingGeometry(1.4, 1.8, 24);
    const ringMat = new THREE.MeshBasicMaterial({
      color: new THREE.Color(colorHex),
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.85,
    });
    const ring = new THREE.Mesh(ringGeom, ringMat);
    ring.rotation.x = Math.PI / 2;
    markerGroup.add(ring);

    // Text Label Sprite
    const sprite = this.createTextSprite(text, colorHex, 9);
    sprite.position.set(0, 3.2, 0);
    markerGroup.add(sprite);

    this.trajectoriesGroup.add(markerGroup);
  }

  // =========================================================================
  // Scrubber & Day Indicator
  // =========================================================================

  private updateDayMarker(day: number): void {
    let marker = this.trajectoriesGroup.getObjectByName('current-day-marker') as THREE.Mesh;
    const scaleX = 95 / 180;
    const posX = day * scaleX;

    if (!marker) {
      const geom = new THREE.CylinderGeometry(0.3, 0.3, 40, 16);
      const mat = new THREE.MeshBasicMaterial({
        color: 0xf59e0b,
        transparent: true,
        opacity: 0.5,
      });
      marker = new THREE.Mesh(geom, mat);
      marker.name = 'current-day-marker';
      this.trajectoriesGroup.add(marker);
    }

    marker.position.set(posX, 0, 0);
  }

  // =========================================================================
  // Ambient Cosmic Environment & Reference Grid
  // =========================================================================

  private createCosmicEnvironment(): void {
    // Ground reference grid
    const grid = new THREE.GridHelper(180, 36, 0x1e293b, 0x0f172a);
    grid.position.y = -18;
    this.gridGroup.add(grid);

    // Starfield particles
    const particleCount = 700;
    const geom = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);

    for (let i = 0; i < particleCount; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 450;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 300;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 450;

      // Color variation: blues, ambers, whites
      const rnd = Math.random();
      if (rnd > 0.8) {
        colors[i * 3] = 0.96; colors[i * 3 + 1] = 0.62; colors[i * 3 + 2] = 0.04; // Amber
      } else if (rnd > 0.5) {
        colors[i * 3] = 0.23; colors[i * 3 + 1] = 0.51; colors[i * 3 + 2] = 0.96; // Blue
      } else {
        colors[i * 3] = 0.7; colors[i * 3 + 1] = 0.8; colors[i * 3 + 2] = 0.9;
      }
    }

    geom.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geom.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const mat = new THREE.PointsMaterial({
      size: 1.4,
      vertexColors: true,
      transparent: true,
      opacity: 0.65,
    });
    const starPoints = new THREE.Points(geom, mat);
    this.gridGroup.add(starPoints);
  }

  // =========================================================================
  // Render Loop & Animation
  // =========================================================================

  private animate = (timestamp?: number): void => {
    this.animationFrameId = requestAnimationFrame(this.animate);

    this.timer.update(timestamp);
    const delta = this.timer.getDelta();
    const elapsed = this.timer.getElapsed();

    // Rotate origin core and shell
    const shell = this.centralNodeGroup.getObjectByName('origin-shell');
    if (shell) {
      shell.rotation.y += delta * 0.45;
      shell.rotation.x += delta * 0.25;
    }

    const ring = this.centralNodeGroup.getObjectByName('origin-ring');
    if (ring) {
      ring.rotation.z += delta * 0.3;
    }

    // Auto-rotation if activated
    if (this.isAutoRotating()) {
      this.cameraSpherical.theta += delta * 0.25;
      this.updateCameraFromSpherical();
    }

    // Subtle breathing animation on contact nodes
    this.contactNodesList.forEach((cn, i) => {
      const bob = Math.sin(elapsed * 1.8 + i) * 0.08;
      cn.mesh.position.y = cn.targetPos.y + bob;
    });

    this.renderer.render(this.scene, this.camera);
  };

  // =========================================================================
  // User Interaction & Orbit Camera Controls
  // =========================================================================

  private setupPointerEvents(): void {
    const container = this.containerRef.nativeElement;

    container.addEventListener('mousedown', (e) => {
      this.isMouseDown = true;
      this.mousePreviousPosition = { x: e.clientX, y: e.clientY };
    });

    window.addEventListener('mouseup', () => {
      this.isMouseDown = false;
    });

    container.addEventListener('mousemove', (e) => {
      const rect = container.getBoundingClientRect();
      const currentX = e.clientX;
      const currentY = e.clientY;

      if (this.isMouseDown) {
        const deltaX = currentX - this.mousePreviousPosition.x;
        const deltaY = currentY - this.mousePreviousPosition.y;

        this.cameraSpherical.theta -= deltaX * 0.007;
        this.cameraSpherical.phi = Math.max(
          0.1,
          Math.min(Math.PI - 0.1, this.cameraSpherical.phi - deltaY * 0.007)
        );
        this.updateCameraFromSpherical();

        this.mousePreviousPosition = { x: currentX, y: currentY };
      }

      // Update normalized mouse coordinates for raycasting
      this.mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      this.mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

      this.checkIntersection();
    });

    container.addEventListener('wheel', (e) => {
      e.preventDefault();
      const zoomFactor = e.deltaY * 0.08;
      this.cameraSpherical.radius = Math.max(25, Math.min(260, this.cameraSpherical.radius + zoomFactor));
      this.updateCameraFromSpherical();
    }, { passive: false });

    container.addEventListener('click', () => {
      this.handleNodeClick();
    });
  }

  private updateCameraFromSpherical(): void {
    const { radius, theta, phi } = this.cameraSpherical;
    const x = this.cameraTarget.x + radius * Math.sin(phi) * Math.sin(theta);
    const y = this.cameraTarget.y + radius * Math.cos(phi);
    const z = this.cameraTarget.z + radius * Math.sin(phi) * Math.cos(theta);

    this.camera.position.set(x, y, z);
    this.camera.lookAt(this.cameraTarget);
  }

  private checkIntersection(): void {
    if (this.interactiveMeshes.length === 0) return;

    this.raycaster.setFromCamera(this.mouse, this.camera);
    const intersects = this.raycaster.intersectObjects(this.interactiveMeshes, false);

    if (intersects.length > 0) {
      const hit = intersects[0].object;
      const contact = (hit as any).userData?.contact as SocialTwinPrediction | undefined;
      if (contact) {
        this.hoveredContact.set(contact);
        document.body.style.cursor = 'pointer';
        return;
      }
    }

    if (!this.activeContact()) {
      this.hoveredContact.set(null);
    }
    document.body.style.cursor = 'default';
  }

  private handleNodeClick(): void {
    this.raycaster.setFromCamera(this.mouse, this.camera);
    const intersects = this.raycaster.intersectObjects(this.interactiveMeshes, false);

    if (intersects.length > 0) {
      const hit = intersects[0].object;
      const contact = (hit as any).userData?.contact as SocialTwinPrediction | undefined;
      if (contact) {
        this.activeContact.set(contact);
        this.contactSelected.emit(contact);
        this.drJefService.selectContact(contact);
      }
    }
  }

  // =========================================================================
  // Camera Presets & UI Controls
  // =========================================================================

  setCameraView(mode: 'default' | 'top' | 'side'): void {
    if (mode === 'default') {
      this.cameraTarget.set(25, 0, 0);
      this.cameraSpherical = { radius: 110, theta: THREE.MathUtils.degToRad(35), phi: THREE.MathUtils.degToRad(65) };
    } else if (mode === 'top') {
      this.cameraTarget.set(0, 0, 0);
      this.cameraSpherical = { radius: 95, theta: 0, phi: THREE.MathUtils.degToRad(8) };
    } else if (mode === 'side') {
      this.cameraTarget.set(45, 0, 0);
      this.cameraSpherical = { radius: 100, theta: THREE.MathUtils.degToRad(90), phi: THREE.MathUtils.degToRad(90) };
    }
    this.updateCameraFromSpherical();
  }

  toggleAutoRotate(): void {
    this.isAutoRotating.update(v => !v);
  }

  toggleBranch(b: TrajectoryPercentileBranch | 'all'): void {
    this.branchSelected.emit(b);
    this.drJefService.selectBranch(b);
  }

  updateBranchVisibility(b: TrajectoryPercentileBranch | 'all'): void {
    const p90 = this.trajectoriesGroup.getObjectByName('branch-p90');
    const p50 = this.trajectoriesGroup.getObjectByName('branch-p50');
    const p10 = this.trajectoriesGroup.getObjectByName('branch-p10');

    if (p90) p90.visible = b === 'all' || b === 'p90';
    if (p50) p50.visible = b === 'all' || b === 'p50';
    if (p10) p10.visible = b === 'all' || b === 'p10';
  }

  onDaySliderInput(event: Event): void {
    const val = Number((event.target as HTMLInputElement).value);
    this.currentDay.set(val);
    this.dayChanged.emit(val);
    this.drJefService.selectDay(val);
  }

  clearActiveContact(): void {
    this.activeContact.set(null);
    this.hoveredContact.set(null);
    this.contactSelected.emit(null);
    this.drJefService.selectContact(null);
  }

  // =========================================================================
  // Helpers
  // =========================================================================

  private resolveReactionColor(reaction: string): string {
    const r = (reaction || '').toLowerCase();
    if (r.includes('indign') || r.includes('enojo') || r.includes('crítica')) return '#EF4444'; // Red
    if (r.includes('desconfian') || r.includes('fatiga') || r.includes('distanc')) return '#F43F5E'; // Rose
    if (r.includes('expectativ') || r.includes('presi') || r.includes('kpi')) return '#F59E0B'; // Amber
    if (r.includes('apoyo') || r.includes('amig') || r.includes('sarcas')) return '#38BDF8'; // Sky Blue
    if (r.includes('aproba') || r.includes('orgullo') || r.includes('excel')) return '#10B981'; // Emerald
    return '#A855F7'; // Purple fallback
  }

  private createTextSprite(text: string, colorHex: string, fontSize: number = 11): THREE.Sprite {
    const canvas = document.createElement('canvas');
    canvas.width = 384;
    canvas.height = 96;
    const ctx = canvas.getContext('2d')!;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Pill background
    ctx.fillStyle = 'rgba(3, 7, 18, 0.85)';
    ctx.strokeStyle = colorHex;
    ctx.lineWidth = 3;
    const radius = 20;
    const x = 12, y = 14, w = canvas.width - 24, h = canvas.height - 28;

    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + w - radius, y);
    ctx.quadraticCurveTo(x + w, y, x + w, y + radius);
    ctx.lineTo(x + w, y + h - radius);
    ctx.quadraticCurveTo(x + w, y + h, x + w - radius, y + h);
    ctx.lineTo(x + radius, y + h);
    ctx.quadraticCurveTo(x, y + h, x, y + h - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // Text
    ctx.font = `bold ${fontSize * 3}px Inter, sans-serif`;
    ctx.fillStyle = colorHex;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, canvas.width / 2, canvas.height / 2);

    const texture = new THREE.CanvasTexture(canvas);
    texture.minFilter = THREE.LinearFilter;
    const mat = new THREE.SpriteMaterial({ map: texture, transparent: true });
    const sprite = new THREE.Sprite(mat);
    sprite.scale.set(12, 3, 1);
    return sprite;
  }

  @HostListener('window:resize')
  onWindowResize(): void {
    if (!this.containerRef || !this.renderer || !this.camera) return;
    const container = this.containerRef.nativeElement;
    const width = container.clientWidth;
    const height = container.clientHeight;

    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height);
  }
}
