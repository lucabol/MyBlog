# My Blog

This is my blog, built with Python and hosted on Netlify.

[![Netlify Status](https://api.netlify.com/api/v1/badges/fdf61c15-1bd9-493a-a4b1-f829d6e77780/deploy-status)](https://app.netlify.com/sites/lucabol/deploys)

## Building Locally

1. Install Python dependencies:
```bash
pip install -r src/requirements.txt
```

2. Build the site:
```bash
python src/generate_blog.py
```

3. For development, you can use the dev server:
```bash
python src/devserver.py
```

## Deployment

The site is automatically deployed to Netlify whenever changes are pushed to the main branch. The GitHub Actions workflow:

1. Builds the site
2. Creates a zip file of the built site
3. Deploys it to Netlify

### Setting up Deployment

To enable automatic deployments, you need to add two secrets to your GitHub repository:

1. `NETLIFY_SITE_ID` - Found in Netlify under Site Settings > General > Site details > Site ID
2. `NETLIFY_AUTH_TOKEN` - Create at https://app.netlify.com/user/applications#personal-access-tokens
