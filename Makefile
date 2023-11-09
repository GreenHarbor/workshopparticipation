lint:
	@flake8 src --ignore=E501 && pylint --fail-under=6 src

run:
	@python src/app.py

test:
	@docker compose -f ci/compose.test.yaml up --exit-code-from workshop-part-pytest --build