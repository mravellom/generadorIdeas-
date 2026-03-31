import { Component, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { ApiService } from '../../services/api';
import { Idea } from '../../models/idea.model';

@Component({
  selector: 'app-dashboard',
  imports: [RouterLink],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
})
export class Dashboard implements OnInit {
  ideas: Idea[] = [];
  loading = true;
  filter: 'all' | 'analyzed' | 'top' = 'all';

  scraping = false;
  analyzing = false;
  executing = false;
  actionMessage = '';

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.loadIdeas();
  }

  loadIdeas() {
    this.loading = true;
    if (this.filter === 'top') {
      this.api.getTopOpportunities(20).subscribe((data) => {
        this.ideas = data;
        this.loading = false;
      });
    } else {
      this.api.getIdeas().subscribe((data) => {
        if (this.filter === 'analyzed') {
          this.ideas = data.filter((i) => i.analysis !== null);
        } else {
          this.ideas = data;
        }
        this.loading = false;
      });
    }
  }

  setFilter(filter: 'all' | 'analyzed' | 'top') {
    this.filter = filter;
    this.loadIdeas();
  }

  runScraper() {
    this.scraping = true;
    this.actionMessage = '';
    this.api.runScraper().subscribe({
      next: (res) => {
        this.actionMessage = `Scraper: ${res.count} startups encontradas`;
        this.scraping = false;
        this.loadIdeas();
      },
      error: () => {
        this.actionMessage = 'Error al ejecutar scraper';
        this.scraping = false;
      },
    });
  }

  analyzeAll() {
    this.analyzing = true;
    this.actionMessage = '';
    this.api.analyzeAll().subscribe({
      next: (res) => {
        this.actionMessage = `Analizadas: ${res.analyzed} | Errores: ${res.errors}`;
        this.analyzing = false;
        this.loadIdeas();
      },
      error: () => {
        this.actionMessage = 'Error al analizar';
        this.analyzing = false;
      },
    });
  }

  executeAll() {
    this.executing = true;
    this.actionMessage = '';
    this.api.executeAll().subscribe({
      next: (res) => {
        this.actionMessage = `Planes generados: ${res.executed} | Errores: ${res.errors}`;
        this.executing = false;
        this.loadIdeas();
      },
      error: () => {
        this.actionMessage = 'Error al generar planes';
        this.executing = false;
      },
    });
  }

  getScoreBadgeClass(score: number | null | undefined): string {
    if (!score) return 'badge-low';
    if (score >= 16) return 'badge-high';
    if (score >= 12) return 'badge-medium';
    return 'badge-low';
  }
}
