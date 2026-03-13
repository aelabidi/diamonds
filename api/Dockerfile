FROM python:3.11-slim

WORKDIR /api

COPY api/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY src src
COPY pyproject.toml pyproject.toml
RUN pip install .

# Bad Practice mais on ne peut pas faire autrement pour le moment.
COPY models/pipeline.pkl models/pipeline.pkl

COPY api/templates api/templates
COPY api/static api/static
COPY api api

ENV MODEL_FOLDER="models"

CMD ["sh", "-c", "fastapi run api/rest.py --host 0.0.0.0 --port ${PORT:-8080}"]