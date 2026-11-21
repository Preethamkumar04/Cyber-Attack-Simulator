from typing import Dict, Any

from app.schemas.evaluation_schema import (
    AnalystResponse,
    EvaluationResult,
)

from app.services.evaluation.scoring_engine import (
    ScoringEngine,
)

from app.services.ai_generator.feedback_generator import (
    FeedbackGenerator,
)


class EvaluationBuilder:
    """
    Orchestrates the complete evaluation pipeline.

    Responsible for:
    1. Scoring the analyst response
    2. Generating AI feedback
    3. Returning the final EvaluationResult
    """

    @classmethod
    def evaluate(
        cls,
        expected: Dict[str, Any],
        response: AnalystResponse,
    ) -> EvaluationResult:

        # ---------------------------------------------
        # Calculate numerical evaluation
        # ---------------------------------------------

        result = ScoringEngine.evaluate(
            expected,
            response,
        )

        # ---------------------------------------------
        # Generate AI coaching feedback
        # ---------------------------------------------

        feedback = FeedbackGenerator.generate(
            result,
            expected,
            response,
        )

        result.feedback = feedback

        return result