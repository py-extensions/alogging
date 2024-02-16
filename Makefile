lint:
	poetry run pylint .

format:
	poetry run autoflake -i -r .
	poetry run black .
	poetry run isort --profile=black .

format-check:
	poetry run autoflake --check -r .
	poetry run black --check .
	poetry run isort -c --profile=black .

test:
	poetry run pytest .

install:
	poetry install --no-root

publish:
	poetry publish --build
