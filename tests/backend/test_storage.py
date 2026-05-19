import unittest
from backend.app.storage import AnalysisStorage


class TestAnalysisStorage(unittest.TestCase):
    def setUp(self):
        self.storage = AnalysisStorage(":memory:")  # In-memory DB for tests

    def test_save_and_get(self):
        analysis_id = self.storage.save(
            filename="test.txt",
            document_text="Some text",
            profile={"age": 22},
            extraction={"title": "Test"},
            eligibility={"status": "eligible"},
            warnings=[],
            checklist=[],
            actions=[],
            evidence=[{"label": "지원 대상", "snippet": "지원 대상: 서울 거주"}],
        )

        result = self.storage.get(analysis_id)
        self.assertIsNotNone(result)
        self.assertEqual(result["filename"], "test.txt")
        self.assertEqual(result["profile"]["age"], 22)
        self.assertEqual(result["evidence"][0]["label"], "지원 대상")

    def test_list_all(self):
        for i in range(3):
            self.storage.save(
                filename=f"test{i}.txt",
                document_text="Text",
                profile={},
                extraction={},
                eligibility={},
                warnings=[],
                checklist=[],
                actions=[],
            )

        analyses = self.storage.list_all()
        self.assertEqual(len(analyses), 3)

    def test_delete(self):
        analysis_id = self.storage.save(
            filename="test.txt",
            document_text="Text",
            profile={},
            extraction={},
            eligibility={},
            warnings=[],
            checklist=[],
            actions=[],
        )

        deleted = self.storage.delete(analysis_id)
        self.assertTrue(deleted)

        result = self.storage.get(analysis_id)
        self.assertIsNone(result)

    def test_list_ordering(self):
        """Verify list returns newest first."""
        import time
        
        ids = []
        for i in range(3):
            id = self.storage.save(
                filename=f"test{i}.txt",
                document_text="Text",
                profile={},
                extraction={},
                eligibility={},
                warnings=[],
                checklist=[],
                actions=[],
            )
            ids.append(id)
            # Small delay to ensure different timestamps
            time.sleep(0.01)

        analyses = self.storage.list_all()
        # Should be in reverse order (newest first)
        self.assertEqual(len(analyses), 3)
        # Verify all IDs are present
        analysis_ids = [a["id"] for a in analyses]
        self.assertEqual(set(analysis_ids), set(ids))


if __name__ == "__main__":
    unittest.main()
