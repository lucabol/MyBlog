# My Blog

This is my blog, built with Python and hosted on Netlify.

[![Netlify Status](https://api.netlify.com/api/v1/badges/fdf61c15-1bd9-493a-a4b1-f829d6e77780/deploy-status)](https://app.netlify.com/sites/lucabol/deploys)

## Building and running locally

Running the webserver automatically builds the website:

```bash
uv run src/devserver.py
```

## Deployment

The site is automatically deployed to Netlify in these cases:
- When changes are pushed to the main branch
- When pull requests are created or updated (for testing)
- When manually triggered from the GitHub Actions UI

The GitHub Actions workflow:

1. Builds the site
2. Creates a zip file of the built site
3. Deploys it to Netlify

### Setting up Deployment

To enable automatic deployments, you need to add two secrets to your GitHub repository:

1. `NETLIFY_SITE_ID` - Found in Netlify under Site Settings > General > Site details > Site ID
2. `NETLIFY_AUTH_TOKEN` - Create at https://app.netlify.com/user/applications#personal-access-tokens

## Image Generation

Story images in this blog have been generated with [InvokeAI](https://github.com/invoke-ai/InvokeAI) using the [Flux.dev](https://huggingface.co/black-forest-labs/FLUX.1-dev) model. The generation process involved using the text of each story as a prompt, with the following style modifier appended:

```
black and white pencil drawing except for a small red sun on the horizon, off-center composition, cross-hatching for shadows, bold strokes, textured paper. sketch+++
```
