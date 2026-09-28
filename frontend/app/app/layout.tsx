import './globals.css';
import type { Metadata } from 'next';

const logo = '/images/ivoirex-logo.png';

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL ?? 'http://localhost:43100'),
  title: 'IVOIREX — Le futur se construit ici',
  description: 'Apprendre, créer et faire grandir les talents de Côte d’Ivoire.',
  applicationName: 'IVOIREX',
  icons: { icon: logo, apple: logo },
  openGraph: {
    title: 'IVOIREX — Le futur se construit ici',
    description: 'Un espace pour apprendre, créer et faire grandir les talents de Côte d’Ivoire.',
    locale: 'fr_CI',
    siteName: 'IVOIREX',
    type: 'website',
    images: [{ url: logo, width: 1254, height: 1254, alt: 'Logo IVOIREX' }],
  },
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return <html lang="fr"><body>{children}</body></html>;
}
