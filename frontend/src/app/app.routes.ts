import { Routes } from '@angular/router';
import { MirrorFutureLandingComponent } from './features/landing/mirror-future-landing.component';
import { FutureSelfOracleV4Component } from './features/future-oracle-v4/future-self-oracle-v4.component';
import { RealIngestionPanelComponent } from './features/real-ingestion/real-ingestion-panel.component';
import { ForensicAndWhatsappTwinComponent } from './features/real-twin-console/forensic-and-whatsapp-twin.component';
import { ActuatorsControlPanelComponent } from './features/actuators/actuators-control-panel.component';
import { Multiverse3dPageComponent } from './features/multiverse-3d/multiverse-3d-page.component';

export const routes: Routes = [
  { path: '', component: MirrorFutureLandingComponent, pathMatch: 'full' },
  { path: 'oracle', component: FutureSelfOracleV4Component },
  { path: 'oracle-v4', redirectTo: 'oracle' },
  { path: 'ingestion', component: RealIngestionPanelComponent },
  { path: 'twins-forensics', component: ForensicAndWhatsappTwinComponent },
  { path: 'actuators-oracle', component: ActuatorsControlPanelComponent },
  { path: 'multiverse-3d', component: Multiverse3dPageComponent },
  { path: '**', redirectTo: '' }
];
