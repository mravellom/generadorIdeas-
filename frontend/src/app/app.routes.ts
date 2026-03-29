import { Routes } from '@angular/router';
import { Dashboard } from './components/dashboard/dashboard';
import { IdeaDetail } from './components/idea-detail/idea-detail';

export const routes: Routes = [
  { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
  { path: 'dashboard', component: Dashboard },
  { path: 'idea/:id', component: IdeaDetail },
];
