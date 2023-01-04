echo "Running Unit Tests"
pytest -s
echo "Running Flake 8"
flake8 app project tests
