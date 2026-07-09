from pathlib import Path

import pandas as pd

from training.export_dataset import BITEXT_LABEL_MAP, merge_datasets


class TestExportDataset:
    def test_bitext_label_map_covers_project_categories(self):
        project_labels = {"hours", "location", "booking", "policy", "services", "payment"}
        mapped = set(BITEXT_LABEL_MAP.values())
        assert mapped.issubset(project_labels)

    def test_merge_datasets_combines_and_deduplicates(self, tmp_path: Path):
        custom = tmp_path / "custom.csv"
        extra = tmp_path / "extra.csv"
        out = tmp_path / "combined.csv"

        pd.DataFrame(
            [
                {"text": "what time do you open", "label": "hours"},
                {"text": "where are you located", "label": "location"},
            ]
        ).to_csv(custom, index=False)

        pd.DataFrame(
            [
                {"text": "what time do you open", "label": "hours"},  # duplicate
                {"text": "do you accept credit cards", "label": "payment"},
            ]
        ).to_csv(extra, index=False)

        result = merge_datasets(custom_path=custom, extra_path=extra, out_path=out)

        assert len(result) == 3
        assert out.exists()
        assert set(result["label"]) == {"hours", "location", "payment"}
