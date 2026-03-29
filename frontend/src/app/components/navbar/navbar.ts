import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { ApiService } from '../../services/api';

@Component({
  selector: 'app-navbar',
  imports: [RouterLink],
  templateUrl: './navbar.html',
  styleUrl: './navbar.scss',
})
export class Navbar {
  scraping = false;
  scraperMessage = '';

  constructor(private api: ApiService) {}

  runScraper() {
    this.scraping = true;
    this.scraperMessage = '';
    this.api.runScraper().subscribe({
      next: (res) => {
        this.scraperMessage = res.message;
        this.scraping = false;
      },
      error: () => {
        this.scraperMessage = 'Error al scrapear';
        this.scraping = false;
      },
    });
  }
}
