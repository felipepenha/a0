.PHONY: run ollama attack help

# Default target
.DEFAULT_GOAL := help

help:
	@echo "Agent Zero Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make run - Launch standard standalone Agent Zero container (port 8080)"
	@echo ""

run:
	bash ./run.sh
