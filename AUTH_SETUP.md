# Auth0 Configuration for User Profile Data

## Problem
The JWT token from Auth0 doesn't include the user's name and email by default, causing the profile page to show "Not available" for these fields.

## Solution Options

### Option 1: Configure Auth0 to Include User Data in JWT (Recommended)

This is the simplest solution that doesn't require additional API calls.

#### Steps:

1. **Go to Auth0 Dashboard** → Applications → Your Application → Advanced Settings → OAuth

2. **Add Custom Claims** to include user profile data in the JWT token:
   - Go to Actions → Flows → Login / Post Login
   - Create a new Action with this code:

```javascript
exports.onExecutePostLogin = async (event, api) => {
  const namespace = 'https://your-app.com/';
  
  if (event.user) {
    api.idToken.setCustomClaim(`${namespace}email`, event.user.email);
    api.idToken.setCustomClaim(`${namespace}name`, event.user.name);
    api.idToken.setCustomClaim(`${namespace}nickname`, event.user.nickname);
    api.idToken.setCustomClaim(`${namespace}picture`, event.user.picture);
  }
};
```

3. **Update Backend Code** to read from custom claims:

```python
# In routes.py, update the profile endpoint:
auth0_info = {
    'sub': auth0_sub,
    'email': g.current_user.get('https://your-app.com/email') or g.current_user.get('email'),
    'name': g.current_user.get('https://your-app.com/name') or g.current_user.get('name')
}
```

### Option 2: Use Auth0 Management API (Current Implementation)

The current implementation tries to fetch user data from Auth0 Management API when not available in the JWT.

#### Required Environment Variables:
```bash
AUTH0_MGMT_CLIENT_ID=your-management-client-id
AUTH0_MGMT_CLIENT_SECRET=your-management-client-secret
```

#### Steps to Get Management API Credentials:

1. **Go to Auth0 Dashboard** → Applications → Create Application
2. **Choose "Machine to Machine Applications"**
3. **Select "Auth0 Management API"**
4. **Grant scopes**: `read:users`, `read:user_idp_tokens`
5. **Copy Client ID and Secret** to your environment variables

### Option 3: Use Auth0 UserInfo Endpoint

Fetch user data from Auth0's UserInfo endpoint using the access token.

#### Implementation:
```python
def get_user_info_from_auth0(access_token, auth0_domain):
    """Fetch user info from Auth0 UserInfo endpoint."""
    try:
        userinfo_url = f'https://{auth0_domain}/userinfo'
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(userinfo_url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching user info: {e}")
    
    return None
```

## Testing the Fix

1. **Restart your backend server**
2. **Login to your application**
3. **Go to the profile page**
4. **Check that name and email are now displayed**

## Debug Information

The backend now includes debug logging to help troubleshoot:
- Check backend logs for "DEBUG: Fetched user info from Auth0" messages
- Verify that environment variables are set correctly
- Ensure Auth0 Management API credentials have proper permissions

## Recommended Approach

**Option 1 (Custom Claims)** is recommended because:
- No additional API calls required
- Faster response times
- Simpler implementation
- More secure (no need for Management API credentials)

The current implementation (Option 2) provides a fallback that will work even without custom claims configuration.
