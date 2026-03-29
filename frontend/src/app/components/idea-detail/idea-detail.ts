import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { ApiService } from '../../services/api';
import { Idea } from '../../models/idea.model';

@Component({
  selector: 'app-idea-detail',
  imports: [],
  templateUrl: './idea-detail.html',
  styleUrl: './idea-detail.scss',
})
export class IdeaDetail implements OnInit {
  idea: Idea | null = null;
  loading = true;
  analyzing = false;
  generating = false;

  constructor(
    private route: ActivatedRoute,
    private api: ApiService
  ) {}

  ngOnInit() {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.api.getIdea(id).subscribe((data) => {
      this.idea = data;
      this.loading = false;
    });
  }

  analyze() {
    if (!this.idea) return;
    this.analyzing = true;
    this.api.analyzeIdea(this.idea.id).subscribe({
      next: (data) => {
        this.idea = data;
        this.analyzing = false;
      },
      error: () => (this.analyzing = false),
    });
  }

  generateExecution() {
    if (!this.idea) return;
    this.generating = true;
    this.api.generateExecution(this.idea.id).subscribe({
      next: (data) => {
        this.idea = data;
        this.generating = false;
      },
      error: () => (this.generating = false),
    });
  }

  getScoreWidth(score: number | null | undefined): number {
    return score ? (score / 5) * 100 : 0;
  }
}
