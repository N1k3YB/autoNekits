import os
from dotenv import load_dotenv


load_dotenv()


PG_HOST=os.getenv("PG_HOST")
PG_PORT=os.getenv("PG_PORT")
PG_USER=os.getenv("PG_USER")
PG_PASSWORD=os.getenv("PG_PASSWORD")
PG_DB=os.getenv("PG_DB")


MS_HOST=os.getenv("MS_HOST")
MS_USER=os.getenv("MS_USER")
MS_PASSWORD=os.getenv("MS_PASSWORD")
TRUST_CONNECTION="yes"

GIT_URL=os.getenv("GIT_URL")
GIT_PORT=os.getenv("GIT_PORT")
GIT_PREFIX=os.getenv("GIT_PREFIX")


