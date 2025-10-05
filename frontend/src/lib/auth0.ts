// Auth0 configuration and utilities
const AUTH0_DOMAIN = process.env.NEXT_PUBLIC_AUTH0_DOMAIN || 'dev-flmsl50bypxcwox4.us.auth0.com';
const AUTH0_CLIENT_ID = process.env.NEXT_PUBLIC_AUTH0_CLIENT_ID || 'EBaffK1uS7nzjhQZvu5rV8muio5wLvte';
const AUTH0_AUDIENCE = process.env.NEXT_PUBLIC_AUTH0_AUDIENCE || 'https://dev-flmsl50bypxcwox4.us.auth0.com/api/v2/';

// Get the base URL safely for both client and server
const getBaseUrl = () => {
  if (typeof window !== 'undefined') {
    return window.location.origin;
  }
  // Fallback for server-side rendering
  return process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000';
};

// Alternative: Try using a different callback URL that might be allowed
const getCallbackUrl = () => {
  // Try using a hardcoded URL that might be allowed by default
  return 'http://localhost:3000/callback';
};

export const auth0Config = {
  domain: AUTH0_DOMAIN,
  clientId: AUTH0_CLIENT_ID,
  audience: AUTH0_AUDIENCE,
  redirectUri: getCallbackUrl(),
  scope: 'openid profile email'
};

export function getAuth0LoginUrl(): string {
  const params = new URLSearchParams({
    response_type: 'code',
    client_id: AUTH0_CLIENT_ID,
    redirect_uri: auth0Config.redirectUri,
    scope: 'openid profile email',
    audience: AUTH0_AUDIENCE,
    state: Math.random().toString(36).substring(7)
  });

  return `https://${AUTH0_DOMAIN}/authorize?${params.toString()}`;
}

export function getAuth0LogoutUrl(): string {
  const params = new URLSearchParams({
    client_id: AUTH0_CLIENT_ID,
    returnTo: getBaseUrl()
  });

  return `https://${AUTH0_DOMAIN}/v2/logout?${params.toString()}`;
}
