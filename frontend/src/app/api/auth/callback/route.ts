import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const code = searchParams.get('code');
  const error = searchParams.get('error');
  const errorDescription = searchParams.get('error_description');

  if (error) {
    console.error('Auth0 error:', error, errorDescription);
    return NextResponse.redirect(new URL(`/landing?error=${encodeURIComponent(error)}`, request.url));
  }

  if (!code) {
    console.error('No authorization code received');
    return NextResponse.redirect(new URL('/landing?error=no_code', request.url));
  }

  try {
    // Exchange code for tokens
    const tokenResponse = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000'}/api/auth/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code }),
    });

    if (!tokenResponse.ok) {
      throw new Error('Token exchange failed');
    }

    const { accessToken, idToken, user } = await tokenResponse.json();

    // Redirect to callback page with tokens
    const callbackUrl = new URL('/callback', request.url);
    callbackUrl.searchParams.set('access_token', accessToken);
    callbackUrl.searchParams.set('id_token', idToken);
    callbackUrl.searchParams.set('user', JSON.stringify(user));

    return NextResponse.redirect(callbackUrl);
  } catch (error) {
    console.error('Callback error:', error);
    return NextResponse.redirect(new URL('/landing?error=callback_failed', request.url));
  }
}
