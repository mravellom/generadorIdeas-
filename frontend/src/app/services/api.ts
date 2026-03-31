import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Idea } from '../models/idea.model';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getIdeas(): Observable<Idea[]> {
    return this.http.get<Idea[]>(`${this.baseUrl}/api/ideas/`);
  }

  getTopOpportunities(limit = 10): Observable<Idea[]> {
    return this.http.get<Idea[]>(`${this.baseUrl}/api/ideas/top?limit=${limit}`);
  }

  getIdea(id: number): Observable<Idea> {
    return this.http.get<Idea>(`${this.baseUrl}/api/ideas/${id}`);
  }

  analyzeIdea(id: number): Observable<Idea> {
    return this.http.post<Idea>(`${this.baseUrl}/api/ideas/${id}/analyze`, {});
  }

  generateExecution(id: number): Observable<Idea> {
    return this.http.post<Idea>(`${this.baseUrl}/api/ideas/${id}/execute`, {});
  }

  runScraper(): Observable<{ message: string; count: number }> {
    return this.http.post<{ message: string; count: number }>(`${this.baseUrl}/api/scraper/run`, {});
  }
}
