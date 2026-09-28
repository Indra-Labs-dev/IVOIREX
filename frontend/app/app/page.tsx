'use client';

import Image from 'next/image';
import Link from 'next/link';
import { FormEvent, useEffect, useState } from 'react';
import type { paths } from './types/api';

type Profile = paths['/api/v1/profile/me']['get']['responses'][200]['content']['application/json'] & {
  skills: string[];
  interests: string[];
};

type SessionResult = { authenticated: boolean; profile?: Profile; detail?: string };

const defaultProfile: Omit<Profile, 'user_id' | 'username' | 'updated_at'> = {
  display_name: '', bio: '', city: 'Abidjan', country: 'Côte d’Ivoire', skills: [], interests: [],
};

export default function Home() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [form, setForm] = useState(defaultProfile);
  const [mode, setMode] = useState<'login' | 'register'>('register');
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    fetch('/api/session', { cache: 'no-store' })
      .then(async (response) => {
        if (!response.ok) throw new Error('La session est temporairement indisponible. Réessaie dans un instant.');
        return response.json() as Promise<SessionResult>;
      })
      .then((session) => {
        if (active && session.profile) loadProfile(session.profile);
      })
      .catch((reason: unknown) => { if (active) setError(reason instanceof Error ? reason.message : 'Impossible de joindre le service.'); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  function loadProfile(value: Profile) {
    setProfile(value);
    setForm({ display_name: value.display_name, bio: value.bio, city: value.city, country: value.country, skills: value.skills, interests: value.interests });
  }

  async function submitAuth(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setError(''); setNotice('');
    try {
      const response = await fetch('/api/session', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: mode, email, password, ...(mode === 'register' ? { username } : {}) }) });
      const result = await response.json() as SessionResult;
      if (!response.ok || !result.profile) throw new Error(result.detail ?? 'La connexion a échoué.');
      loadProfile(result.profile); setPassword(''); setNotice('Ton espace IVOIREX est prêt.');
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'La connexion a échoué.'); }
    finally { setBusy(false); }
  }

  async function saveProfile(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setError(''); setNotice('');
    try {
      const response = await fetch('/api/session', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'save-profile', profile: { ...form, skills: form.skills, interests: form.interests } }) });
      const result = await response.json() as Profile & { detail?: string };
      if (!response.ok) throw new Error(result.detail ?? 'Le profil n’a pas pu être enregistré.');
      loadProfile(result); setNotice('Profil enregistré. Tes changements sont sauvegardés.');
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Le profil n’a pas pu être enregistré.'); }
    finally { setBusy(false); }
  }

  async function signOut() {
    setBusy(true); setError('');
    try {
      await fetch('/api/session', { method: 'DELETE' });
      setProfile(null); setForm(defaultProfile); setNotice('Tu es déconnecté·e.');
    } catch { setError('La déconnexion a échoué. Réessaie.'); }
    finally { setBusy(false); }
  }

  function setTags(field: 'skills' | 'interests', value: string) {
    const values = value.split(',').map((item) => item.trim()).filter(Boolean).slice(0, 12);
    setForm((current) => ({ ...current, [field]: values }));
  }

  const completeness = profile ? Math.round(([
    Boolean(profile.display_name),
    Boolean(profile.bio),
    Boolean(profile.city),
    profile.skills.length > 0,
    profile.interests.length > 0,
  ].filter(Boolean).length / 5) * 100) : 0;

  return (
    <main className="app-shell">
      <nav className="nav" aria-label="Navigation principale">
        <a className="brand" href="#home" aria-label="IVOIREX, accueil"><Image src="/images/ivoirex-logo.png" alt="" width={42} height={42} priority /><span>IVOIREX</span></a>
        <div className="nav-right"><Link href="/campus" className="quiet-button">Campus</Link><span className="origin-label"><i /> DIGITAL CÔTE D’IVOIRE</span>{profile && <button className="quiet-button" onClick={signOut} disabled={busy}>Déconnexion</button>}</div>
      </nav>

      {loading ? <section className="loading-panel" aria-live="polite"><span className="loader" />Chargement de ton espace…</section> : profile ? (
        <>
          <section className="welcome" id="home">
            <div><div className="eyebrow"><span className="flag" aria-label="Drapeau ivoirien" /> TON ESPACE PERSONNEL</div><h1>Bonjour, <em>{profile.display_name}</em>.</h1><p>Pose la première pierre de ta présence dans la nouvelle génération numérique ivoirienne.</p></div>
            <div className="identity-mark"><span>{profile.display_name.trim().slice(0, 1).toUpperCase()}</span><small>@{profile.username}</small></div>
          </section>
          <section className="profile-layout" aria-label="Profil personnel">
            <aside className="profile-aside card-surface">
              <div className="aside-orb"><span>{profile.display_name.trim().slice(0, 1).toUpperCase()}</span></div>
              <h2>{profile.display_name}</h2><p className="handle">@{profile.username}</p>
              <p className="place"><span aria-hidden="true">⌖</span> {profile.city}, {profile.country}</p>
              <div className="aside-divider" />
              <p className="aside-caption">TA PRÉSENCE</p><p className="aside-copy">Ce profil t’appartient. Les informations ne deviennent visibles aux autres membres qu’avec les espaces communautaires à venir.</p>
              <div className="profile-completeness"><div><span>Profil</span><b>{completeness}%</b></div><span className="progress-track" role="progressbar" aria-label="Profil complété" aria-valuemin={0} aria-valuemax={100} aria-valuenow={completeness}><i style={{ width: `${completeness}%` }} /></span></div>
            </aside>
            <div className="editor-column">
              <div className="section-heading"><div><div className="eyebrow">IDENTITÉ · PROFIL</div><h2>Raconte qui tu es.</h2></div><span className="saved-indicator"><i /> ENREGISTRÉ DANS TON COMPTE</span></div>
              <form className="editor card-surface" onSubmit={saveProfile}>
                <div className="field-grid">
                  <label className="field"><span>Nom affiché</span><input required maxLength={80} value={form.display_name} onChange={(event) => setForm({ ...form, display_name: event.target.value })} autoComplete="name" /></label>
                  <label className="field"><span>Ville</span><input required maxLength={64} value={form.city} onChange={(event) => setForm({ ...form, city: event.target.value })} placeholder="Abidjan" autoComplete="address-level2" /></label>
                  <label className="field field-wide"><span>À propos <small>{form.bio.length}/280</small></span><textarea maxLength={280} rows={4} value={form.bio} onChange={(event) => setForm({ ...form, bio: event.target.value })} placeholder="Ce qui t’anime, ce que tu construis, ce que tu veux apprendre…" /></label>
                  <label className="field"><span>Compétences <small>séparées par des virgules</small></span><input value={form.skills.join(', ')} onChange={(event) => setTags('skills', event.target.value)} placeholder="Design, Python, entrepreneuriat" /></label>
                  <label className="field"><span>Centres d’intérêt <small>séparés par des virgules</small></span><input value={form.interests.join(', ')} onChange={(event) => setTags('interests', event.target.value)} placeholder="IA, agriculture, musique" /></label>
                </div>
                <div className="editor-footer"><p>Ton nom d’utilisateur <b>@{profile.username}</b> et ton pays ne peuvent pas être modifiés ici.</p><button className="primary-button" type="submit" disabled={busy}>{busy ? 'Enregistrement…' : 'Enregistrer le profil'} <span aria-hidden="true">↗</span></button></div>
                {error && <p className="message error" role="alert">{error}</p>}{notice && <p className="message success" role="status">{notice}</p>}
              </form>
              <div className="next-step"><span className="next-icon">✳</span><div><b>Ta prochaine étape commence ici.</b><p>Les compétences de ton profil serviront bientôt à te proposer des formations, projets et opportunités adaptés.</p></div><span className="coming-soon">À VENIR</span></div>
            </div>
          </section>
        </>
      ) : (
        <section className="auth-layout" id="home">
          <div className="auth-story"><div className="eyebrow"><span className="flag" /> ABIDJAN · BOUAKÉ · YAMOUSSOUKRO · PARTOUT</div><h1>Le futur<br />se construit<br /><em>ici.</em></h1><p>Un espace pour apprendre, créer et faire grandir les talents de Côte d’Ivoire. Commence par prendre ta place.</p><div className="story-line"><span /> Une plateforme ivoirienne, construite avec ambition.</div><div className="story-glow" aria-hidden="true" /></div>
          <div className="auth-card card-surface">
            <div className="auth-title"><div className="eyebrow">TON PROCHAIN CHAPITRE</div><h2>{mode === 'register' ? 'Crée ton espace.' : 'Bon retour.'}</h2><p>{mode === 'register' ? 'Ton profil est la première pierre de ton parcours.' : 'Retrouve ton espace IVOIREX.'}</p></div>
            <div className="auth-tabs" role="group" aria-label="Connexion ou inscription"><button type="button" aria-pressed={mode === 'register'} className={mode === 'register' ? 'selected' : ''} onClick={() => { setMode('register'); setError(''); }}>Créer un compte</button><button type="button" aria-pressed={mode === 'login'} className={mode === 'login' ? 'selected' : ''} onClick={() => { setMode('login'); setError(''); }}>Se connecter</button></div>
            <form className="auth-form" onSubmit={submitAuth}>
              {mode === 'register' && <label className="field"><span>Nom d’utilisateur</span><input required minLength={3} maxLength={32} pattern="[A-Za-z0-9_]+" value={username} onChange={(event) => setUsername(event.target.value)} placeholder="ex. aya_kouame" autoComplete="username" /></label>}
              <label className="field"><span>Adresse e-mail</span><input required type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="toi@exemple.ci" autoComplete="email" /></label>
              <label className="field"><span>Mot de passe</span><input required minLength={mode === 'register' ? 12 : 1} maxLength={72} type="password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder={mode === 'register' ? '12 caractères minimum' : 'Ton mot de passe'} autoComplete={mode === 'register' ? 'new-password' : 'current-password'} /></label>
              {error && <p className="message error" role="alert">{error}</p>}{notice && <p className="message success" role="status">{notice}</p>}
              <button className="primary-button auth-submit" type="submit" disabled={busy}>{busy ? 'Un instant…' : mode === 'register' ? 'Créer mon espace' : 'Me connecter'} <span aria-hidden="true">↗</span></button>
            </form>
            <p className="auth-privacy">Tes identifiants sont transmis de façon sécurisée. La session reste protégée dans ton navigateur.</p>
          </div>
        </section>
      )}

      <footer className="footer"><span>IVOIREX <b>✳</b> LE FUTUR SE CONSTRUIT ICI.</span><span>CONÇU EN CÔTE D’IVOIRE <i className="flag" /></span></footer>
    </main>
  );
}
