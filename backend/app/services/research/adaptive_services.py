"""Deterministic, auditable adaptation and observable-skill calculations."""

import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.database.models.research import AdaptationDecision, TraineeSkillProfile


class AdaptiveDifficultyService:
    LEVELS = ("BEGINNER", "INTERMEDIATE", "ADVANCED")

    @classmethod
    def resolve(cls, db: Session, user, requested: str):
        requested_upper = requested.upper()
        if requested_upper != "ADAPTIVE":
            return requested_upper, {"mode": "manual", "selected_difficulty": requested_upper, "reason": "Manual difficulty selection."}
        profile = db.query(TraineeSkillProfile).filter(TraineeSkillProfile.user_id == user.id, TraineeSkillProfile.tenant_id == user.tenant_id).first()
        dimensions = json.loads(profile.skill_dimensions_json) if profile else {}
        completed = profile.sessions_completed if profile else 0
        average = sum(dimensions.values()) / len(dimensions) if dimensions else 0
        if completed < 2:
            selected, reason = "BEGINNER", "Fewer than two completed sessions; establish a baseline."
        elif average >= 0.75:
            selected, reason = "ADVANCED", "High observable-skill average; increase stages and ambiguity."
        elif average >= 0.45:
            selected, reason = "INTERMEDIATE", "Developing observable skills; use a multi-stage scenario."
        else:
            selected, reason = "BEGINNER", "Low observable-skill average; reduce complexity for reinforcement."
        return selected, {"mode": "adaptive", "selected_difficulty": selected, "reason": reason, "sessions_completed": completed, "skill_average": round(average, 2)}

    @staticmethod
    def record(db: Session, session, user, decision):
        session.difficulty_adaptation_json = json.dumps(decision)
        db.add(AdaptationDecision(session_id=session.id, user_id=user.id, tenant_id=user.tenant_id,
                                  decision_type="difficulty", current_attack_step=None,
                                  trainee_state_json=json.dumps({"skill_average": decision.get("skill_average")}),
                                  candidate_actions_json=json.dumps(list(AdaptiveDifficultyService.LEVELS)),
                                  selected_action=decision["selected_difficulty"], reason=decision["reason"]))


class AdaptiveAttackerService:
    @staticmethod
    def consider(db: Session, session, user, tracker, engine_type: str, lab_manager=None):
        prior = db.query(AdaptationDecision).filter(AdaptationDecision.session_id == session.id, AdaptationDecision.decision_type == "attack_path").count()
        if prior:
            return None
        commands = tracker.commands
        if not commands:
            return None
        text = " ".join(item["command"].lower() for item in commands)
        detected = any(token in text for token in ("auth.log", "access.log", "grep", "netstat", "find"))
        candidates = ["continue_planned_path", "alternate_safe_internal_check"]
        selected = "alternate_safe_internal_check" if detected and engine_type == "docker" else "continue_planned_path"
        reason = "Trainee inspected relevant evidence early; use the predefined alternate safe observation." if selected != "continue_planned_path" else "No early detection signal requiring an alternate bounded action."
        state = {"command_count": len(commands), "detected": detected, "accessed_files": tracker.accessed_files, "discovered_files": tracker.discovered_files}
        outcome = None
        if selected == "alternate_safe_internal_check":
            try:
                outcome = lab_manager.execute_validated_action(session.id, "internal_auth_check", session.docker_lab_key)
            except Exception as exc:
                outcome = f"failed: {exc}"
                selected = "continue_planned_path"
                reason = "Alternate action was unavailable; no unsafe fallback was attempted."
        decision = AdaptationDecision(session_id=session.id, user_id=user.id, tenant_id=user.tenant_id,
                                      decision_type="attack_path", current_attack_step=str(prior + 1),
                                      trainee_state_json=json.dumps(state), candidate_actions_json=json.dumps(candidates),
                                      selected_action=selected, reason=reason)
        db.add(decision)
        db.commit()
        return {"selected_action": selected, "reason": reason, "outcome": outcome}


class TraineeSkillService:
    DIMENSIONS = ("log_analysis", "network_investigation", "terminal_investigation", "attack_identification", "root_cause_analysis", "incident_response")

    @classmethod
    def update(cls, db: Session, session, user, evaluation, tracker):
        existing_profile = db.query(TraineeSkillProfile).filter(
            TraineeSkillProfile.user_id == user.id,
            TraineeSkillProfile.tenant_id == user.tenant_id,
        ).first()
        # Evaluation can be requested again from a completed history record. Do
        # not inflate an observable profile for the same session.
        if session.behavior_json:
            return {
                "behavior": json.loads(session.behavior_json),
                "session_dimensions": {},
                "profile_dimensions": json.loads(existing_profile.skill_dimensions_json) if existing_profile else {},
                "sessions_completed": existing_profile.sessions_completed if existing_profile else 0,
            }
        commands = tracker.commands if tracker else []
        first_seconds = round((commands[0]["timestamp"] and (datetime.fromisoformat(commands[0]["timestamp"]) - session.created_at).total_seconds()), 2) if commands else None
        successful = sum(1 for command in commands if command["exit_code"] == 0)
        useful = len(evaluation.matched_commands)
        behavior = {"time_to_first_investigation_seconds": first_seconds, "time_to_detect_attack_seconds": first_seconds if evaluation.matched_findings else None,
                    "commands_used": len(commands), "useful_commands": useful, "unsuccessful_commands": len(commands) - successful,
                    "artifacts_inspected": len(tracker.artifacts_inspected) if tracker else 0,
                    "relevant_evidence_discovered": len(evaluation.matched_findings), "incorrect_hypotheses": len(evaluation.missed_findings),
                    "findings_submitted": len(evaluation.matched_findings) + len(evaluation.missed_findings), "final_score": evaluation.score}
        dimensions = {
            "log_analysis": round(min(1, (behavior["relevant_evidence_discovered"] + behavior["artifacts_inspected"]) / 6), 2),
            "network_investigation": round(min(1, sum(1 for c in commands if any(x in c["command"].lower() for x in ("netstat", "ip", "ifconfig", "grep"))) / 3), 2),
            "terminal_investigation": round(successful / len(commands), 2) if commands else 0.0,
            "attack_identification": round(evaluation.findings_score / 35, 2),
            "root_cause_analysis": round(evaluation.root_cause_score / 15, 2),
            "incident_response": round(evaluation.mitigation_score / 10, 2),
        }
        session.behavior_json = json.dumps(behavior)
        profile = existing_profile
        if profile is None:
            profile = TraineeSkillProfile(user_id=user.id, tenant_id=user.tenant_id)
            db.add(profile)
            previous = {}
        else:
            previous = json.loads(profile.skill_dimensions_json)
        completed_before = profile.sessions_completed or 0
        profile.skill_dimensions_json = json.dumps({key: round(((previous.get(key, 0) * completed_before) + value) / (completed_before + 1), 2) for key, value in dimensions.items()})
        profile.metrics_json = json.dumps(behavior)
        profile.sessions_completed = completed_before + 1
        db.commit()
        return {"behavior": behavior, "session_dimensions": dimensions, "profile_dimensions": json.loads(profile.skill_dimensions_json), "sessions_completed": profile.sessions_completed}
