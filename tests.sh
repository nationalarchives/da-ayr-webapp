echo "Running Unit Tests"
pytest -s
echo "Running Flake 8"
flake8 ayr_project tests
