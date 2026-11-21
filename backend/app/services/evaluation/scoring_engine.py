from app.services.evaluation.semantic_matcher import SemanticMatcher

from app.schemas.evaluation_schema import (
    AnalystResponse,
    EvaluationResult
)


class ScoringEngine:

    FINDINGS_WEIGHT = 35
    COMMANDS_WEIGHT = 25
    SEVERITY_WEIGHT = 15
    ROOT_CAUSE_WEIGHT = 15
    MITIGATION_WEIGHT = 10

    @staticmethod
    def _score_list(expected, actual, weight, semantic=False):

        if not expected:
            return weight, [], []

        matched_items = []
        missed_items = []

        if semantic:

            score = SemanticMatcher.score_list(
                expected,
                actual
            )

            for item in expected:

                matched = False

                for response_item in actual:

                    if SemanticMatcher.score_text(
                        item,
                        response_item
                    ):

                        matched = True
                        break

                if matched:
                    matched_items.append(item)
                else:
                    missed_items.append(item)

            return (
                round(score * weight, 2),
                matched_items,
                missed_items
            )

        expected_set = {
            item.strip().lower()
            for item in expected
        }

        actual_set = {
            item.strip().lower()
            for item in actual
        }

        matches = expected_set.intersection(actual_set)

        for item in expected:

            if item.strip().lower() in matches:
                matched_items.append(item)
            else:
                missed_items.append(item)

        score = round(
            (len(matches) / len(expected_set)) * weight,
            2
        )

        return (
            score,
            matched_items,
            missed_items
        )

    @staticmethod
    def _score_text(expected, actual, weight, semantic=False):
        """
        Scores simple text fields.
        """

        if semantic:

            if SemanticMatcher.score_text(expected, actual):
                return weight

            return 0

        if expected.strip().lower() == actual.strip().lower():
            return weight

        return 0

    @classmethod
    def evaluate(
        cls,
        expected,
        response: AnalystResponse
    ):

        findings_score = cls._score_list
        (
            findings_score,
            matched_findings,
            missed_findings
        ) = cls._score_list(
            expected["findings"],
            response.findings,
            cls.FINDINGS_WEIGHT,
            semantic=True
        )

        commands_score = cls._score_list
        (
            commands_score,
            matched_commands,
            missed_commands
        ) = cls._score_list(
            expected["commands"],
            response.commands,
            cls.COMMANDS_WEIGHT
        )

        severity_score = cls._score_text(
            expected["severity"],
            response.severity,
            cls.SEVERITY_WEIGHT
        )

        root_cause_score = cls._score_text(
            expected["root_cause"],
            response.root_cause,
            cls.ROOT_CAUSE_WEIGHT,
            semantic=True
        )

        mitigation_score = cls._score_list
        (
            mitigation_score,
            matched_mitigation,
            missed_mitigation
        ) = cls._score_list(
            expected["mitigation"],
            response.mitigation,
            cls.MITIGATION_WEIGHT,
            semantic=True
        )

        total_score = (
            findings_score
            + commands_score
            + severity_score
            + root_cause_score
            + mitigation_score
        )

        return EvaluationResult(

            session_id=response.session_id,

            score=round(total_score, 2),

            findings_score=findings_score,
            commands_score=commands_score,
            severity_score=severity_score,
            root_cause_score=root_cause_score,
            mitigation_score=mitigation_score,

            matched_findings=matched_findings,
            missed_findings=missed_findings,

            matched_commands=matched_commands,
            missed_commands=missed_commands,

            matched_mitigation=matched_mitigation,
            missed_mitigation=missed_mitigation,

            feedback=""
        )