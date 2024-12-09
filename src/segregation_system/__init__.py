import sys
from src.segregation_system.SegregationSystemOrchestrator import SegregationSystemOrchestrator

def main():
    controller = SegregationSystemOrchestrator()
    controller.run()
    sys.exit(0)

if __name__ == "__main__":
    main()