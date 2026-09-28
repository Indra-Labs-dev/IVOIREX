import { expect, test } from '@playwright/test';

test('new member registers, signs in, learns, saves progress, then signs out', async ({ page }) => {
  const suffix = `${Date.now()}${Math.floor(Math.random() * 1000)}`;
  const username = `campus_${suffix}`;
  const email = `${username}@example.ci`;
  const password = 'Campus-E2E-Password-2026!';

  await page.goto('/');
  await page.getByLabel('Nom d’utilisateur').fill(username);
  await page.getByLabel('Adresse e-mail').fill(email);
  await page.getByLabel('Mot de passe').fill(password);
  await page.getByRole('button', { name: 'Créer mon espace' }).click();
  await expect(page.locator('.identity-mark small')).toHaveText(`@${username}`);
  await page.getByRole('button', { name: 'Déconnexion' }).click();
  await expect(page.getByRole('button', { name: 'Se connecter' })).toBeVisible();

  await page.getByRole('button', { name: 'Se connecter' }).click();
  await page.getByLabel('Adresse e-mail').fill(email);
  await page.getByLabel('Mot de passe').fill(password);
  await page.getByRole('button', { name: 'Me connecter' }).click();
  await expect(page.getByRole('button', { name: 'Déconnexion' })).toBeVisible();

  await page.getByRole('link', { name: 'Campus' }).click();
  await expect(page.getByRole('heading', { name: 'Trouve ton prochain parcours.' })).toBeVisible();
  const course = page.locator('.course-card').first();
  await expect(course).toBeVisible();
  await course.click();
  await page.getByRole('button', { name: 'M’inscrire gratuitement' }).click();
  await page.getByRole('link', { name: 'Continuer mon parcours' }).click();
  await expect(page.locator('.lesson-content h2')).toBeVisible();
  await page.getByRole('button', { name: 'Marquer comme terminée' }).click();
  await expect(page.getByText('Leçon terminée · progression enregistrée')).toBeVisible();
  await expect(page.locator('.learn-progress b')).toHaveText('25%');

  await page.getByRole('link', { name: 'Quitter le cours' }).click();
  await page.getByRole('link', { name: 'Mon espace' }).click();
  await page.getByRole('button', { name: 'Déconnexion' }).click();
  await expect(page.getByRole('button', { name: 'Créer un compte' })).toBeVisible();
});
