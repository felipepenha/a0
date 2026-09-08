.PHONY: run help

# Default target
.DEFAULT_GOAL := help

help:
	@echo "Agent Zero Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make run  - Launch Agent Zero container (port 8080)"
	@echo ""

run:
	bash ./run.sh
