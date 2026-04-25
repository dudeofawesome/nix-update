from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING

from .http import DEFAULT_TIMEOUT, urlopen
from .version import Version

if TYPE_CHECKING:
    from urllib.parse import ParseResult


def _local_name(name: str) -> str:
    return name.rsplit("}", 1)[-1]


def _child_text(element: ET.Element, name: str) -> str | None:
    for child in element:
        if _local_name(child.tag) == name and child.text:
            return child.text.strip()
    return None


def _attr(element: ET.Element, name: str) -> str | None:
    for attr_name, value in element.attrib.items():
        if _local_name(attr_name) == name:
            return value
    return None


def _version_from_item(item: ET.Element) -> Version | None:
    version = _child_text(item, "shortVersionString") or _child_text(item, "version")
    if version is not None:
        return Version(version)

    for enclosure in item.findall("{*}enclosure"):
        version = _attr(enclosure, "shortVersionString") or _attr(enclosure, "version")
        if version is not None:
            return Version(version)

    return None


def fetch_sparkle_versions(url: ParseResult) -> list[Version]:
    if url.scheme not in ("http", "https") or not url.path.endswith(".xml"):
        return []

    with urlopen(url.geturl(), timeout=DEFAULT_TIMEOUT) as resp:
        try:
            tree = ET.fromstring(resp.read())
        except ET.ParseError:
            return []

    versions = []
    for item in tree.findall(".//{*}item"):
        version = _version_from_item(item)
        if version is not None:
            versions.append(version)
    return versions
