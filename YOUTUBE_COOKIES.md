# YouTube Cookie Authentication

## Problem
YouTube may require authentication to download videos, especially when accessed from server IPs. This prevents yt-dlp from extracting video content.

## Solution
Export your browser cookies and provide them to the application.

### For Local Development

**Option A: Use Environment Variable (Recommended)**

Set `YTDLP_USE_BROWSER_COOKIES=true` in your `.env` file to enable automatic browser cookie detection:
```bash
YTDLP_USE_BROWSER_COOKIES=true
```

The application will automatically try to use cookies from Chrome, Firefox, Safari, or Edge.

**Option B: Use Cookie File**

Export cookies and point to the file:
```bash
# Export cookies using yt-dlp
yt-dlp --cookies-from-browser chrome --cookies cookies.txt "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Set environment variable
YTDLP_COOKIE_FILE=/path/to/cookies.txt
```

### For Production/Railway Deployment

#### Step 1: Export Cookies from Browser

**Option A: Using Browser Extension (Recommended)**
1. Install "Get cookies.txt LOCALLY" extension:
   - Chrome: https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc
   - Firefox: https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/

2. Visit YouTube.com and make sure you're logged in
3. Click the extension icon and click "Export" to download `cookies.txt`

**Option B: Using yt-dlp Command**
```bash
# This exports cookies from your browser
yt-dlp --cookies-from-browser chrome --cookies cookies.txt https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

#### Step 2: Deploy Cookies to Railway

1. Base64 encode your cookies file:
```bash
base64 -i cookies.txt -o cookies.b64
# On macOS, use: base64 -i cookies.txt > cookies.b64
# On Linux, use: base64 -w 0 cookies.txt > cookies.b64
```

2. In Railway dashboard:
   - Go to your backend service
   - Click on "Variables" tab
   - Add new variable:
     - Name: `YTDLP_COOKIES_BASE64`
     - Value: (paste the entire contents of cookies.b64 as a single line)
   - Save the variable

3. Railway will automatically redeploy with the new cookies

That's it! The application will automatically decode and use the cookies.

**Alternative: Store in File System**

If your deployment has persistent storage:
1. Upload `cookies.txt` to your server
2. Set environment variable:
   ```
   YTDLP_COOKIE_FILE=/path/to/cookies.txt
   ```

### Cookie Expiration

Cookies typically expire after a few months. If you start seeing authentication errors again:
1. Export fresh cookies from your browser
2. Update the environment variable in Railway
3. Redeploy the application

### Security Note

⚠️ **Important**: Cookies contain authentication tokens. Keep them secure:
- Never commit `cookies.txt` to git
- Use environment variables for production
- Rotate cookies periodically
- Use a dedicated YouTube account if possible

### Note on Cookie Requirement

Most YouTube videos work without authentication. You only need cookies if:
- You encounter "Sign in to confirm you're not a bot" errors
- The video is age-restricted
- The video is private or unlisted
- YouTube blocks your server's IP address

For production use on Railway, it's recommended to set up cookies to avoid intermittent failures.
