# Notes on the Current Data Flow

`update-2023` branch

## `10-install-dependencies`

- Update pip, setuptools, wheel (overkill!)
- Install pinned requirements

## `20-prepare-files`

- Clear Markdown output
- Rename old f8.list (not used after this)
- Unzip entry-point JSON payloads and COPY to `.old`
- Unzip RSS JSON payload WITHOUT copy

## `30-retrieve-package-data`

- Pull PyPI JSON Simple API listing
- Find all projects with `flake8`, add any `ADDL_PKGS` and remove any `SKIP_PKGS`
- Write the complete list of these to `f8.list`
  - These are ALL MATCHING PACKAGES. All of these should be checked for entry points and included in the Markdown if they have them.
  - Currently, it _appears_ that network load is being reduced by only rechecking the entry points of new and updated packages.
- Retrieve a mapping of project name to project version from the prior entry points JSON hives
- Create a set of PEP 503 normalized package names from the prior entry points JSON hives
- Using the PyPI JSON package API, create a mapping of the new list of project names to their versions
  - If JSON API pull is successful and a version found, store that found version
  - If the JSON API 404s, take it as a signal that the package has been deleted from PyPI, and DO NOT INCLUDE in the new {project: version} mapping
  - If the JSON API web request times out 5x, use a dummy v0.0 version
    - **Might be better for this to be more picky? Error out the script/workflow? At minimum, report it more aggressively?**
  - If the returned JSON does not have a `["info"]["version"]` content path, use a dummy v0.0 version
    - **Might be better for this to be more picky? Error out the script/workflow? At minimum report it more aggressively?**
  - If any other `Exception` occurrs, use a dummy v0.0 version
    - **Almost *certainly* should be more picky here!**
- Determine new projects based upon the PEP 503 normalized name of the new project not matching the PEP 503 normalized name of any old project.
- Determine "updated" projects per:
  - PEP 503 normalized name of a new package *does* match the PEP 503 normalized name of an old package; and
  - Canonicalized version of the new package is *not equal* to that of the PEP 503 normalization-matched old package.
  - Is this what we want?
    - There are at least two uses of this information:
      - Deciding what to check for new/updated entry point information
      - Deciding what to tweet/RSS feed about
    - It *does* make sense to be cautious and recheck the entry point information if the version number is different *at all*.
      - The main situation I can think of that would lead to this is a newer version either being deleted or being yanked. In this case, we:
        - Definitely want to update the Markdown tables to reflect whatever the now-most-recent package version is (if the entry points changed in the version that is now deleted/yanked, then we want to undo that change post-delete/-yank).
        - Definitely do not want to declare this changed version as a New or Upgraded package version for the purposes of public notification. **If anything, we would want to declare it as a *Downgraded* package version.**
