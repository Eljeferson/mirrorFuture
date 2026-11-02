import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DrJefCausalGraph3dComponent } from './dr-jef-causal-graph-3d.component';
import { MonteCarloChartComponent } from './monte-carlo-chart.component';
import { DrJefService } from '../../core/services/dr-jef.service';
import { DrJefApiService } from '../../core/services/dr-jef-api.service';

@Component({
  selector: 'app-multiverse-3d-page',
  standalone: true,
  imports: [CommonModule, DrJefCausalGraph3dComponent, MonteCarloChartComponent],
  template: `
    <div class="max-w-7xl mx-auto p-4 md:p-6 space-y-8">
      <app-dr-jef-causal-graph-3d
        [curves]="state.curves()"
        [contacts]="state.simulatedContacts()"
        [branch]="state.selectedBranch()"
        [selectedDay]="state.selectedDay()"
        (contactSelected)="state.selectContact($event)"
        (branchSelected)="state.selectBranch($event)"
        (dayChanged)="state.selectDay($event)">
      </app-dr-jef-causal-graph-3d>

      @if (state.curves()) {
        <app-monte-carlo-chart
          [curves]="state.curves()"
          [prescription]="state.prescription()"
          [diagnosis]="state.diagnosis()">
        </app-monte-carlo-chart>
      }
    </div>
  `
})
export class Multiverse3dPageComponent implements OnInit {
  readonly state = inject(DrJefService);
  private readonly api = inject(DrJefApiService);

  ngOnInit(): void {
    // Si entra directo a la pestaña 3D y aún no ha corrido Monte Carlo, dispara una corrida real al backend
    if (!this.state.curves()) {
      this.api.simulateMonteCarlo().subscribe({
        next: (res) => this.state.setMonteCarloOutput(res),
        error: (err) => console.error('Error cargando curvas iniciales:', err)
      });
    }
  }
}
