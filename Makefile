.PHONY: run ollama attack help

# Default target
.DEFAULT_GOAL := help

help:
	@echo "Agent Zero Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make run      - Launch standard standalone Agent Zero container (port 8080)"
	@echo "  make ollama   - Launch Agent Zero with local Ollama LLM integration (port 50001)"
	@echo "  make attack   - Launch security attack lab with OWASP Juice Shop target (port 50001)"
	@echo ""

run:
	bash ./run.sh

ollama:
	bash ./ollama.sh

attack:
	bash ./attack.sh
