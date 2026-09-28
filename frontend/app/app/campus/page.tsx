'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import type { components } from '../types/api';
import './campus.css';

type Page = components['schemas']['CoursePage'];

export default function CampusCatalog() {
  const [data, setData] = useState<Page | null>(null);
  const [q, setQ] = useState(''); const [category, setCategory] = useState(''); const [level, setLevel] = useState(''); const [duration, setDuration] = useState('');
  const [page, setPage] = useState(1); const [loading, setLoading] = useState(true); const [error, setError] = useState('');
  useEffect(() => {
    let active = true;
    const params = new URLSearchParams({ page: String(page), page_size: '9' });
    if (q.trim()) params.set('q', q.trim()); if (category) params.set('category', category); if (level) params.set('level', level); if (duration) params.set('max_duration_minutes', duration);
    fetch(`/api/campus/courses?${params}`, { cache: 'no-store' }).then(async (r) => { if (!r.ok) throw new Error('Le catalogue est indisponible pour le moment.'); return r.json() as Promise<Page>; })
      .then((result) => { if (active) setData(result); }).catch((e: unknown) => { if (active) setError(e instanceof Error ? e.message : 'Une erreur est survenue.'); }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [page, q, category, level, duration]);
  function updateFilter(change: () => void) { setLoading(true); setError(''); change(); setPage(1); }
  return <main className="campus-shell">
    <nav className="campus-nav"><Link href="/" className="campus-brand"><span className="campus-mark">✳</span> IVOIREX</Link><div><Link href="/">Mon espace</Link><Link href="/campus" aria-current="page">Campus</Link><Link href="/api/session">Compte</Link></div></nav>
    <section className="campus-hero"><div className="campus-kicker"><span className="flag"/> CAMPUS · APPRENDRE ENSEMBLE</div><h1>Les compétences<br/>qui <em>ouvrent des portes.</em></h1><p>Des parcours concrets pour apprendre, pratiquer et faire grandir tes ambitions en Côte d’Ivoire.</p><div className="campus-stats"><span><b>{data?.total ?? '—'}</b> formations</span><span><b>À ton rythme</b> · où que tu sois</span></div></section>
    <section className="catalog-section"><div className="catalog-heading"><div><div className="campus-kicker">LE CATALOGUE</div><h2>Trouve ton prochain parcours.</h2></div><label className="catalog-search"><span className="sr-only">Rechercher une formation</span><span aria-hidden="true">⌕</span><input value={q} onChange={(e) => updateFilter(() => setQ(e.target.value))} placeholder="Python, entrepreneuriat…" /></label></div>
      <div className="catalog-filters"><label><span>Thématique</span><select value={category} onChange={(e) => updateFilter(() => setCategory(e.target.value))}><option value="">Toutes</option>{(data?.categories ?? []).map((v) => <option key={v}>{v}</option>)}</select></label><label><span>Niveau</span><select value={level} onChange={(e) => updateFilter(() => setLevel(e.target.value))}><option value="">Tous les niveaux</option>{(data?.levels ?? []).map((v) => <option key={v}>{v}</option>)}</select></label><label><span>Durée maximale</span><select value={duration} onChange={(e) => updateFilter(() => setDuration(e.target.value))}><option value="">Toutes les durées</option><option value="30">30 minutes</option><option value="60">1 heure</option><option value="120">2 heures</option></select></label><span className="catalog-count">{data ? `${data.total} résultat${data.total > 1 ? 's' : ''}` : ''}</span></div>
      {loading && <p className="catalog-state" role="status">Chargement des formations…</p>}{error && <p className="catalog-state error" role="alert">{error}</p>}
      {!loading && !error && data?.items.length === 0 && <div className="catalog-state">Aucune formation ne correspond à cette recherche.</div>}
      {!loading && !error && data && <div className="course-grid">{data.items.map((course, i) => <Link className="course-card" href={`/campus/${course.slug}`} key={course.id}><div className={`course-art art-${i % 6}`}><span>{course.category}</span><b>{String(i + 1 + (page - 1) * 9).padStart(2, '0')}</b>{course.is_demo && <small>PARCOURS DÉMO</small>}</div><div className="course-card-body"><div className="course-meta"><span>{course.level}</span><span>{course.duration_minutes} min</span></div><h3>{course.title}</h3><p>{course.short_description}</p><div className="course-card-foot"><span>{course.module_count} modules · {course.lesson_count} leçons</span><b>Explorer <i>↗</i></b></div></div></Link>)}</div>}
      {data && data.total > data.page_size && <div className="catalog-pagination"><button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}>← Précédent</button><span>Page {page}</span><button onClick={() => setPage((p) => p + 1)} disabled={!data.has_more}>Suivant →</button></div>}
    </section><footer className="campus-footer"><span>IVOIREX <b>✳</b> LE FUTUR SE CONSTRUIT ICI.</span><span>CONÇU EN CÔTE D’IVOIRE <i className="flag"/></span></footer>
  </main>;
}
