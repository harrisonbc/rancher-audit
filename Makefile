.PHONY: install audit rotate clean

# Installs the required Python packages
install:
	pip install -r requirements.txt

# Runs the main audit script to generate the Excel report
audit:
	python3 rancher-audit.py

# Runs the token rotation script and creates a backup of the config
rotate:
	python3 rotate-rancher-tokens.py

# Cleans up the directory by removing the spreadsheet and config backups
clean:
	rm -f *.xlsx *.bak
	@echo "Cleaned up Excel reports and config backups."
