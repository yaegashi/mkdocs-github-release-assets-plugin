import os
import re
import requests
from datetime import datetime
from ghapi.all import GhApi, paged
from . import logger


class GitHubReleaseAssets:
    def __init__(self, dest_dir: str, owner: str, repo: str, token: str | None = None, gh_host: str | None = None):
        self.dest_dir = dest_dir
        self.owner = owner
        self.repo = repo
        self.token = token
        self.gh_host = gh_host
        self.api = GhApi(token=token, gh_host=gh_host)
        self.releases = []
        self.indexes = []
        self.assets = []

    @property
    def uris(self):
        return self.indexes + self.assets

    def get_releases(self, release_filter=None, asset_filter=None) -> None:
        releases = []
        for page in paged(self.api.repos.list_releases, self.owner, self.repo, per_page=100):
            releases += page
        if release_filter:
            pat = re.compile(release_filter)
            releases = [r for r in releases if pat.search(r.tag_name)]
        if asset_filter:
            pat = re.compile(asset_filter)
            for r in releases:
                r.assets = [a for a in r.assets if pat.search(a.name)]
        self.releases = releases

    def update_indexes(self) -> None:
        logger.info(f'Creating {self.dest_dir}')
        os.makedirs(self.dest_dir, exist_ok=True)
        self.indexes = ['index.md']
        logger.info(f'Writing index.md')
        with open(os.path.join(self.dest_dir, 'index.md'), 'w') as f1:
            f1.write(f'# {self.owner}/{self.repo} releases\n\n')
            for r in self.releases:
                release_dir = os.path.join(self.dest_dir, r.tag_name)
                os.makedirs(release_dir, exist_ok=True)
                index_uri = os.path.join(r.tag_name, 'index.md')
                self.indexes.append(index_uri)
                logger.info(f'Writing {index_uri}')
                with open(os.path.join(self.dest_dir, index_uri), 'w') as f2:
                    f2.write(f'# {r.name}\n\n')
                    f2.write(f'{r.body}\n\n')
                    if r.assets:
                        f2.write('## Assets\n\n')
                        f2.write('|Name|Size|Date|\n')
                        f2.write('|:-|-:|:-|\n')
                        for a in r.assets:
                            f2.write(
                                f'| [{a.name}]({a.name})|{a.size}|{a.updated_at}|\n')
                f1.write(
                    f'- [{r.tag_name}]({index_uri}) ({r.created_at})\n')

    def update_assets(self) -> None:
        self.assets = []
        headers = {'Accept': 'application/octet-stream'}
        if self.token:
            headers['Authorization'] = f'token {self.token}'
        for release in self.releases:
            release_dir = os.path.join(self.dest_dir, release.tag_name)
            os.makedirs(release_dir, exist_ok=True)
            for asset in release.assets:
                asset_uri = os.path.join(release.tag_name, asset.name)
                asset_dest_path = os.path.join(self.dest_dir, asset_uri)
                self.assets.append(asset_uri)
                asset_timestamp = datetime.strptime(
                    asset.updated_at, '%Y-%m-%dT%H:%M:%SZ').timestamp()
                if os.path.exists(asset_dest_path):
                    size = os.path.getsize(asset_dest_path)
                    timestamp = os.path.getmtime(asset_dest_path)
                    if size == asset.size and timestamp >= asset_timestamp:
                        logger.info(f'Downloading {asset_uri} (skipped)')
                        continue
                logger.info(f'Downloading {asset_uri}')
                response = requests.get(asset.url, headers=headers)
                response.raise_for_status()
                with open(asset_dest_path, 'wb') as f:
                    f.write(response.content)
                os.utime(asset_dest_path, (asset_timestamp, asset_timestamp))
