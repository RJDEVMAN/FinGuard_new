from initialisation_client import client1
from dotenv import load_dotenv
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum
import base64

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fingard_audit.log'),
        logging.StreamHandler()
    ]
)

load_dotenv()


class ExecutionMode(Enum):
    ASK = "ASK"
    COMMAND = "COMMAND"


class AgentDecision(Enum):
    SAFE = "SAFE"
    FRAUD = "FRAUD"
    CHECK_REQUIRED = "CHECK-REQUIRED"
    BLOCKED = "BLOCKED"


class MediaType(Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"


class ExecutionContext:
    def __init__(self, 
                 user_input: str,
                 media_type: MediaType,
                 mode: ExecutionMode,
                 input_metadata: Optional[Dict] = None):
        self.user_input = user_input
        self.media_type = media_type
        self.mode = mode
        self.input_metadata = input_metadata or {}
        self.execution_timestamp = datetime.now().isoformat()
        self.audit_trail = []
        self.agent_reports = {}
        self.blocked_actions = []
        self.errors = []
        self.session_id = self._generate_session_id()
        
    def _generate_session_id(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"SESSION_{timestamp}"
    
    def log_action(self, agent_name: str, action: str, status: str, details: Dict):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "action": action,
            "status": status,
            "details": details
        }
        self.audit_trail.append(log_entry)
        logging.info(f"[{agent_name}] {action} - {status}: {details}")
    
    def log_blocked_action(self, agent_name: str, action: str, reason: str):
        blocked_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "action": action,
            "reason": reason
        }
        self.blocked_actions.append(blocked_entry)
        logging.warning(f"[BLOCKED] {agent_name} attempted {action}: {reason}")
    
    def log_error(self, agent_name: str, error_msg: str, error_type: str):
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "error_type": error_type,
            "error_message": error_msg
        }
        self.errors.append(error_entry)
        logging.error(f"[{agent_name}] {error_type}: {error_msg}")
    
    def add_agent_report(self, agent_name: str, report: Dict):
        self.agent_reports[agent_name] = report


class BaseAgent:
    def __init__(self, agent_id: str, agent_name: str, policy: Dict):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.policy = policy
        self.logger = logging.getLogger(agent_name)
        
    def _capture_plan(self, 
                     prompt: str, 
                     steps: List[Dict],
                     metadata: Optional[Dict] = None) -> Dict:
        plan = {
            "goal": prompt,
            "steps": steps,
            "metadata": metadata or {"agent": self.agent_name}
        }
        
        try:
            captured_plan = client1.capture_plan(
                llm="gpt-4",
                prompt=prompt,
                plan=plan
            )
            self.logger.info(f"Plan captured successfully")
            return captured_plan
        except Exception as e:
            self.logger.error(f"Plan capture failed: {str(e)}")
            raise
    
    def _get_intent_token(self, captured_plan: Dict) -> Dict:
        try:
            token_response = client1.get_intent_token(
                plan_capture=captured_plan,
                policy=self.policy,
                validity_seconds=3600
            )
            self.logger.info(f"Intent token generated with policy enforcement")
            return token_response
        except Exception as e:
            self.logger.error(f"Token generation failed: {str(e)}")
            raise
    
    def _invoke_action(self, 
                      intent_token: Dict,
                      mcp: str,
                      action: str,
                      params: Dict) -> Dict:
        try:
            result = client1.invoke(
                mcp=mcp,
                action=action,
                intent_token=intent_token,
                params=params
            )
            
            if result.get("success"):
                self.logger.info(f"Action '{action}' executed successfully")
            else:
                self.logger.warning(f"Action '{action}' failed: {result.get('error')}")
            
            return result
        except Exception as e:
            self.logger.error(f"Action invocation failed: {str(e)}")
            raise
    
    def _delegate_to_next_agent(self,
                               intent_token: Dict,
                               next_agent_public_key: str,
                               next_agent_actions: List[str],
                               context: ExecutionContext) -> Dict:
        try:
            delegation_result = client1.delegate(
                intent_token=intent_token,
                delegate_public_key=next_agent_public_key,
                validity_seconds=1800,
                allowed_actions=next_agent_actions
            )
            
            context.log_action(
                self.agent_name,
                "DELEGATION_CREATED",
                "SUCCESS",
                {
                    "delegation_id": delegation_result.get("delegation_id"),
                    "next_agent_actions": next_agent_actions
                }
            )
            
            self.logger.info(f"Delegation created for next agent: {delegation_result.get('delegation_id')}")
            return delegation_result
        except Exception as e:
            context.log_error(self.agent_name, str(e), "DELEGATION_FAILED")
            self.logger.error(f"Delegation failed: {str(e)}")
            raise
    
    def ask_user_confirmation(self, question: str) -> bool:
        response = input(f"\n{self.agent_name}: {question} (yes/no): ").strip().lower()
        return response in ['yes', 'y']


class FraudAgent(BaseAgent):
    def __init__(self):
        policy = {
            "allow": ["fraud_agent/*", "fraud-mcp/*"],
            "deny": ["risk_agent/*", "compliance_agent/*", "memoryupdate_agent/*"]
        }
        super().__init__("fraud_agent", "FraudAgent", policy)
    
    def analyze(self, context: ExecutionContext) -> Dict:
        self.logger.info(f"Starting fraud analysis for {context.media_type.value}")
        
        try:
            analysis_steps = [
                {
                    "action": "detect_deepfakes",
                    "mcp": "fraud-mcp",
                    "params": {
                        "input": context.user_input,
                        "media_type": context.media_type.value
                    },
                    "description": "Detect deepfakes and AI-generated content"
                },
                {
                    "action": "analyze_anomalies",
                    "mcp": "fraud-mcp",
                    "params": {
                        "input": context.user_input,
                        "focus": "minor_details"
                    },
                    "description": "Analyze subtle details for manipulation"
                }
            ]
            
            prompt = f"""
Fraud Detection Analysis for FinGuard
Input Type: {context.media_type.value}
Mode: {context.mode.value}

Analyze for fraud indicators:
1. Deepfake detection - facial inconsistencies, audio sync issues
2. Synthetic media detection - AI-generated content artifacts
3. Manipulated data - altered timestamps, metadata tampering
4. Content authenticity - source verification, chain of custody

Classification: Return SAFE, FRAUD, or CHECK-REQUIRED with reasoning.
Focus on tiniest details and abnormalities.
"""
            
            captured_plan = self._capture_plan(prompt, analysis_steps)
            token = self._get_intent_token(captured_plan)
            
            detection_result = self._invoke_action(
                token,
                "fraud-mcp",
                "detect_deepfakes",
                {
                    "input": context.user_input,
                    "media_type": context.media_type.value
                }
            )
            
            context.log_action(
                "FraudAgent",
                "DEEPFAKE_DETECTION",
                "EXECUTED",
                {"result": detection_result}
            )
            
            anomaly_result = self._invoke_action(
                token,
                "fraud-mcp",
                "analyze_anomalies",
                {
                    "input": context.user_input,
                    "focus": "minor_details"
                }
            )
            
            context.log_action(
                "FraudAgent",
                "ANOMALY_ANALYSIS",
                "EXECUTED",
                {"result": anomaly_result}
            )
            
            fraud_decision = self._determine_fraud_classification(
                detection_result,
                anomaly_result
            )
            
            if context.mode == ExecutionMode.ASK:
                if fraud_decision == AgentDecision.FRAUD:
                    confirmed = self.ask_user_confirmation(
                        f"I detected potential fraud. Should I escalate to Risk Agent?"
                    )
                    if not confirmed:
                        context.log_action("FraudAgent", "USER_OVERRIDE", "ESCALATION_BLOCKED", {})
            
            fraud_report = {
                "agent": "FraudAgent",
                "timestamp": datetime.now().isoformat(),
                "input_type": context.media_type.value,
                "mode": context.mode.value,
                "decision": fraud_decision.value,
                "detection_data": detection_result.get("data", {}),
                "anomaly_data": anomaly_result.get("data", {}),
                "escalate_to_risk": fraud_decision != AgentDecision.SAFE
            }
            
            context.add_agent_report("FraudAgent", fraud_report)
            self.logger.info(f"Fraud analysis complete: {fraud_decision.value}")
            
            return fraud_report
            
        except Exception as e:
            context.log_error("FraudAgent", str(e), "ANALYSIS_FAILED")
            return {
                "agent": "FraudAgent",
                "decision": AgentDecision.CHECK_REQUIRED.value,
                "error": str(e)
            }
    
    def _determine_fraud_classification(self, 
                                       detection_result: Dict,
                                       anomaly_result: Dict) -> AgentDecision:
        deepfake_confidence = detection_result.get("data", {}).get("confidence", 0)
        anomaly_count = len(anomaly_result.get("data", {}).get("anomalies", []))
        
        if deepfake_confidence > 0.8 or anomaly_count > 5:
            return AgentDecision.FRAUD
        elif deepfake_confidence > 0.5 or anomaly_count > 2:
            return AgentDecision.CHECK_REQUIRED
        else:
            return AgentDecision.SAFE


class RiskAgent(BaseAgent):
    def __init__(self):
        policy = {
            "allow": ["risk_agent/*", "risk-mcp/*"],
            "deny": ["fraud_agent/*", "compliance_agent/*", "memoryupdate_agent/*"]
        }
        super().__init__("risk_agent", "RiskAgent", policy)
    
    def assess_risk(self, 
                   context: ExecutionContext,
                   fraud_report: Dict) -> Dict:
        self.logger.info("Starting risk assessment")
        
        try:
            risk_steps = [
                {
                    "action": "calculate_risk_score",
                    "mcp": "risk-mcp",
                    "params": {
                        "fraud_indicators": fraud_report.get("detection_data", {}),
                        "severity_multiplier": 1.5 if fraud_report["decision"] == "FRAUD" else 1.0
                    },
                    "description": "Calculate comprehensive risk score"
                },
                {
                    "action": "assess_impact",
                    "mcp": "risk-mcp",
                    "params": {
                        "threat_type": fraud_report["decision"],
                        "media_type": context.media_type.value
                    },
                    "description": "Assess potential impact of threat"
                }
            ]
            
            prompt = f"""
Risk Assessment Analysis
========================
Fraud Finding: {fraud_report['decision']}
Input Type: {context.media_type.value}

Assess the risk level:
1. Threat severity (Low/Medium/High/Critical)
2. Potential financial impact
3. Reputational damage risk
4. Compliance violation likelihood

Provide risk score 0-100 and mitigation recommendations.
"""
            
            captured_plan = self._capture_plan(prompt, risk_steps)
            token = self._get_intent_token(captured_plan)
            
            risk_score_result = self._invoke_action(
                token,
                "risk-mcp",
                "calculate_risk_score",
                {
                    "fraud_indicators": fraud_report.get("detection_data", {}),
                    "severity_multiplier": 1.5 if fraud_report["decision"] == "FRAUD" else 1.0
                }
            )
            
            context.log_action(
                "RiskAgent",
                "RISK_SCORING",
                "EXECUTED",
                {"score": risk_score_result.get("data", {}).get("risk_score", 0)}
            )
            
            impact_result = self._invoke_action(
                token,
                "risk-mcp",
                "assess_impact",
                {
                    "threat_type": fraud_report["decision"],
                    "media_type": context.media_type.value
                }
            )
            
            context.log_action(
                "RiskAgent",
                "IMPACT_ASSESSMENT",
                "EXECUTED",
                {"severity": impact_result.get("data", {}).get("severity", "UNKNOWN")}
            )
            
            risk_score = risk_score_result.get("data", {}).get("risk_score", 0)
            
            if context.mode == ExecutionMode.ASK and risk_score > 70:
                confirmed = self.ask_user_confirmation(
                    f"Risk Score: {risk_score}/100. Should I escalate to Compliance Agent?"
                )
                if not confirmed:
                    context.log_action("RiskAgent", "USER_OVERRIDE", "ESCALATION_BLOCKED", {})
            
            risk_report = {
                "agent": "RiskAgent",
                "timestamp": datetime.now().isoformat(),
                "fraud_finding": fraud_report["decision"],
                "risk_score": risk_score,
                "severity": impact_result.get("data", {}).get("severity", "UNKNOWN"),
                "escalate_to_compliance": risk_score > 70,
                "recommendations": impact_result.get("data", {}).get("recommendations", [])
            }
            
            context.add_agent_report("RiskAgent", risk_report)
            self.logger.info(f"Risk assessment complete. Score: {risk_score}")
            
            return risk_report
            
        except Exception as e:
            context.log_error("RiskAgent", str(e), "ASSESSMENT_FAILED")
            return {
                "agent": "RiskAgent",
                "risk_score": 50,
                "error": str(e)
            }


class ComplianceAgent(BaseAgent):
    def __init__(self):
        policy = {
            "allow": ["compliance_agent/*", "compliance-mcp/*"],
            "deny": ["fraud_agent/*", "risk_agent/*", "memoryupdate_agent/*"]
        }
        super().__init__("compliance_agent", "ComplianceAgent", policy)
    
    def validate_compliance(self,
                          context: ExecutionContext,
                          fraud_report: Dict,
                          risk_report: Dict) -> Dict:
        self.logger.info("Starting compliance validation")
        
        try:
            compliance_steps = [
                {
                    "action": "check_aml_kyc",
                    "mcp": "compliance-mcp",
                    "params": {
                        "fraud_level": fraud_report["decision"],
                        "risk_score": risk_report.get("risk_score", 0)
                    },
                    "description": "Check AML/KYC compliance requirements"
                },
                {
                    "action": "validate_regulations",
                    "mcp": "compliance-mcp",
                    "params": {
                        "threat_type": fraud_report["decision"],
                        "input_type": context.media_type.value
                    },
                    "description": "Validate against applicable regulations"
                }
            ]
            
            prompt = f"""
Compliance Validation
====================
Fraud Status: {fraud_report['decision']}
Risk Score: {risk_report.get('risk_score', 'N/A')}
Input Type: {context.media_type.value}

Check compliance:
1. AML/KYC requirements
2. Data protection regulations
3. Content liability rules
4. Reporting obligations

Generate compliance status and required actions.
"""
            
            captured_plan = self._capture_plan(prompt, compliance_steps)
            token = self._get_intent_token(captured_plan)
            
            aml_result = self._invoke_action(
                token,
                "compliance-mcp",
                "check_aml_kyc",
                {
                    "fraud_level": fraud_report["decision"],
                    "risk_score": risk_report.get("risk_score", 0)
                }
            )
            
            context.log_action(
                "ComplianceAgent",
                "AML_KYC_CHECK",
                "EXECUTED",
                {"status": aml_result.get("data", {}).get("aml_status", "UNKNOWN")}
            )
            
            regulation_result = self._invoke_action(
                token,
                "compliance-mcp",
                "validate_regulations",
                {
                    "threat_type": fraud_report["decision"],
                    "input_type": context.media_type.value
                }
            )
            
            context.log_action(
                "ComplianceAgent",
                "REGULATION_VALIDATION",
                "EXECUTED",
                {"violations": regulation_result.get("data", {}).get("violations", [])}
            )
            
            compliance_report = {
                "agent": "ComplianceAgent",
                "timestamp": datetime.now().isoformat(),
                "aml_kyc_status": aml_result.get("data", {}).get("aml_status", "UNKNOWN"),
                "violations": regulation_result.get("data", {}).get("violations", []),
                "required_actions": regulation_result.get("data", {}).get("required_actions", []),
                "compliance_approved": len(regulation_result.get("data", {}).get("violations", [])) == 0
            }
            
            context.add_agent_report("ComplianceAgent", compliance_report)
            self.logger.info("Compliance validation complete")
            
            return compliance_report
            
        except Exception as e:
            context.log_error("ComplianceAgent", str(e), "VALIDATION_FAILED")
            return {
                "agent": "ComplianceAgent",
                "compliance_approved": False,
                "error": str(e)
            }


class MemoryUpdateAgent(BaseAgent):
    def __init__(self):
        policy = {
            "allow": ["memoryupdate_agent/*", "memory-mcp/*"],
            "deny": ["fraud_agent/*", "risk_agent/*", "compliance_agent/*"]
        }
        super().__init__("memoryupdate_agent", "MemoryUpdateAgent", policy)
    
    def finalize_and_log(self,
                        context: ExecutionContext) -> Dict:
        self.logger.info("Starting memory update and audit trail finalization")
        
        try:
            memory_steps = [
                {
                    "action": "consolidate_findings",
                    "mcp": "memory-mcp",
                    "params": {
                        "reports": context.agent_reports,
                        "blocked_actions": context.blocked_actions
                    },
                    "description": "Consolidate all agent findings"
                },
                {
                    "action": "generate_audit_trail",
                    "mcp": "memory-mcp",
                    "params": {
                        "session_id": context.session_id,
                        "audit_log": context.audit_trail,
                        "errors": context.errors
                    },
                    "description": "Generate complete audit trail"
                }
            ]
            
            prompt = f"""
Memory Update and Audit Trail Finalization
==========================================
Session: {context.session_id}
Timestamp: {context.execution_timestamp}

Consolidate all findings:
1. Fraud Agent findings
2. Risk Assessment results
3. Compliance validation
4. All blocked actions and errors

Generate comprehensive audit trail for future reference and learning.
"""
            
            captured_plan = self._capture_plan(prompt, memory_steps)
            token = self._get_intent_token(captured_plan)
            
            consolidation_result = self._invoke_action(
                token,
                "memory-mcp",
                "consolidate_findings",
                {
                    "reports": context.agent_reports,
                    "blocked_actions": context.blocked_actions
                }
            )
            
            context.log_action(
                "MemoryUpdateAgent",
                "CONSOLIDATION",
                "EXECUTED",
                {"summary": "All findings consolidated"}
            )
            
            audit_result = self._invoke_action(
                token,
                "memory-mcp",
                "generate_audit_trail",
                {
                    "session_id": context.session_id,
                    "audit_log": context.audit_trail,
                    "errors": context.errors
                }
            )
            
            context.log_action(
                "MemoryUpdateAgent",
                "AUDIT_TRAIL_GENERATION",
                "EXECUTED",
                {
                    "audit_log_entries": len(context.audit_trail),
                    "error_count": len(context.errors)
                }
            )
            
            memory_report = {
                "agent": "MemoryUpdateAgent",
                "timestamp": datetime.now().isoformat(),
                "session_id": context.session_id,
                "total_audit_entries": len(context.audit_trail),
                "blocked_actions_count": len(context.blocked_actions),
                "errors_count": len(context.errors),
                "consolidation_status": "SUCCESS"
            }
            
            context.add_agent_report("MemoryUpdateAgent", memory_report)
            self.logger.info("Memory update and audit trail finalization complete")
            
            return memory_report
            
        except Exception as e:
            context.log_error("MemoryUpdateAgent", str(e), "FINALIZATION_FAILED")
            return {
                "agent": "MemoryUpdateAgent",
                "consolidation_status": "FAILED",
                "error": str(e)
            }


class FinGuardOrchestrator:
    def __init__(self):
        self.fraud_agent = FraudAgent()
        self.risk_agent = RiskAgent()
        self.compliance_agent = ComplianceAgent()
        self.memory_agent = MemoryUpdateAgent()
        self.logger = logging.getLogger("FinGuardOrchestrator")
    
    def process_input(self,
                     user_input: str,
                     media_type: str,
                     mode: str,
                     metadata: Optional[Dict] = None) -> Dict:
        try:
            media = MediaType[media_type.upper()]
            exec_mode = ExecutionMode[mode.upper()]
        except KeyError as e:
            return {"error": f"Invalid media type or mode: {e}"}
        
        context = ExecutionContext(user_input, media, exec_mode, metadata)
        
        self.logger.info(f"Starting FinGuard analysis - Session: {context.session_id}")
        self.logger.info(f"Mode: {exec_mode.value}, Media Type: {media.value}")
        
        final_report = {
            "session_id": context.session_id,
            "timestamp": context.execution_timestamp,
            "mode": exec_mode.value,
            "media_type": media.value,
            "agent_reports": {},
            "audit_trail": [],
            "blocked_actions": [],
            "errors": [],
            "final_decision": "PENDING"
        }
        
        try:
            self.logger.info("=== STAGE 1: Fraud Analysis ===")
            fraud_report = self.fraud_agent.analyze(context)
            final_report["agent_reports"]["fraud_agent"] = fraud_report
            
            if fraud_report.get("decision") != AgentDecision.SAFE.value and \
               fraud_report.get("escalate_to_risk", False):
                
                self.logger.info("=== STAGE 2: Risk Assessment (Delegated) ===")
                risk_report = self.risk_agent.assess_risk(context, fraud_report)
                final_report["agent_reports"]["risk_agent"] = risk_report
                
                if risk_report.get("escalate_to_compliance", False):
                    self.logger.info("=== STAGE 3: Compliance Validation (Delegated) ===")
                    compliance_report = self.compliance_agent.validate_compliance(
                        context, fraud_report, risk_report
                    )
                    final_report["agent_reports"]["compliance_agent"] = compliance_report
            
            self.logger.info("=== STAGE 4: Audit Trail Finalization ===")
            memory_report = self.memory_agent.finalize_and_log(context)
            final_report["agent_reports"]["memory_agent"] = memory_report
            
            final_decision = self._determine_final_decision(final_report)
            final_report["final_decision"] = final_decision
            
            final_report["audit_trail"] = context.audit_trail
            final_report["blocked_actions"] = context.blocked_actions
            final_report["errors"] = context.errors
            
            self.logger.info(f"FinGuard analysis complete. Final Decision: {final_decision}")
            
        except Exception as e:
            self.logger.error(f"Orchestrator error: {str(e)}", exc_info=True)
            context.log_error("FinGuardOrchestrator", str(e), "ORCHESTRATION_FAILED")
            final_report["error"] = str(e)
            final_report["audit_trail"] = context.audit_trail
            final_report["errors"] = context.errors
        
        return final_report
    
    def _determine_final_decision(self, final_report: Dict) -> str:
        fraud_decision = final_report.get("agent_reports", {}).get("fraud_agent", {}).get("decision", "SAFE")
        risk_score = final_report.get("agent_reports", {}).get("risk_agent", {}).get("risk_score", 0)
        compliance_approved = final_report.get("agent_reports", {}).get("compliance_agent", {}).get("compliance_approved", True)
        
        if fraud_decision == AgentDecision.FRAUD.value:
            if risk_score > 80:
                return "BLOCK_IMMEDIATELY"
            elif not compliance_approved:
                return "ESCALATE_TO_AUTHORITIES"
            else:
                return "FRAUD_DETECTED_MONITOR"
        elif fraud_decision == AgentDecision.CHECK_REQUIRED.value:
            return "REQUIRE_MANUAL_REVIEW"
        else:
            return "SAFE_APPROVED"


def main():
    print("\n" + "="*50)
    print("FinGuard Multi-Agent Financial Defense System")
    print("Powered by ArmorClaw")
    print("="*50 + "\n")
    
    orchestrator = FinGuardOrchestrator()
    
    try:
        user_input = input("Enter your input (or file path for media): ").strip()
        if not user_input:
            print("Input cannot be empty!")
            return
        
        media_type = input("Media type (text/image/audio/video/document): ").strip().upper()
        if media_type not in ["TEXT", "IMAGE", "AUDIO", "VIDEO", "DOCUMENT"]:
            print("Invalid media type!")
            return
        
        mode = input("Mode (ASK/COMMAND): ").strip().upper()
        if mode not in ["ASK", "COMMAND"]:
            print("Invalid mode!")
            return
        
        final_report = orchestrator.process_input(
            user_input=user_input,
            media_type=media_type,
            mode=mode,
            metadata={"source": "cli_input"}
        )
        
        print("\n" + "="*50)
        print("FINAL REPORT")
        print("="*50)
        print(json.dumps(final_report, indent=2, default=str))
        
        with open("fingard_final_report.json", "w") as f:
            json.dump(final_report, f, indent=2, default=str)
        print("\n✓ Full report saved to fingard_final_report.json")
        print("✓ Audit trail saved to fingard_audit.log")
        
    except KeyboardInterrupt:
        print("\n\nFinGuard execution cancelled by user.")
    except Exception as e:
        print(f"\nError during execution: {str(e)}")
        logging.exception("Fatal error in main execution")


if __name__ == "__main__":
    main()
