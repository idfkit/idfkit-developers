"""Hand the templates the vendored identity fragments that have to be inlined (008-FR-020).

`docs/identity/` is vendored from idfkit-brand at `[tool.idfkit.identity] level` and served as the
tag wrote it: `mkdocs.yml` links its stylesheets, pastes its palette, and points `theme.logo` and
`theme.favicon` at its files. Two of its files cannot reach the page that way, because what they
carry has to be inside the page's own markup or inside another plugin's configuration. This hook
reads each one at build time and puts the result in `config.extra`, so that nothing under
`docs/overrides/` or in `mkdocs.yml` restates a colour, a font or a path the derivation owns.

    identity_head    `hosts/<host>/head.html`: the favicon set, both theme colours and the
                     social image. Its paths are relative to the host's root, and this site serves
                     the directory at `identity/hosts/<host>/` (the derivation contract lets a
                     consumer rewrite the prefix at adoption; the vendored file is untouched).
                     The paths come out site-root-relative, and `main.html` makes them
                     page-relative with `base_url`, as the theme does for its own assets.
    identity_social  `material/social.yml`: the social plugin's card options, written into the
                     plugin's configuration here because `mkdocs.yml` is identity-bearing and may
                     carry no colour literal (touchpoint-check.md, assertion 4).

Every read is under `config.docs_dir`. Nothing here computes a path above `docs/`, so the portable
build, which copies `docs/` and `mkdocs.yml` and nothing else, sees the same files.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

_HOST_HREF = 'href="/'
_SOCIAL_PLUGIN = "social"
_CARD_OPTIONS = "cards_layout_options"


def _served_directory(site_url: str) -> tuple[str, str]:
    """The host the site is published on, and the site-root-relative path its host directory is served at."""
    host = urlparse(site_url).netloc
    if not host:
        raise SystemExit(
            f"site_url {site_url!r} names no host, so the identity hook cannot find docs/identity/hosts/<host>/"
        )
    return host, f"identity/hosts/{host}/"


def _read(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(
            f"{path} is missing. docs/identity/ is vendored from idfkit-brand at [tool.idfkit.identity] level; "
            "adopt the tag through the identity-adopt skill rather than writing the file by hand."
        )
    return path.read_text(encoding="utf-8")


def _rewrite_head(head: str, site_url: str, served: str) -> str:
    """Prefix the host-root paths in head.html with where this site serves the directory.

    Relative `href="/x"` becomes `href="identity/hosts/<host>/x"`, for the template to make
    page-relative. The absolute social-image address keeps its origin and gains the same prefix.
    """
    origin = site_url.rstrip("/")
    head = head.replace(_HOST_HREF, f'href="{served}')
    return head.replace(f'content="{origin}/', f'content="{origin}/{served}')


def on_config(config: Any) -> Any:
    """Read the two fragments out of the vendored tree and hand them to the templates."""
    identity = Path(config.docs_dir) / "identity"
    host, served = _served_directory(config.site_url or "")
    config.extra["identity_head"] = _rewrite_head(
        _read(identity / "hosts" / host / "head.html"), config.site_url, served
    ).strip()
    social: dict[str, Any] = yaml.safe_load(_read(identity / "material" / "social.yml")) or {}
    options = social.get(_CARD_OPTIONS)
    if not isinstance(options, dict):
        raise SystemExit(f"docs/identity/material/social.yml carries no {_CARD_OPTIONS} mapping")
    # The collection keys a theme-provided plugin by its namespaced name (`material/social`), so
    # the name is matched on its last segment. Not finding it is an error, not a skip: the options
    # have nowhere else to go, and a silent skip renders the cards in the theme's default colour.
    names = [name for name in config.plugins if name.rsplit("/", 1)[-1] == _SOCIAL_PLUGIN]
    if not names:
        raise SystemExit(
            f"the {_SOCIAL_PLUGIN} plugin is not configured, so {_CARD_OPTIONS} from social.yml cannot be applied"
        )
    # Read lazily by the plugin, per page, so writing it here after the plugin's own on_config is
    # in time. The site-level mapping is replaced whole: the derivation owns every key.
    config.plugins[names[0]].config[_CARD_OPTIONS] = dict(options)
    return config
