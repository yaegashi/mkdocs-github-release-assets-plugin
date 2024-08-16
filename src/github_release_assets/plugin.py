import os
import tempfile
from mkdocs.plugins import BasePlugin
from mkdocs.config import Config
from mkdocs.config import config_options as opt
from mkdocs.structure.files import File, Files
from mkdocs.config.defaults import MkDocsConfig

from . import logger
from .github import GitHubReleaseAssets


class PluginConfig(Config):
    owner = opt.Optional(opt.Type(str))
    repo = opt.Optional(opt.Type(str))
    token = opt.Optional(opt.Type(str))
    gh_host = opt.Optional(opt.URL())
    dest_dir = opt.Optional(opt.Type(str))
    base_uri = opt.Optional(opt.Type(str))
    release_filter = opt.Optional(opt.Type(str))
    asset_filter = opt.Optional(opt.Type(str))
    nav_title = opt.Optional(opt.Type(str))
    enabled = opt.Type(bool, default=True)


class GitHubReleaseAssetsPlugin(BasePlugin[PluginConfig]):
    def __init__(self) -> None:
        super().__init__()

    def update_config_nav(self, nav: list | dict) -> None:
        if isinstance(nav, list):
            for n in nav:
                self.update_config_nav(n)
        elif isinstance(nav, dict):
            if self.config.nav_title in nav.keys():
                src_uri = 'index.md'
                if self.config.base_uri:
                    src_uri = os.path.join(self.config.base_uri, src_uri)
                n = [{'Index': src_uri}]
                for release in self.ghra.releases:
                    src_uri = os.path.join(release.tag_name, 'index.md')
                    if self.config.base_uri:
                        src_uri = os.path.join(self.config.base_uri, src_uri)
                    n.append({release.tag_name: src_uri})
                nav[self.config.nav_title] = n

    def on_config(self, config: Config) -> PluginConfig:
        if not self.config.enabled:
            return config
        self.dest_dir = self.config.dest_dir
        if not self.dest_dir:
            self.dest_dir = tempfile.mkdtemp()
        self.ghra = GitHubReleaseAssets(dest_dir=self.dest_dir,
                                        owner=self.config.owner, repo=self.config.repo,
                                        token=self.config.token, gh_host=self.config.gh_host)
        return config

    def on_files(self, files: Files, config: MkDocsConfig) -> Files | None:
        if not self.config.enabled:
            return files
        self.ghra.get_releases(self.config.release_filter,
                               self.config.asset_filter)
        self.ghra.update_indexes()
        self.ghra.update_assets()
        for uri in self.ghra.uris:
            src_uri = uri
            if self.config.base_uri:
                src_uri = os.path.join(self.config.base_uri, uri)
            abs_src_path = os.path.join(self.dest_dir, uri)
            logger.info(f'Adding src_uri={uri} abs_src_path={abs_src_path}')
            file = File.generated(
                config=config, src_uri=src_uri, abs_src_path=abs_src_path)
            files.append(file)
        if self.config.nav_title:
            self.update_config_nav(config.nav)
        files
