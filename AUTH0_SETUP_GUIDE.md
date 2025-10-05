# Auth0 Configuration Guide

## Option 1: Configure Auth0 Custom Claims (Recommended)

This is the simplest approach that adds user name and email directly to the JWT token.

### Step 1: Create a Post-Login Action

1. **Go to Auth0 Dashboard** → **Actions** → **Library**
2. **Click "Create Action"**
3. **Choose "Build from scratch"**
4. **Name it**: "Add User Profile to Token"
5. **Trigger**: Select "Post Login"
6. **Copy and paste this code**:

```javascript
exports.onExecutePostLogin = async (event, api) => {
  const namespace = 'https://kora-travel.com/';
  
  // Access user information from the event
  const user = event.user || event.user_metadata || {};
  
  if (user) {
    // Add user profile information to the JWT token
    api.idToken.setCustomClaim(`${namespace}email`, user.email);
    api.idToken.setCustomClaim(`${namespace}name`, user.name);
    api.idToken.setCustomClaim(`${namespace}nickname`, user.nickname);
    api.idToken.setCustomClaim(`${namespace}picture`, user.picture);
  }
};
```

6. **Click "Deploy"**

### Step 2: Add the Action to Your Login Flow

1. **Go to Actions** → **Flows** → **Login**
2. **Click "Add Action"**
3. **Select "Add User Profile to Token"**
4. **Click "Apply"**

### Step 3: Update Backend Code

Update the profile endpoint in `backend/app/api/routes.py` to read from custom claims:

```python
# In the get_user_profile function, replace this section:
jwt_email = g.current_user.get('email')
jwt_name = g.current_user.get('name')

# With this:
jwt_email = g.current_user.get('https://kora-travel.com/email') or g.current_user.get('email')
jwt_name = g.current_user.get('https://kora-travel.com/name') or g.current_user.get('name')
```

## Option 2: Configure Auth0 Management API (Alternative)

If you prefer to use the Management API approach, you'll need to:

### Step 1: Create a Machine-to-Machine Application

1. **Go to Auth0 Dashboard** → Applications → Create Application
2. **Name**: "KORA Management API"
3. **Choose**: "Machine to Machine Applications"
4. **Select**: "Auth0 Management API"
5. **Grant scopes**: 
   - `read:users`
   - `read:user_idp_tokens`
6. **Copy the Client ID and Secret**

### Step 2: Add Environment Variables

Add these to your backend `.env` file:

```bash
AUTH0_MGMT_CLIENT_ID=your-management-client-id
AUTH0_MGMT_CLIENT_SECRET=your-management-client-secret
```

### Step 3: The backend code is already set up to use this approach!

## Testing the Configuration

1. **Restart your backend server**
2. **Log out and log back in** (to get a new JWT token with the custom claims)
3. **Go to the profile page**
4. **Check that name and email are now displayed**

## Debugging

If it's not working:

1. **Check the JWT token** in your browser's developer tools:
   - Go to Application/Storage → Local Storage
   - Look for the `auth_token` key
   - Decode the JWT at [jwt.io](https://jwt.io) to see what claims are included

2. **Check backend logs** for debug messages about user info

3. **Verify the Action is deployed** in Auth0 Dashboard → Actions

## Recommended Approach

**Option 1 (Custom Claims)** is recommended because:
- ✅ No additional API calls required
- ✅ Faster response times
- ✅ Simpler implementation
- ✅ More secure (no need for Management API credentials)
- ✅ Works with the current backend code

The current backend implementation will automatically use the custom claims if they're available, and fall back to "Not available" if they're not.
