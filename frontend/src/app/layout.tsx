import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'GLUVIAS 1.0 | Legal Intelligence',
  description: 'Secure Legal Knowledge Management',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body style={{ margin: 0, backgroundColor: 'black' }}>
        {children}
      </body>
    </html>
  )
}
