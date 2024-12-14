"""Evaluation System Orchestrator init module"""
from evaluation_system.testing_state import TESTING  # must be first
from evaluation_system.evaluation_system_orchestrator import EvaluationSystemOrchestrator


# Prepare and run the Evaluation System Orchestrator, having set TESTNG value
if __name__ == "__main__":
    print("init start")
    app = EvaluationSystemOrchestrator()
    print("orchestrator loaded")
    app.run()
    print("end")
