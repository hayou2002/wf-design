import argparse
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import bili


class BiliToolTests(unittest.TestCase):
    def test_human_chinese_track_precedes_ai_track(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            args = argparse.Namespace(video="BV19DySz4EQF", part=1, language=None, refresh=True)
            info = {"pages": [{"page": 1, "cid": 42}]}
            player = {"subtitle": {"subtitles": [
                {"lan": "ai-zh", "lan_doc": "中文", "ai_type": 0, "subtitle_url": "//example.com/ai"},
                {"lan": "zh-Hans", "lan_doc": "中文（简体）", "ai_type": 0, "subtitle_url": "//example.com/human"},
            ]}}
            with patch.object(bili, "CACHE", Path(directory)), patch.object(bili, "command_info", return_value=info), \
                    patch.object(bili, "current_session", return_value={"cookies": {"SESSDATA": "test"}}), \
                    patch.object(bili, "require_ok", return_value=player), \
                    patch.object(bili, "request_json", return_value={"body": [{"from": 0, "to": 1, "content": "内容"}]}):
                result = bili.command_subtitles(args)
            self.assertEqual(result["subtitle"]["lan"], "zh-Hans")
            self.assertEqual(result["subtitle"]["kind"], "human_or_unmarked")
            self.assertNotIn("cookies", result)

    def test_empty_filtered_search_explains_scope(self) -> None:
        args = argparse.Namespace(query="不存在的内容", order="totalrank", uploader=None, uploader_mid=13030183, limit=5)
        with patch.object(bili, "request_json", return_value={"result": []}), \
                patch.object(bili, "require_ok", side_effect=lambda payload: payload):
            result = bili.command_search(args)
        self.assertEqual(result["count"], 0)
        self.assertIn("第一页", result["result_note"])

    def test_parse_bvid_from_url(self) -> None:
        self.assertEqual(bili.parse_bvid("https://www.bilibili.com/video/BV19DySz4EQF/?p=2"), "BV19DySz4EQF")


if __name__ == "__main__":
    unittest.main()
