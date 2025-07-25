import sys
from main import DocumentIntelligenceSystem

print("Testing Document Intelligence System")
system = DocumentIntelligenceSystem()
result = system.process_collection("input", "output")
print("Result:", result)
