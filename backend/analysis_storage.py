import json
import uuid

from pathlib import Path
from typing import Optional


class AnalysisStorage:

    def __init__(
        self,
        directory: str = "data/analyses"
    ):
        self.directory = Path(directory)

        self.directory.mkdir(
            parents=True,
            exist_ok=True
        )

    def save(self, response: dict) -> str:
        """
        Save one complete analysis response
        into a separate JSON file.

        Returns the generated analysis_id.
        """

        analysis_id = str(uuid.uuid4())

        file_path = (
            self.directory /
            f"{analysis_id}.json"
        )

        # Add ID to stored response
        response_to_save = {
            "analysis_id": analysis_id,
            **response
        }

        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                response_to_save,
                file,
                ensure_ascii=False,
                indent=2
            )

        return analysis_id

    def get(
        self,
        analysis_id: str
    ) -> Optional[dict]:
        """
        Load one analysis by ID.
        """

        file_path = (
            self.directory /
            f"{analysis_id}.json"
        )

        if not file_path.exists():
            return None

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    def get_comments_by_issue(
        self,
        analysis_id: str,
        issue_category: str
    ) -> list[dict]:
        """
        Load one analysis file and return
        comments matching the issue category.
        """

        analysis = self.get(analysis_id)

        if analysis is None:
            return []

        comments = analysis.get(
            "comments",
            []
        )

        return [
            comment
            for comment in comments
            if issue_category
            in comment.get(
                "issue_categories",
                []
            )
        ]
