# Repo Search & Replace Utility

Utility to search a repository and performing a search & replace on files matching the file_pattern input

## Inputs

## `file_pattern`

**Required** file search pattern (plaintext or regex) Default `*`, meaning searches all files.

## `search_string`

**Required** string to search for

## `replace_string`

**Required** replacment string

## Outputs

## `change_log`

log of replacements

## Example usage

uses: actions/search-replace-repo-util@v2'
description: 'search repo files matching the file_pattern input, and then perform a search & replace
with:
  file_pattern: `/.*\.tf/`
  search_string: `github.com/[GHEC_Y]`
  replace_string: `github.com/[GHEC_X]`