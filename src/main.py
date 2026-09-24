# Fastapi dependencies
from fastapi import FastAPI


# App object
app = FastAPI()

# Healthcheck
@app.get('/', include_in_schema=False)
def healthcheck() -> dict:
    return {'Healthcheck':'passed!'}
