import logging
from typing import Any, MutableMapping


class _PluginLogger(logging.LoggerAdapter):
    def __init__(self, prefix: str, logger: logging.Logger):
        super().__init__(logger, {})
        self.prefix = prefix

    def process(self, msg: str, kwargs: MutableMapping[str, Any]) -> tuple[str, Any]:
        return f"{self.prefix}: {msg}", kwargs


logger = _PluginLogger('github_release_assets', logging.getLogger(
    "mkdocs.plugins.github_release_assets"))
