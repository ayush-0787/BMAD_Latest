#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""
Fetch work item details from an on-prem TFS / Azure DevOps Server project.

Scopes a query one of four ways: an explicit ID list, an iteration path, an
area path, a tag, or a raw WIQL query — then fetches full field detail for
every matching work item. Auth is Basic (empty username + PAT as password).

The PAT is never accepted as a plain CLI argument (it would leak into shell
history and process listings). Supply it via stdin (default) or point
--pat-env at an environment variable that already holds it.

Usage:
    echo "$PAT" | python3 fetch_work_items.py --ids 9248686,9283193
    echo "$PAT" | python3 fetch_work_items.py --iteration-path "TWEHR\\ADP 26.2"
    echo "$PAT" | python3 fetch_work_items.py --tag "Release 26.3" --project TWEHR
    echo "$PAT" | python3 fetch_work_items.py --test-connection

Run with --help for the full option list.
"""

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_SERVER = "https://almdivapp1.rd.allscripts.com/tfs/projects/"
DEFAULT_PROJECT = "TWEHR"
DEFAULT_API_VERSION = "5.1"
DEFAULT_FIELDS = [
    "System.Id",
    "System.WorkItemType",
    "System.Title",
    "System.State",
    "System.Description",
    "System.Tags",
    "System.AreaPath",
    "System.IterationPath",
    "Microsoft.VSTS.TCM.ReproSteps",
    "Microsoft.VSTS.Common.ResolvedReason",
    "Microsoft.VSTS.Common.Priority",
]
BATCH_SIZE = 200


def escape_wiql_literal(value: str) -> str:
    """Escape a string for use inside a single-quoted WIQL literal."""
    return value.replace("'", "''")


def build_api_base(server: str, project: str, collection: str | None, api_base_override: str | None) -> str:
    """Construct the `_apis` base URL from server/collection/project, or use an explicit override."""
    if api_base_override:
        return api_base_override.rstrip("/")
    base = server.rstrip("/")
    if collection:
        base = f"{base}/{collection.strip('/')}"
    base = f"{base}/{project.strip('/')}"
    return f"{base}/_apis"


def build_wiql(project: str, ids=None, iteration_path=None, area_path=None, tag=None, raw_wiql=None) -> str | None:
    """Build a WIQL query string from the given scope. Returns None if scoping by explicit IDs (no query needed)."""
    if raw_wiql:
        return raw_wiql
    if ids:
        return None
    conditions = [f"[System.TeamProject] = '{escape_wiql_literal(project)}'"]
    if iteration_path:
        conditions.append(f"[System.IterationPath] UNDER '{escape_wiql_literal(iteration_path)}'")
    if area_path:
        conditions.append(f"[System.AreaPath] UNDER '{escape_wiql_literal(area_path)}'")
    if tag:
        conditions.append(f"[System.Tags] CONTAINS '{escape_wiql_literal(tag)}'")
    if len(conditions) == 1:
        raise ValueError("No scope given: provide --ids, --iteration-path, --area-path, --tag, or --wiql")
    where = " AND ".join(conditions)
    return f"SELECT [System.Id] FROM WorkItems WHERE {where} ORDER BY [System.ChangedDate] DESC"


def http_request(url: str, pat: str, method: str = "GET", body: dict | None = None) -> dict:
    """Issue an authenticated JSON request against the TFS/ADO REST API."""
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(url, data=data, method=method)
    token = base64.b64encode(f":{pat}".encode("utf-8")).decode("ascii")
    request.add_header("Authorization", f"Basic {token}")
    request.add_header("Content-Type", "application/json")
    request.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} from {url}\n{detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Could not reach {url}: {exc.reason}") from exc


def read_pat(pat_env: str | None) -> str:
    if pat_env:
        pat = os.environ.get(pat_env)
        if not pat:
            raise RuntimeError(f"Environment variable {pat_env} is not set or empty")
        return pat.strip()
    pat = sys.stdin.readline().strip()
    if not pat:
        raise RuntimeError("No PAT provided on stdin. Pipe it in, e.g.: echo \"$PAT\" | fetch_work_items.py ...")
    return pat


def fetch_work_items_by_ids(api_base: str, pat: str, ids: list[int], fields: list[str], api_version: str) -> list[dict]:
    items = []
    for start in range(0, len(ids), BATCH_SIZE):
        chunk = ids[start:start + BATCH_SIZE]
        id_param = ",".join(str(i) for i in chunk)
        field_param = ",".join(fields)
        url = f"{api_base}/wit/workitems?ids={id_param}&fields={field_param}&api-version={api_version}"
        result = http_request(url, pat)
        items.extend(result.get("value", []))
    return items


def normalize_work_item(raw: dict) -> dict:
    fields = raw.get("fields", {})
    return {
        "id": raw.get("id"),
        "type": fields.get("System.WorkItemType"),
        "title": fields.get("System.Title"),
        "state": fields.get("System.State"),
        "description": fields.get("System.Description"),
        "repro_steps": fields.get("Microsoft.VSTS.TCM.ReproSteps"),
        "resolved_reason": fields.get("Microsoft.VSTS.Common.ResolvedReason"),
        "area_path": fields.get("System.AreaPath"),
        "iteration_path": fields.get("System.IterationPath"),
        "tags": fields.get("System.Tags"),
        "priority": fields.get("Microsoft.VSTS.Common.Priority"),
        "url": raw.get("url"),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--server", default=DEFAULT_SERVER, help=f"TFS/ADO server base URL (default: {DEFAULT_SERVER})")
    parser.add_argument("--project", default=DEFAULT_PROJECT, help=f"Team project name (default: {DEFAULT_PROJECT})")
    parser.add_argument("--collection", default=None, help="Collection name, if the server URL doesn't already include one")
    parser.add_argument("--api-base", default=None, help="Full override for the `_apis` base URL, bypassing --server/--collection/--project")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION, help=f"REST API version (default: {DEFAULT_API_VERSION})")
    parser.add_argument("--ids", default=None, help="Comma-separated list of work item IDs to fetch directly")
    parser.add_argument("--iteration-path", default=None, help="Scope to an iteration path (WIQL UNDER match)")
    parser.add_argument("--area-path", default=None, help="Scope to an area path (WIQL UNDER match)")
    parser.add_argument("--tag", default=None, help="Scope to work items containing this tag")
    parser.add_argument("--wiql", default=None, help="Raw WIQL query, overrides all other scope options")
    parser.add_argument("--fields", default=None, help="Comma-separated field list to fetch (default: a standard set)")
    parser.add_argument("--pat-env", default=None, help="Read the PAT from this environment variable instead of stdin")
    parser.add_argument("--test-connection", action="store_true", help="Only verify the connection (fetches work item types for the project) and exit")
    args = parser.parse_args()

    try:
        pat = read_pat(args.pat_env)
        api_base = build_api_base(args.server, args.project, args.collection, args.api_base)
        fields = args.fields.split(",") if args.fields else DEFAULT_FIELDS

        if args.test_connection:
            url = f"{api_base}/wit/workitemtypes?api-version={args.api_version}"
            result = http_request(url, pat)
            types = [t.get("name") for t in result.get("value", [])]
            print(json.dumps({
                "status": "ok",
                "api_base": api_base,
                "project": args.project,
                "work_item_types": types,
            }, indent=2))
            return

        if args.ids:
            ids = [int(i.strip()) for i in args.ids.split(",") if i.strip()]
            raw_items = fetch_work_items_by_ids(api_base, pat, ids, fields, args.api_version)
        else:
            wiql = build_wiql(args.project, iteration_path=args.iteration_path, area_path=args.area_path, tag=args.tag, raw_wiql=args.wiql)
            query_url = f"{api_base}/wit/wiql?api-version={args.api_version}"
            query_result = http_request(query_url, pat, method="POST", body={"query": wiql})
            ids = [w["id"] for w in query_result.get("workItems", [])]
            if not ids:
                print(json.dumps({"status": "ok", "api_base": api_base, "wiql": wiql, "work_items": []}, indent=2))
                return
            raw_items = fetch_work_items_by_ids(api_base, pat, ids, fields, args.api_version)

        work_items = [normalize_work_item(item) for item in raw_items]
        print(json.dumps({"status": "ok", "api_base": api_base, "count": len(work_items), "work_items": work_items}, indent=2))

    except Exception as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, indent=2))
        print(str(exc), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
