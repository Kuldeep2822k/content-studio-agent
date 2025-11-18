# Get Free SerpAPI Key for Real Web Search

To enable real web search in your Content Studio Agent, follow these steps:

## Step 1: Sign Up for SerpAPI

1. Go to: https://serpapi.com/signup
2. Create a free account (email + password)
3. Confirm your email

## Step 2: Get Your API Key

1. Log in to https://serpapi.com/dashboard
2. Copy your API key from the dashboard

## Step 3: Add to .env

Edit your `.env` file and replace:

```
SERPAPI_API_KEY=your_serpapi_key_here
```

with your actual key:

```
SERPAPI_API_KEY=your_actual_key_from_dashboard
```

## Step 4: Test It

Run the demo again:

```powershell
.venv\Scripts\python demo.py
```

Now when you enter a topic, it will search the web in real-time instead of using placeholder data.

---

**Free tier:** 100 searches/month (plenty for testing and your capstone demo)
