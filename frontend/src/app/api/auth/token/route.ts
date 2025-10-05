import { NextRequest, NextResponse } from 'next/server';

const AUTH0_DOMAIN = process.env.AUTH0_ISSUER_BASE_URL?.replace('https://', '') || 'dev-flmsl50bypxcwox4.us.auth0.com';
const AUTH0_CLIENT_ID = process.env.AUTH0_CLIENT_ID || 'EBaffK1uS7nzjhQZvu5rV8muio5wLvte';
const AUTH0_CLIENT_SECRET = process.env.AUTH0_CLIENT_SECRET || 'idG3QPnTjt7UL2SetE6HTt4XUALxB87Illyprbd9R1f6Mk0NH1_V1AOOSLFU2N1m';
const AUTH0_AUDIENCE = process.env.AUTH0_AUDIENCE || 'https://dev-flmsl50bypxcwox4.us.auth0.com/api/v2/';

// Simple in-memory cache to prevent code reuse
const usedCodes = new Set<string>();

export async function POST(request: NextRequest) {
  try {
    const { code } = await request.json();

    if (!code) {
      return NextResponse.json({ error: 'Authorization code is required' }, { status: 400 });
    }

    // Check if code has already been used
    if (usedCodes.has(code)) {
      console.error('Authorization code already used:', code.substring(0, 10) + '...');
      return NextResponse.json({ error: 'Authorization code has already been used' }, { status: 400 });
    }

    // Mark code as used
    usedCodes.add(code);

    // Exchange authorization code for access token
    const tokenResponse = await fetch(`https://${AUTH0_DOMAIN}/oauth/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        grant_type: 'authorization_code',
        client_id: AUTH0_CLIENT_ID,
        client_secret: AUTH0_CLIENT_SECRET,
        code: code,
        redirect_uri: 'http://localhost:3000/callback',
        audience: AUTH0_AUDIENCE,
      }),
    });

    if (!tokenResponse.ok) {
      const error = await tokenResponse.text();
      console.error('Token exchange failed:', error);
      console.error('Request details:', {
        domain: AUTH0_DOMAIN,
        client_id: AUTH0_CLIENT_ID,
        redirect_uri: 'http://localhost:3000/callback',
        code_length: code.length
      });
      
      // Remove the code from used set if exchange failed
      usedCodes.delete(code);
      
      return NextResponse.json({ 
        error: 'Failed to exchange code for token', 
        details: error 
      }, { status: 400 });
    }

    const tokenData = await tokenResponse.json();

    // Get user info using the access token
    const userResponse = await fetch(`https://${AUTH0_DOMAIN}/userinfo`, {
      headers: {
        'Authorization': `Bearer ${tokenData.access_token}`,
      },
    });

    if (!userResponse.ok) {
      return NextResponse.json({ error: 'Failed to get user info' }, { status: 400 });
    }

    const userData = await userResponse.json();

    return NextResponse.json({
      access_token: tokenData.access_token,
      user: userData,
    });
  } catch (error) {
    console.error('Auth callback error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
