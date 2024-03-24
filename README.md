# Deploying Python Shinylive App via GitHub Pages through GitHub Actions

This repository demonstrates how to deploy a [Python Shinylive app](https://shiny.posit.co/py/docs/shinylive.html) using GitHub Actions and GitHub Pages.

Interested in seeing an R version? [Click here!](https://github.com/coatless-tutorials/convert-shiny-app-r-shinylive).

We're using an app that was translated from R Shiny over to [Shiny for Python](https://shiny.posit.co/py/). The initial R Shiny App source code came from a [StackOverflow Question](https://stackoverflow.com/questions/78160039/using-shinylive-to-allow-deployment-of-r-shiny-apps-from-a-static-webserver-yiel) by [Faustin Gashakamba](https://stackoverflow.com/users/5618354/faustin-gashakamba) that spawned the [first tutorial on deploying an R Shiny app using R Shinylive](https://github.com/coatless-tutorials/convert-shiny-app-r-shinylive). 

## Deploying Automatically with GitHub Actions

### Serving a Website from a GitHub Repository

Please **avoid** using the [`gh-pages` branch deployment technique](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site#publishing-from-a-branch) for sharing the app on GitHub pages. 

Instead, opt for the [GitHub Actions approach](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site#publishing-with-a-custom-github-actions-workflow), which is preferred because it doesn't store artifacts from converting a Shiny for Python App into a Python Shinylive App inside the repository. Plus, this approach allows for Shinylive apps to be deployed up to the [GitHub Pages maximum of about 1 GB](https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages#usage-limits). 

### Project Layout

For this to work, we're advocating for a file structure of: 

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

With this file structure, we can place any requirements for local development inside of [`requirements-dev.txt`](requirements-dev.txt). That is, we're placing any packages required for the shiny app. For the GitHub Actions runner to correctly export the Shiny for Python app into a Python Shinylive App, we only need the `shinylive` python package. So, we'll use the [`requirements-ci.txt`](requirements-ci.txt) file in the GitHub Action workflow to install and cache the package for faster iterations.

> [!IMPORTANT]
>
> Please do **not** use `requirements.txt` as
> [py-shinylive will attempt to install packages](https://github.com/posit-dev/py-shinylive/issues/17)
> listed in that dependency file for the app. This is problematic as shinylive itself has a dependency
> that does not have a Pyodide-compiled Python package wheel causing the app to fail.

With this said, the source for the Shiny for Python app can be placed into the [`app.py`](app.py) file.  Moreover, we can use the following GitHub Action in [`.github/workflows/build-and-deploy-py-shinylive-app.yml`](.github/workflows/build-and-deploy-py-shinylive-app.yml) to build and deploy the shinylive app every time the repository is updated.

## GitHub Action Workflow for Building and Deploying

The following workflow contains a single step that encompasses both the build and deploy phases.

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

> [!NOTE]
>
> We make an assumption when exporting the Shiny for Python app about:
>
> 1. the app location is in the working directory, e.g. `.`; and,
> 2. the deployment folder or what should be shown on the web is `_site`
> 
> If this is not the case, please modified the step in the deployment recipe
> that contains: 
>
> ```sh
> shinylive export . _site
> ```
>

> [!NOTE]
>
> The output directory of `_site` for the converted shinylive app
> is used since it is the default path location for the
> [`upload-pages-artifact`](https://github.com/actions/upload-pages-artifact)
> action. This can be changed by supplying `path` parameter under `with` in the
> "Upload Pages artifact" step.
>
> ```yaml
>  uses: actions/upload-pages-artifact@v2
>  with: 
>   retention-days: 1
>   path: "new-path-here"
> ```

Deployment through the GitHub Actions to GitHub Pages requires it to be enabled on the repository by:

- Clicking on the repository's **Settings** page
- Selecting **Pages** on the left sidebar.
- Picking the **GitHub Actions** option in the **Source** drop-down under the Build and Deployment section.
- Ensuring that **Enforced HTTPS** is checked. 

[![Example annotation of the repository's Settings page for GitHub Actions deployment][1]][1]

## Working Example

You can view the example shinylive-ified [app.py](app.py) source included in the repository here:

<https://tutorials.thecoatlessprofessor.com/convert-py-shiny-app-to-py-shinylive-app/>

Though, please be warned that the exported app size is not mobile friendly (~>38 mb).

If you are data constrained, you can see the app in this screenshot: 

[![Example of the working Python Shinylive app][2]][2]

Moreover, you can view one of the deployment apps sizes here: 

[![Summary of the deployment of the Python Shinylive app][3]][3]


  [1]: https://i.imgur.com/xouALeM.png
  [2]: https://i.imgur.com/krmVxIF.png
  [3]: https://i.imgur.com/lGkZNeM.png
