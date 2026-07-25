.PHONY: up down trigger help

# Start all services (Docker, Backend, Detector, Frontend)
up:
	@echo "Starting AXIS Prototype..."
	@bash start_all.sh

# Trigger the mock flight cancellation event
trigger:
	@echo "Triggering Disruption Event..."
	@bash trigger_disruption.sh

# Shut down Docker infrastructure and clean up
down:
	@echo "Stopping AXIS Prototype..."
	@docker compose down
	@echo "Cleaned up Docker containers."

# Print help message
help:
	@echo "AXIS Prototype Makefile Commands:"
	@echo ""
	@echo "  make up       - Start all services (Infrastructure, Backend, Detector, Frontend)"
	@echo "  make trigger  - Trigger the mock flight cancellation event (AX100)"
	@echo "  make down     - Stop and remove Docker containers"
	@echo ""
	@echo "Note: If running in GitHub Codespaces, ensure Port 8000 is set to 'Public' in the Ports tab."