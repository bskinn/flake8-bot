# Notes on the Current Data Flow

Based on `update-2023` branch, a/o [8c95577].

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
- Find all projects with `flake8`, add any `ADDL_PKGS` and remove any
  `SKIP_PKGS`
- Write the complete list of these to **`f8.list`**
  - These are ALL MATCHING PACKAGES. All of these should be checked for entry
    points and included in the Markdown if they have them.
  - Currently, it _appears_ that network load is being reduced by only rechecking the entry points of new and updated packages.
- Retrieve a mapping of project name to project version from the prior entry
  points JSON hives
- Create a set of PEP 503 normalized package names from the prior entry points
  JSON hives
- Using the PyPI JSON package API, create a mapping of the new list of project
  names to their versions
  - If JSON API pull is successful and a version found, store that found version
  - If the JSON API 404s, take it as a signal that the package has been deleted
    from PyPI, and DO NOT INCLUDE in the new {project: version} mapping
  - If the JSON API web request times out 5x, use a dummy v0.0 version
    - **Might be better for this to be more picky? Error out the
      script/workflow? At minimum, report it more aggressively?**
  - If the returned JSON does not have a `["info"]["version"]` content path, use
    a dummy v0.0 version
    - **Might be better for this to be more picky? Error out the
      script/workflow? At minimum report it more aggressively?**
  - If any other `Exception` occurrs, use a dummy v0.0 version
    - **Almost *certainly* should be more picky here!**
- Determine new projects based upon the PEP 503 normalized name of the new
  project not matching the PEP 503 normalized name of any old project.
- Determine "updated" projects per:
  - PEP 503 normalized name of a new package *does* match the PEP 503 normalized
    name of an old package; and
  - Canonicalized version of the new package is *not equal* to that of the PEP
    503 normalization-matched old package.
  - Is this what we want?
    - There are at least two uses of this information:
      - Deciding what to check for new/updated entry point information
      - Deciding what to tweet/RSS feed about
    - It *does* make sense to be cautious and recheck the entry point
      information if the version number is different *at all*.
      - The main situation I can think of that would lead to this is a newer
        version either being deleted or being yanked. In this case, we:
        - Definitely want to update the Markdown tables to reflect whatever the
          now-most-recent package version is (if the entry points changed in the
          version that is now deleted/yanked, then we want to undo that change
          post-delete/-yank).
        - Definitely do not want to declare this changed version as a New or
          Upgraded package version for the purposes of public notification. **If
          anything, we would want to declare it as a *Downgraded* package
          version.**
- Report the new and updated packages to `stdout`, mostly for CI logging
- Save newline-separated combined set of new/updated packages to
  **`f8_active.list`**
  - This is the source list for the `generate_eps_json` script, which means that
    script is limited to only pulling packages detected here as new/updated
    - I likely did this to reduce CI run time and network traffic to
      PyPI—`generate_eps_json` updates the new copy of the JSON hives in-place,
      so anything not detected as new/updated remains unchanged.
    - **With pip caching enabled on the workflow, this may no longer be
      necessary.**
      - One option would be to run `generate_eps_json` on the entire `f8.list`
        - This would ensure everything is current, and the pip caching would
          minimize network traffic because if a package is neither new nor
          updated, it'll just pull from cache
        - **This would also correctly handle *downgraded* packages**, which is
          an argument in its favor
        - **This would also cleanly drop *deleted* packages**, which is another
          argument in its favor
        - Even if it doesn't increase network traffic, **it still would increase
          CI run time, likely by 10x or more**
          - But this is only run 1x/day, so that run-time is probably not a huge
            deal?
      - Another option is to keep the current logic, but add handling to ensure
        that:
        - Deleted packages are removed from the JSON hive
        - Downgraded packages are updated correctly in the JSON hive
        - **This is likely the better option**
        - **Could we consolidate the new/updated/downgraded/deleted package
          detection, and not have to do it again in `extract_new_upd_pkgs.py`?**
        - **Could we add detection, tracking, and reporting of downgraded
          packages?**
        - **Could we add detection, tracking, and reporting of deleted packages
          (ones either removed from PyPI, or that have had all their
          distributions yanked/deleted)?**

## `40-generate-eps-json`

- Delete the old logfile from prior eps JSON creation step
- Loop over all entries in **`f8_active.list`**
  - List of packages identified as new/updated in `30-retrieve-package-data`
  - For each package:
    - Attempt a no-deps pip install
      - If failed, log the failure and skip the entry point retrieval attempt
    - If success, run `eps_json.py` to do the entry point retrieval
      - ***[What happens here? Any side effects? Fill this in!]***
    - Whether success or failure, proceed to uninstall the package
      - If failure, _hard stop the entire script_, because any entry points from
        the failed-to-uninstall package would pollute the associations with
        future packages under examination



[8c95577]: https://github.com/bskinn/flake8-bot/tree/8c95577f03b287c10b6c26aeb3cabed6884fbabc
