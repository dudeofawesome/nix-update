from __future__ import annotations

import io
import textwrap
import unittest.mock
from urllib.parse import urlparse

from nix_update.version import VersionFetchConfig, fetch_latest_version
from nix_update.version.sparkle import fetch_sparkle_versions
from nix_update.version.version import VersionPreference


def _response(xml: str) -> io.BytesIO:
    return io.BytesIO(textwrap.dedent(xml).encode())


def test_fetch_sparkle_versions_prefers_short_version_string() -> None:
    appcast = """
        <rss version="2.0" xmlns:sparkle="http://www.andymatuschak.org/xml-namespaces/sparkle">
          <channel>
            <item>
              <sparkle:version>1248</sparkle:version>
              <sparkle:shortVersionString>1.5.1</sparkle:shortVersionString>
              <enclosure url="https://example.com/App.zip" />
            </item>
          </channel>
        </rss>
    """

    with unittest.mock.patch(
        "nix_update.version.sparkle.urlopen",
        return_value=_response(appcast),
    ):
        versions = fetch_sparkle_versions(
            urlparse("https://example.com/appcast.xml"),
        )

    assert [version.number for version in versions] == ["1.5.1"]


def test_fetch_sparkle_versions_supports_enclosure_attributes() -> None:
    appcast = """
        <rss version="2.0" xmlns:sparkle="http://www.andymatuschak.org/xml-namespaces/sparkle">
          <channel>
            <item>
              <enclosure
                url="https://example.com/App-2.0.zip"
                sparkle:version="2.0"
                length="42" />
            </item>
          </channel>
        </rss>
    """

    with unittest.mock.patch(
        "nix_update.version.sparkle.urlopen",
        return_value=_response(appcast),
    ):
        versions = fetch_sparkle_versions(
            urlparse("https://example.com/appcast.xml"),
        )

    assert [version.number for version in versions] == ["2.0"]


def test_fetch_latest_version_sorts_sparkle_versions() -> None:
    appcast = """
        <rss version="2.0" xmlns:sparkle="http://www.andymatuschak.org/xml-namespaces/sparkle">
          <channel>
            <item>
              <sparkle:version>1.9.9</sparkle:version>
            </item>
            <item>
              <sparkle:version>2.0.0</sparkle:version>
            </item>
          </channel>
        </rss>
    """

    with unittest.mock.patch(
        "nix_update.version.sparkle.urlopen",
        return_value=_response(appcast),
    ):
        version = fetch_latest_version(
            urlparse("https://example.com/appcast.xml"),
            VersionFetchConfig(
                preference=VersionPreference.STABLE,
                version_regex="(.*)",
            ),
        )

    assert version.number == "2.0.0"


def test_fetch_sparkle_versions_ignores_non_xml_urls() -> None:
    versions = fetch_sparkle_versions(
        urlparse("https://example.com/App-1.0.zip"),
    )

    assert versions == []
