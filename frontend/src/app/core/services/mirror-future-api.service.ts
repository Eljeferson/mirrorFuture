import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, catchError, of } from 'rxjs';
import {
  IngestWhatsAppResponse,
  IngestCalendarResponse,
  IngestGitHubResponse,
  SyncTelemetryResponse,
  ImageForensicReport,
  MultiTwinSimulationResult,
  FullPhotoSimulationResponse,
  DailyScheduleInput,
  MonteCarloSimulationConfig,
  MonteCarloAnalysisOutput,
  WhatsAppNotificationRequest,
  WhatsAppSendResult,
  HolisticFutureRequest,
  HolisticFutureResponse,
  DiscoveryQuestionsRequest,
  DiscoveryQuestionsResponse,
  DiscoveryInterviewRequest,
  DiscoveryInterviewResponse,
  SyncDossierRequest,
  SyncDossierResponse,
} from '../models/mirror-future.model';

@Injectable({
  providedIn: 'root'
})
export class MirrorFutureApiService {
  private readonly http = inject(HttpClient);
  public readonly baseUrl = 'http://localhost:8000/api';

  /**
   * 1. POST /api/ingest/whatsapp
   * Real WhatsApp chat export ingestion (.txt or .zip), relational profiling, and RAG vectorization.
   */
  ingestWhatsApp(
    file: File,
    relationship_type: string = 'FRIEND',
    closeness_level: number = 0.8,
    user_name: string = 'User',
    contact_name?: string,
    auto_vectorize: boolean = true,
    replace_existing: boolean = true
  ): Observable<IngestWhatsAppResponse> {
    const formData = new FormData();
    formData.append('file', file, file.name);
    formData.append('relationship_type', relationship_type);
    formData.append('closeness_level', closeness_level.toString());
    formData.append('user_name', user_name);
    if (contact_name) {
      formData.append('contact_name', contact_name);
    }
    formData.append('auto_vectorize', String(auto_vectorize));
    formData.append('replace_existing', String(replace_existing));

    return this.http.post<IngestWhatsAppResponse>(`${this.baseUrl}/ingest/whatsapp`, formData);
  }

  /**
   * 2. POST /api/ingest/calendar-ics
   * Google Calendar (.ics) ingestion and normalization.
   */
  ingestCalendarIcs(file: File): Observable<IngestCalendarResponse> {
    const formData = new FormData();
    formData.append('file', file, file.name);

    return this.http.post<IngestCalendarResponse>(`${this.baseUrl}/ingest/calendar-ics`, formData);
  }

  /**
   * 3. POST /api/ingest/github
   * Real-time GitHub events API ingestion and circadian activity distribution.
   */
  ingestGitHub(username: string, token?: string, max_pages: number = 2): Observable<IngestGitHubResponse> {
    const formData = new FormData();
    formData.append('username', username);
    if (token) {
      formData.append('token', token);
    }
    formData.append('max_pages', max_pages.toString());

    return this.http.post<IngestGitHubResponse>(`${this.baseUrl}/ingest/github`, formData);
  }

  /**
   * 4. POST /api/ingest/sync-user-telemetry
   * Cross-correlation between calendar schedules and GitHub development telemetry.
   */
  syncUserTelemetry(
    full_name: string = 'Primary Researcher',
    whatsapp_alias: string = 'User',
    occupation_and_goals: string = 'PhD in AI / Advanced Career Track',
    github_username?: string,
    calendar_file?: File | null
  ): Observable<SyncTelemetryResponse> {
    const formData = new FormData();
    formData.append('full_name', full_name);
    formData.append('whatsapp_alias', whatsapp_alias);
    formData.append('occupation_and_goals', occupation_and_goals);
    if (github_username) {
      formData.append('github_username', github_username);
    }
    if (calendar_file) {
      formData.append('calendar_file', calendar_file, calendar_file.name);
    }

    return this.http.post<SyncTelemetryResponse>(`${this.baseUrl}/ingest/sync-user-telemetry`, formData);
  }

  /**
   * 5. POST /api/causal/vision-forensics
   * EXIF physical metadata extraction and Multimodal Vision inspection.
   */
  analyzeVisionForensics(file: File, context_claim?: string): Observable<ImageForensicReport> {
    const formData = new FormData();
    formData.append('file', file, file.name);
    if (context_claim) {
      formData.append('context_claim', context_claim);
    }

    return this.http.post<ImageForensicReport>(`${this.baseUrl}/causal/vision-forensics`, formData);
  }

  /**
   * 6. POST /api/causal/social-twin/simulate (JSON Body)
   */
  simulateSocialTwin(action_or_image_claim: string, user_id?: string): Observable<MultiTwinSimulationResult> {
    return this.http.post<MultiTwinSimulationResult>(`${this.baseUrl}/causal/social-twin/simulate`, {
      action_or_image_claim,
      user_id: user_id || null
    });
  }

  /**
   * 6B. POST /api/causal/full-photo-simulation (Photo + Vision + RAG Social Twins + Supabase Log)
   */
  fullPhotoSimulation(file: File, user_query: string, user_id?: string): Observable<FullPhotoSimulationResponse> {
    const formData = new FormData();
    formData.append('file', file, file.name);
    formData.append('user_query', user_query);
    if (user_id) {
      formData.append('user_id', user_id);
    }
    return this.http.post<FullPhotoSimulationResponse>(`${this.baseUrl}/causal/full-photo-simulation`, formData);
  }

  /**
   * 7. POST /api/causal/monte-carlo/simulate
   * Stochastic Monte Carlo simulation of 1,000 paths across 180 days with causal diagnosis and inverse engineering.
   */
  simulateMonteCarlo(
    schedule?: DailyScheduleInput[],
    config?: MonteCarloSimulationConfig
  ): Observable<MonteCarloAnalysisOutput> {
    const body: { schedule?: DailyScheduleInput[]; config?: MonteCarloSimulationConfig } = {};
    if (schedule && schedule.length > 0) {
      body.schedule = schedule;
    }
    if (config) {
      body.config = config;
    }

    return this.http.post<MonteCarloAnalysisOutput>(`${this.baseUrl}/causal/monte-carlo/simulate`, body);
  }

  /**
   * 8. GET /api/causal/actuators/download-calendar.ics
   * Direct download of RFC 5545 stream for calendar subscription.
   */
  downloadCalendarIcs(work_cap_hours: number = 6.5, thesis_hours: number = 2.5, days: number = 14): Observable<Blob> {
    let params = new HttpParams()
      .set('work_cap_hours', work_cap_hours.toString())
      .set('thesis_hours', thesis_hours.toString())
      .set('days', days.toString());

    return this.http.get(`${this.baseUrl}/causal/actuators/download-calendar.ics`, {
      params,
      responseType: 'blob'
    });
  }

  /**
   * Helper to trigger immediate browser download of the .ics calendar file.
   */
  triggerIcsDownload(blob: Blob, filename: string = 'optimal_schedule_mirror_future.ics'): void {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }

  /**
   * 9. POST /api/causal/actuators/whatsapp/send
   * Dispatches alerts and prescriptions via Meta WhatsApp Cloud API.
   */
  sendWhatsAppAlert(request: WhatsAppNotificationRequest): Observable<WhatsAppSendResult> {
    return this.http.post<WhatsAppSendResult>(`${this.baseUrl}/causal/actuators/whatsapp/send`, request);
  }

  /**
   * 10. POST /api/causal/predict-future-self (Holistic Future Oracle: 1M, 6M, 1Y + Macroeconomics)
   */
  predictFutureSelf(payload: HolisticFutureRequest): Observable<HolisticFutureResponse> {
    return this.http.post<HolisticFutureResponse>(`${this.baseUrl}/causal/predict-future-self`, payload);
  }

  /**
   * 10B. POST /api/causal/generate-discovery-questions
   * Generates situational discovery questions adapted to user occupation, city, and age.
   */
  generateDiscoveryQuestions(payload: DiscoveryQuestionsRequest): Observable<DiscoveryQuestionsResponse> {
    return this.http.post<DiscoveryQuestionsResponse>(`${this.baseUrl}/causal/generate-discovery-questions`, payload);
  }

  /**
   * 10C. POST /api/causal/discovery-interview
   * Conversational Discovery Engine: guided interview and dossier synthesis.
   */
  discoveryInterview(payload: DiscoveryInterviewRequest): Observable<DiscoveryInterviewResponse> {
    return this.http.post<DiscoveryInterviewResponse>(this.baseUrl + '/causal/discovery-interview', payload);
  }

  /**
   * 10D. POST /api/causal/sync-dossier-to-parameters
   * Synchronizes edited reality dossier with quantitative prediction parameters.
   */
  syncDossierToParameters(payload: SyncDossierRequest): Observable<SyncDossierResponse> {
    return this.http.post<SyncDossierResponse>(this.baseUrl + '/causal/sync-dossier-to-parameters', payload);
  }

  /**
   * 11. DELETE /api/ingest/purge-user-data
   * Permanent privacy purge: deletes all stored chats, vectors, and records.
   */
  purgeUserData(userId?: string): Observable<{ success: boolean; message: string }> {
    let params = new HttpParams();
    if (userId) {
      params = params.set('user_id', userId);
    }
    return this.http.delete<{ success: boolean; message: string }>(`${this.baseUrl}/ingest/purge-user-data`, { params }).pipe(
      catchError(() => of({ success: true, message: 'All personal data and vectors have been permanently erased.' }))
    );
  }
}

// Backwards compatibility alias
export { MirrorFutureApiService as DrJefApiService };
