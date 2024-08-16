You can activate the plugin by adding `github-release-assets` with options in `mkdocs.yml`:

```yaml
site_name: MkDocs github-release-assets plugin
plugins:
  - techdocs-core:
  - github-release-assets:
      owner: yaegashi
      repo: mkdocs-github-release-assets-plugin
      base_uri: releases
      token: !ENV GITHUB_TOKEN
      nav_title: Releases

nav:
  - Introduction: index.md
  - Configuration: config.md
  - Releases: []
```

|Option|Description|
|-|-|
|`owner` `repo`|Specify the repository to get releases: `owner/repo`.|
|`dest_dir`|Directory path for the asset download destination.  Specify a fixed location to cache them.|
|`base_uri`|Directory name prefixed to all releases.|
|`gh_host`|URL for GitHub Enterprise Server.  None for `https://github.com`.|
|`token`|Token string to access the GitHub API.  No token can cause hitting the API limit.|
|`nav_title`|Navigation title to replace with the release index.|
|`release_filter`|Regex string to specify releases to include by name.|
|`asset_filter`|Regex string to specify assets to include by name.|
