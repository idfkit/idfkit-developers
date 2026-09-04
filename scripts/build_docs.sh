#!/usr/bin/env bash

set -euo pipefail

# ------------------------------------------------------------------------------------------------
# BUILDING AGAINST AN UNRELEASED LIBRARY (003-FR-022, contracts/site-build.md "The override").
#
# Sometimes the page comes before the release it documents. IDFKIT_LIBRARY_DIR points the build at
# a local checkout of idfkit instead of the version [tool.idfkit.library] pins.
#
#     IDFKIT_LIBRARY_DIR=../idfkit ./scripts/build_docs.sh
#
# EXPLICIT ONLY. It is never a fallback that engages because a lookup failed. A fallback would let
# a build that should have stopped succeed quietly, which is the failure mode all four pinned
# levels exist to prevent, and it is why an unset variable here changes nothing rather than
# triggering a search for a sibling checkout.
#
# It announces itself, in the same words IDFKIT_GOVERNANCE_DIR, IDFKIT_TYPEDOC_JSON and
# --from-sibling use, because a maintainer should meet one idea rather than four.
#
# A BUILD UNDER IT IS NOT EVIDENCE ABOUT THE DECLARED LEVEL. It proves the pages render against a
# working tree nobody can install. docs.yml asserts the variable is unset in every job, so a green
# check is always a statement about a released version.
# ------------------------------------------------------------------------------------------------
if [ -n "${IDFKIT_LIBRARY_DIR:-}" ]; then
  if [ ! -d "${IDFKIT_LIBRARY_DIR}" ]; then
    echo "!! IDFKIT_LIBRARY_DIR is set to ${IDFKIT_LIBRARY_DIR}, which is not a directory." >&2
    echo "!! The override is explicit or nothing: it does not fall back to the pinned level." >&2
    exit 1
  fi
  declared=$(python3 -c "
import pathlib, tomllib
print(tomllib.loads(pathlib.Path('pyproject.toml').read_text())['tool']['idfkit']['library']['level'])
")
  echo "!! Reading ${IDFKIT_LIBRARY_DIR}, a working tree, instead of the pinned idfkit ${declared}."
  echo "!! This build is NOT evidence about the declared level. It shows that the pages render"
  echo "!! against a checkout nobody can install, which is a different and much weaker claim."
  # --with-editable on the run itself, not a `uv pip install` beforehand. `uv run` re-syncs the
  # environment from uv.lock, so an editable install done in a previous command is discarded before
  # mkdocs starts and the build silently uses the pinned release after announcing that it would
  # not. That is the exact failure this override exists to make impossible.
  OVERRIDE=(--with-editable "${IDFKIT_LIBRARY_DIR}")
else
  OVERRIDE=()
fi

# The four weather-browser files are part of the library's distribution and part of a page. They
# reached the page by symlink while the site lived inside the library; they are copied out of the
# installed distribution now, because a symlink does not survive a repository boundary.
#
# This runs before mkdocs on EVERY build, including the portable one, which is the point: the
# portable build copies docs/ and mkdocs.yml into a scratch directory with no src/ beside them, so
# a symlink there resolved to nothing. A missing asset stops the build rather than publishing a
# page with a broken widget.
uv run "${OVERRIDE[@]}" python scripts/copy_shipped_assets.py

uv run "${OVERRIDE[@]}" mkdocs build "$@"
# The unified site's host (001-FR-051). py.idfkit.com and js.idfkit.com are served by separate
# redirect-only builds and no longer publish this site (001-FR-056).
printf 'developers.idfkit.com\n' > site/CNAME
