"""Local, non-destructive review and stable-ID CSV interchange."""

from __future__ import annotations

import copy
import csv
import io
import json
from typing import Any

from .core import LedgerError, validate

FIELDS = (
    "id",
    "adaptation",
    "category",
    "significance",
    "source_version",
    "adaptation_version",
    "source_anchor",
    "adaptation_anchor",
    "evidence",
)


def merge_csv(ledger: dict[str, Any], text: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Preview full-record updates by ID; preserve untouched records and ordering."""
    reader = csv.DictReader(io.StringIO(text.lstrip("\ufeff")))
    headers = reader.fieldnames or []
    required = set(FIELDS[:6])
    if len(headers) != len(set(headers)) or not required.issubset(headers):
        raise LedgerError("CSV needs unique headers and all six required difference fields.")
    if set(headers) - set(FIELDS):
        raise LedgerError("CSV contains unsupported columns.")
    merged = copy.deepcopy(ledger)
    positions = {item["id"]: index for index, item in enumerate(merged["differences"])}
    seen: set[str] = set()
    changes: list[dict[str, Any]] = []
    for line, row in enumerate(reader, 2):
        if None in row or any(value is None for value in row.values()):
            raise LedgerError(f"CSV row {line} has a different number of cells than its header.")
        identifier = row["id"]
        if not identifier or identifier in seen:
            raise LedgerError(f"CSV row {line} has an empty or duplicate difference ID.")
        seen.add(identifier)
        before = None
        if identifier in positions:
            index = positions[identifier]
            before = merged["differences"][index]
            if before["adaptation"] != row["adaptation"]:
                raise LedgerError(
                    f"ID {identifier} belongs to another adaptation; choose a new ID."
                )
            after = {**before, **row}
            merged["differences"][index] = after
        else:
            after = dict(row)
            merged["differences"].append(after)
        changes.append(
            {
                "id": identifier,
                "action": "added"
                if before is None
                else "unchanged"
                if before == after
                else "updated",
                "before": before,
                "after": after,
            }
        )
    validate(merged)
    return merged, {
        "changes": changes,
        "removed": [],
        "note": "Preview only. Omitted IDs are preserved.",
    }


def csv_export(ledger: dict[str, Any]) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=FIELDS, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(ledger["differences"])
    return output.getvalue()


def html_review(report: dict[str, Any]) -> str:
    payload = json.dumps(report).replace("<", "\\u003c").replace("&", "\\u0026")
    return (
        """<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Adaptation review</title>
<style>body{font:17px system-ui;max-width:1120px;margin:auto;padding:22px;background:#f5f1e8;color:#203442}
header,article{background:white;border:1px solid #b4c4ca;padding:20px;border-radius:12px;margin:16px 0}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:24px}p{white-space:pre-wrap;overflow-wrap:anywhere}
input,select{font:inherit;max-width:100%;box-sizing:border-box;padding:9px}label{display:inline-block;margin:8px}
a{color:#165778} @media(max-width:600px){.pair{grid-template-columns:1fr}label{display:block}}</style>
<h1>Adaptation comparison</h1><p>Author-recorded differences. Chapter and scene anchors are local reference labels.</p>
<header><label>Search <input id="search" type="search"></label><label>Category <select id="category"><option value="">All categories</option></select></label>
<label>Significance <select id="significance"><option value="">All significance levels</option></select></label><p id="count" role="status"></p></header>
<main id="review"></main><script id="data" type="application/json">"""
        + payload
        + """</script><script>
const data=JSON.parse(document.getElementById('data').textContent),rows=[];
const titles=Object.fromEntries(data.adaptations.map(a=>[a.id,a.title]));
for(const key of ['category','significance'])for(const value of [...new Set(data.differences.map(d=>d[key]))].sort()){
const option=document.createElement('option');option.value=value;option.textContent=value;document.getElementById(key).append(option);}
for(const [index,item] of data.differences.entries()){
const article=document.createElement('article');article.id='difference-'+index;const h=document.createElement('h2');
const link=document.createElement('a');link.href='#'+article.id;link.textContent=item.id+' · '+titles[item.adaptation];h.append(link);article.append(h);
const badge=document.createElement('p');badge.textContent=item.category+' / '+item.significance;article.append(badge);
const pair=document.createElement('div');pair.className='pair';
for(const [key,label] of [['source','Source'],['adaptation','Adaptation']]){const section=document.createElement('section');
section.id=article.id+'-'+key;const heading=document.createElement('h3');const anchor=document.createElement('a');anchor.href='#'+section.id;
anchor.textContent=label+(item[key+'_anchor']?' — '+item[key+'_anchor']:'');heading.append(anchor);
const text=document.createElement('p');text.textContent=item[key+'_version'];section.append(heading,text);pair.append(section);}article.append(pair);
if(item.evidence){const p=document.createElement('p');p.textContent='Evidence: '+item.evidence;article.append(p);}
document.getElementById('review').append(article);rows.push([item,article]);}
function filter(){let count=0;for(const [item,article] of rows){const visible=(!category.value||item.category===category.value)&&(!significance.value||item.significance===significance.value)&&JSON.stringify(item).toLowerCase().includes(search.value.toLowerCase());article.hidden=!visible;if(visible)count++;}document.getElementById('count').textContent=count+' of '+rows.length+' differences shown';}
const search=document.getElementById('search'),category=document.getElementById('category'),significance=document.getElementById('significance');
for(const control of [search,category,significance])control.addEventListener('input',filter);filter();</script></html>"""
    )
