'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import type { components } from '../../types/api';
import '../campus.css';

type Course = components['schemas']['CourseDetail'];
type Enrollments = components['schemas']['EnrollmentPage'];

export default function CoursePage() {
  const { slug } = useParams<{ slug: string }>(); const router = useRouter(); const [course, setCourse] = useState<Course | null>(null); const [enrolled, setEnrolled] = useState(false); const [progress, setProgress] = useState(0); const [auth, setAuth] = useState(false); const [loading, setLoading] = useState(true); const [busy, setBusy] = useState(false); const [error, setError] = useState('');
  useEffect(() => { let active = true;
    Promise.all([fetch(`/api/campus/courses/${encodeURIComponent(slug)}`, { cache: 'no-store' }).then(async (r) => { if (!r.ok) throw new Error('Cette formation est introuvable.'); return r.json() as Promise<Course>; }), fetch('/api/session', { cache: 'no-store' }).then((r) => r.json())])
      .then(async ([item, session]) => { if (!active) return; setCourse(item); const logged = Boolean(session.authenticated); setAuth(logged); if (logged) { const response = await fetch('/api/campus/enrollments/me'); if (response.ok) { const mine = await response.json() as Enrollments; const match = mine.items.find((e) => e.course_id === item.id); if (match) { setEnrolled(true); setProgress(match.progress_percent); } } } })
      .catch((e: unknown) => { if (active) setError(e instanceof Error ? e.message : 'Une erreur est survenue.'); }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [slug]);
  async function enroll() { if (!course) return; if (!auth) { router.push('/'); return; } setBusy(true); setError(''); try { const response = await fetch('/api/campus/enrollments', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ course_id: course.id }) }); if (!response.ok) { const result = await response.json(); throw new Error(result.detail ?? 'Inscription impossible.'); } setEnrolled(true); } catch (e) { setError(e instanceof Error ? e.message : 'Inscription impossible.'); } finally { setBusy(false); } }
  if (loading) return <main className="campus-shell"><p className="catalog-state">Chargement de la formation…</p></main>;
  if (!course) return <main className="campus-shell"><p className="catalog-state error" role="alert">{error || 'Formation introuvable.'}</p><Link href="/campus">Retour au catalogue</Link></main>;
  return <main className="campus-shell"><nav className="campus-nav"><Link href="/" className="campus-brand"><span className="campus-mark">✳</span> IVOIREX</Link><div><Link href="/">Mon espace</Link><Link href="/campus">Campus</Link></div></nav>
    <div className="crumb"><Link href="/campus">← Toutes les formations</Link><span> / {course.category}</span></div>
    <section className="detail-hero"><div className="detail-copy"><div className="campus-kicker">{course.category} · {course.level}{course.is_demo ? ' · PARCOURS DÉMO' : ''}</div><h1>{course.title}</h1><p className="detail-lead">{course.short_description}</p><div className="detail-facts"><span>{course.module_count} modules</span><span>{course.lesson_count} leçons</span><span>{course.duration_minutes} minutes</span><span>Par {course.instructor}</span></div>{enrolled ? <Link className="campus-cta" href={`/campus/${course.slug}/learn`}>Continuer mon parcours <span>↗</span></Link> : <button className="campus-cta" onClick={enroll} disabled={busy}>{busy ? 'Inscription…' : auth ? 'M’inscrire gratuitement' : 'Connecte-toi pour commencer'} <span>↗</span></button>}{error && <p className="message error" role="alert">{error}</p>}{enrolled && <p className="enrolled-note">Progression enregistrée · {progress}%</p>}</div><div className="detail-emblem" aria-hidden="true"><span>✳</span><b>APPRENDRE<br/>POUR AGIR</b></div></section>
    <section className="detail-layout"><article className="detail-description"><div className="campus-kicker">LE PARCOURS</div><h2>Des bases solides, une étape à la fois.</h2><p>{course.description}</p><div className="detail-instructor"><span className="instructor-avatar">{course.instructor.slice(0,1)}</span><div><small>TRANSMIS PAR</small><b>{course.instructor}</b></div><span className="flag"/></div></article><aside className="outline-panel"><div className="campus-kicker">AU PROGRAMME</div><h2>Le parcours en détail</h2>{course.modules.map((module, index) => <div className="outline-module" key={module.id}><div className="outline-module-title"><span>{String(index + 1).padStart(2, '0')}</span><b>{module.title}</b><small>{module.lessons.length} leçons</small></div>{module.lessons.map((lesson) => <div className="outline-lesson" key={lesson.id}><span>◇</span><span>{lesson.title}</span><small>{lesson.duration_minutes} min</small></div>)}</div>)}</aside></section><footer className="campus-footer"><span>IVOIREX <b>✳</b> LE FUTUR SE CONSTRUIT ICI.</span><span>CONÇU EN CÔTE D’IVOIRE <i className="flag"/></span></footer>
  </main>;
}
