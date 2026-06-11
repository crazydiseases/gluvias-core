import React from 'react';
import Link from 'next/link';

export default function HomePage() {
  return (
    <div style={{ 
      backgroundColor: '#000', 
      color: '#fff', 
      minHeight: '100vh', 
      display: 'flex', 
      flexDirection: 'column', 
      alignItems: 'center', 
      justifyContent: 'center',
      fontFamily: 'sans-serif' 
    }}>
      <h1 style={{ fontSize: '3rem', marginBottom: '1rem', background: 'linear-gradient(to right, #3b82f6, #8b5cf6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
        Firm AI
      </h1>
      <p style={{ color: '#aaa', fontSize: '1.2rem', marginBottom: '2rem' }}>
        Next-generation legal intelligence.
      </p>
      <div style={{ display: 'flex', gap: '20px' }}>
        <Link href="/dashboard" style={{ padding: '12px 24px', backgroundColor: '#3b82f6', borderRadius: '8px', color: 'white', textDecoration: 'none', fontWeight: 'bold' }}>
          Get Started
        </Link>
        <Link href="/account" style={{ padding: '12px 24px', border: '1px solid #333', borderRadius: '8px', color: 'white', textDecoration: 'none' }}>
          Settings
        </Link>
      </div>
    </div>
  );
}
