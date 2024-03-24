# Deploying Python Shinylive App via GitHub Pages through GitHub Actions

This repository demonstrates how to deploy a [Python Shinylive app](https://shiny.posit.co/py/docs/shinylive.html) using GitHub Actions and GitHub Pages.

If you're interested in an R version, you can find it: [here](https://github.com/coatless-tutorials/convert-shiny-app-r-shinylive).

## Background

We'll be working with an app that was initially developed in R Shiny and later translated to [Shiny for Python](https://shiny.posit.co/py/). The original R Shiny App's source code originated from a [StackOverflow Question](https://stackoverflow.com/questions/78160039/using-shinylive-to-allow-deployment-of-r-shiny-apps-from-a-static-webserver-yiel) by [Faustin Gashakamba](https://stackoverflow.com/users/5618354/faustin-gashakamba), which led to the creation of the [first tutorial on deploying an R Shiny app using R Shinylive](https://github.com/coatless-tutorials/convert-shiny-app-r-shinylive).

## Deploying Automatically with GitHub Actions

### Serving a Website from a GitHub Repository

We recommend against using the [`gh-pages` branch deployment technique](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site#publishing-from-a-branch) for sharing the app on GitHub Pages. Instead, opt for the [GitHub Actions approach](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site#publishing-with-a-custom-github-actions-workflow). This method is preferred because it doesn't store conversion artifacts inside the repository, and it allows Shinylive apps to be deployed up to the [GitHub Pages maximum size limit of about 1 GB](https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages#usage-limits).

### Project Layout

For this to work, we're advocating for a repository structure of: 

```sh
.
├── .github
│   └── workflows
│       └── build-and-deploy-py-shinylive-app.yml
├── README.md
├── app.py
├── requirements-ci.txt
└── requirements-dev.txt
```

With this file structure, we can place any Python package requirements into two requirement files:

1. [`requirements-dev.txt`](requirements-dev.txt): Handles local development requirements like developing the Shiny for Python app outside of Python Shinylive as well as converting with a local copy of `shinylive`.
2. [`requirements-ci.txt`](requirements-ci.txt): Describes the python packages to install and cache for faster iterations.

It may seem odd to have two separate `requirements*.txt` files, however, the actual conversion of the Shiny for Python app into a Python shinylive app requires just the `shinylive` python package. 

> [!IMPORTANT]
>
> Please **avoid** using `requirements.txt` since
> [`py-shinylive` will attempt to install packages](https://github.com/posit-dev/py-shinylive/issues/17)
> listed in that file for the app. This is problematic as `py-shinylive` itself has a dependency
> that does not have a Pyodide-compiled Python package wheel causing the app to fail.

With this said, the source for the Shiny for Python app can be placed into the [`app.py`](app.py) file.  Moreover, we can use the following GitHub Action in [`.github/workflows/build-and-deploy-py-shinylive-app.yml`](.github/workflows/build-and-deploy-py-shinylive-app.yml) to build and deploy the shinylive app every time the repository is updated.

## GitHub Action Workflow for Converting and Deploying

The following workflow contains a single step that encompasses both the build and deploy phases. We use the `requirements-ci.txt` discussed above as the `pip` package cache to speed up the conversion and, subsequently, the deployment of the Python Shinylive app. For more details about customizing the conversion step or the deployment step, please see the two notes that immediately follow from the workflow.

```yaml
on:
    push:
      branches: [main, master]
    release:
        types: [published]
    workflow_dispatch: {}
   
name: demo-py-shinylive-app

jobs:
    build-and-deploy-py-shinylive-app:
      runs-on: ubuntu-latest
      # Only restrict concurrency for non-PR jobs
      concurrency:
        group: py-shinylive-website-${{ github.event_name != 'pull_request' || github.run_id }}
      # Describe the permissions for obtain repository contents and 
      # deploying a GitHub pages website for the repository
      permissions:
        contents: read
        pages: write
        id-token: write
      steps:
        # Obtain the contents of the repository
        - name: "Check out repository"
          uses: actions/checkout@v4

        # Install Python on the GitHub Actions worker
        - name: "Setup Python"
          uses: actions/setup-python@v5
          with:
            python-version: '3.12'
            cache: 'pip' # caching pip dependencies
            cache-dependency-path: 'requirements-ci.txt'

        # Install the dependencies for the py-shinylive app
        - name: "Setup Python dependency for Shinylive App export"
          shell: bash
          run: pip install -r requirements-ci.txt
  
        # Export the current working directory as the py-shiny app
        # using the version of the py-shinylive package
        - name: Create Python Shinylive App from working directory files
          shell: bash
          run: |
           shinylive export . _site

        # Upload a tar file that will work with GitHub Pages
        # Make sure to set a retention day to avoid running into a cap
        # This artifact shouldn't be required after deployment onto pages was a success.
        - name: Upload Pages artifact
          uses: actions/upload-pages-artifact@v2
          with: 
            retention-days: 1
        
        # Use an Action deploy to push the artifact onto GitHub Pages
        # This requires the `Action` tab being structured to allow for deployment
        # instead of using `docs/` or the `gh-pages` branch of the repository
        - name: Deploy to GitHub Pages
          id: deployment
          uses: actions/deploy-pages@v2
```

#### Conversion Assumptions

When exporting the Shiny for Python app, we assume:

1. The app is located in the working directory, denoted by `.`.
2. The deployment folder or what should be shown on the web is `_site`.

If these assumptions don't align with your setup, please modify the conversion step accordingly.

```yaml
  - name: Create Python Shinylive App from working directory files
    shell: bash
    run: |
      shinylive export . _site
```

#### Customize Deployment Path

The output directory `_site` for the converted Shinylive app is used as it's the default path for the [`upload-pages-artifact`](https://github.com/actions/upload-pages-artifact) action. You can change this by supplying a `path` parameter under `with` in the "Upload Pages artifact" step, e.g.

```yaml
- name: Upload Pages artifact
  uses: actions/upload-pages-artifact@v2
  with: 
    retention-days: 1
    path: "new-path-here"
```





## Enabling GitHub Pages Deployment

To enable deployment through GitHub Actions to GitHub Pages:

1. Navigate to the repository's **Settings** page.
2. Select **Pages** on the left sidebar.
3. Choose the **GitHub Actions** option in the **Source** drop-down under the Build and Deployment section.
4. Ensure that **Enforced HTTPS** is checked.

[![Example annotation of the repository's Settings page for GitHub Actions deployment][1]][1]

## Working Example

You can view the example shinylive-ified [app.py source included in the repository here:

<https://tutorials.thecoatlessprofessor.com/convert-py-shiny-app-to-py-shinylive-app/>

Keep in mind that the exported app size is not mobile-friendly (approximately 38 MB).

If you are data constrained, you can see the app in this screenshot: 

[![Example of the working Python Shinylive app][2]][2]

Moreover, you can view one of the deployment apps sizes here: 

[![Summary of the deployment of the Python Shinylive app][3]][3]

# Fin

That's it! You've successfully learned how to deploy a Python Shinylive app via GitHub Pages using GitHub Actions.

  [1]: https://i.imgur.com/lGkZNeM.png 
  [2]: https://i.imgur.com/xouALeM.png
  [3]: https://i.imgur.com/krmVxIF.png
