'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import LoadingPage from '@/components/LoadingPage';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to landing page
    router.push('/landing');
  }, [router]);

  return (
    <LoadingPage message="Redirecting to landing page..." />
  );
}
