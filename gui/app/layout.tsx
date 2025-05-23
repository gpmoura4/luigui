import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from './providers';
import RootLayoutContent from './root-layout-content';

const inter = Inter({ subsets: ['latin'] });

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          <RootLayoutContent>{children}</RootLayoutContent>
        </Providers>
      </body>
    </html>
  );
}

export const metadata = {
  generator: 'v0.dev'
};
