import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from osduo_business_connect.utils.website import safe_video_url, video_embed

APP_DIR = os.path.join(os.path.dirname(__file__), "..")
YT = "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ"


class TestVideoEmbedProviders(unittest.TestCase):
    """Reported bug 1: a YouTube watch/share link put straight in an iframe is
    refused by the provider. It must be rewritten to a frameable embed URL."""

    def test_youtube_watch_becomes_nocookie_embed(self):
        self.assertEqual(
            video_embed("https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
            {"kind": "iframe", "src": YT},
        )

    def test_youtu_be_short_link(self):
        self.assertEqual(video_embed("https://youtu.be/dQw4w9WgXcQ"), {"kind": "iframe", "src": YT})

    def test_youtube_mobile_and_music_hosts(self):
        for host in ("m.youtube.com", "music.youtube.com"):
            with self.subTest(host=host):
                self.assertEqual(
                    video_embed(f"https://{host}/watch?v=dQw4w9WgXcQ"),
                    {"kind": "iframe", "src": YT},
                )

    def test_youtube_shorts_and_live(self):
        for kind in ("shorts", "live"):
            with self.subTest(kind=kind):
                self.assertEqual(
                    video_embed(f"https://www.youtube.com/{kind}/dQw4w9WgXcQ"),
                    {"kind": "iframe", "src": YT},
                )

    def test_youtube_embed_url_passthrough(self):
        self.assertEqual(video_embed(YT), {"kind": "iframe", "src": YT})

    def test_vimeo_share_becomes_player(self):
        self.assertEqual(
            video_embed("https://vimeo.com/76979871"),
            {"kind": "iframe", "src": "https://player.vimeo.com/video/76979871"},
        )

    def test_vimeo_player_passthrough(self):
        self.assertEqual(
            video_embed("https://player.vimeo.com/video/76979871"),
            {"kind": "iframe", "src": "https://player.vimeo.com/video/76979871"},
        )

    def test_google_drive_view_becomes_preview(self):
        self.assertEqual(
            video_embed("https://drive.google.com/file/d/1AbC_2def/view?usp=sharing"),
            {"kind": "iframe", "src": "https://drive.google.com/file/d/1AbC_2def/preview"},
        )

    def test_dailymotion_share_becomes_embed(self):
        self.assertEqual(
            video_embed("https://www.dailymotion.com/video/x8abcdef"),
            {"kind": "iframe", "src": "https://www.dailymotion.com/embed/video/x8abcdef"},
        )


class TestVideoEmbedNextcloud(unittest.TestCase):
    """Reported bug 2: a Nextcloud public share rendered nothing because the
    host was not in the fixed allow-list. Self-hosted shares must play as a
    direct file via an HTML5 <video> (kind == "file")."""

    def test_nextcloud_share_page_becomes_direct_download(self):
        self.assertEqual(
            video_embed("https://nextcloud.mybiz.com/s/AbCdEf12GhIjKlM"),
            {"kind": "file", "src": "https://nextcloud.mybiz.com/s/AbCdEf12GhIjKlM/download?inline=true"},
        )

    def test_nextcloud_index_php_and_download_variants(self):
        # The index.php/ prefix is preserved (it is a valid Nextcloud rewrite),
        # and an already-/download share is not doubled.
        self.assertEqual(
            video_embed("https://c.example/index.php/s/AbCdEf12GhIjKlM")["src"],
            "https://c.example/index.php/s/AbCdEf12GhIjKlM/download?inline=true",
        )
        self.assertEqual(
            video_embed("https://c.example/s/AbCdEf12GhIjKlM/download")["src"],
            "https://c.example/s/AbCdEf12GhIjKlM/download?inline=true",
        )

    def test_nextcloud_share_is_file_kind(self):
        self.assertEqual(video_embed("https://cloud.host/s/AbCdEf12GhIjKlM")["kind"], "file")


class TestVideoEmbedDirectFiles(unittest.TestCase):
    def test_direct_file_on_arbitrary_https_host(self):
        self.assertEqual(
            video_embed("https://cdn.example.org/promo.mp4"),
            {"kind": "file", "src": "https://cdn.example.org/promo.mp4"},
        )

    def test_other_video_extensions(self):
        for ext in (".webm", ".ogg", ".ogv", ".m4v", ".mov"):
            with self.subTest(ext=ext):
                self.assertEqual(
                    video_embed(f"https://host.example/v{ext}")["kind"], "file"
                )


class TestVideoEmbedRejectsUnsafe(unittest.TestCase):
    def test_dangerous_protocols(self):
        for bad in ("javascript:alert(1)", "data:text/html,<script>", "vbscript:x", "file:///etc/passwd"):
            with self.subTest(bad=bad):
                self.assertIsNone(video_embed(bad))

    def test_non_https_scheme(self):
        self.assertIsNone(video_embed("ftp://host.example/video.mp4"))

    def test_lookalike_domain_is_not_a_provider(self):
        # youtube.com.evil.com must not be treated as YouTube; it is also not a
        # video file / Nextcloud share, so it is dropped entirely.
        self.assertIsNone(video_embed("https://youtube.com.evil.com/watch?v=dQw4w9WgXcQ"))

    def test_unknown_page_url_returns_none(self):
        self.assertIsNone(video_embed("https://some-blog.example.com/article"))

    def test_empty_and_none(self):
        self.assertIsNone(video_embed(""))
        self.assertIsNone(video_embed(None))


class TestSafeVideoUrlCompat(unittest.TestCase):
    def test_returns_iframe_src_for_providers(self):
        self.assertEqual(safe_video_url("https://youtu.be/dQw4w9WgXcQ"), YT)

    def test_returns_empty_for_non_iframe_sources(self):
        # Nextcloud / direct files are handled by video_embed, not this filter.
        self.assertEqual(safe_video_url("https://nextcloud.mybiz.com/s/AbCdEf12"), "")
        self.assertEqual(safe_video_url("https://host.example/v.mp4"), "")

    def test_returns_empty_for_dangerous(self):
        self.assertEqual(safe_video_url("javascript:alert(1)"), "")


class TestVideoTemplates(unittest.TestCase):
    """Templates must use video_embed and render iframe vs video, and must not
    emit an empty iframe when the URL is unusable."""

    PAGES = ("product/product", "service/service")

    def _read(self, sub):
        with open(os.path.join(APP_DIR, "templates", "pages", sub) + ".html") as f:
            return f.read()

    def test_uses_video_embed_filter(self):
        for sub in self.PAGES:
            body = self._read(sub)
            self.assertIn("doc.video_url | video_embed", body, sub)
            self.assertIn('video_player.kind == "iframe"', body, sub)
            self.assertIn("<video ", body, sub)

    def test_guards_on_resolved_player_not_raw_url(self):
        for sub in self.PAGES:
            body = self._read(sub)
            self.assertIn("{% if video_player %}", body, sub)
            self.assertNotIn("{% if doc.video_url %}", body, sub)

    def test_no_raw_unsanitized_src(self):
        for sub in self.PAGES:
            body = self._read(sub)
            self.assertNotIn('src="{{ doc.video_url }}"', body, sub)


if __name__ == "__main__":
    unittest.main()
