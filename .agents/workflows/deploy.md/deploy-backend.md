---
description: Deploy backend to Render free tier
---

1. Run the validate workflow first
2. Ensure requirements.txt is up to date
3. Verify gunicorn is in requirements.txt
4. Create backend/Procfile with: web: gunicorn "app:create_app()" --bind 0.0.0.0:$PORT
5. Tell user to go to https://dashboard.render.com/
6. Create Web Service connected to GitHub repo
7. Set root directory to backend
8. Set build command: pip install -r requirements.txt
9. Set start command: gunicorn "app:create_app()" --bind 0.0.0.0:$PORT
10. Add env vars from .env.example
11. For Redis use Upstash free tier at https://upstash.com
12. Hit deployed_url/api/health to verify
13. Update extension API base URL and CORS origins
