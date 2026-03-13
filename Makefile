
ifneq (,$(wildcard .env))
include .env
export
endif


setup : 
	pip install -e . 

launch-mlflow-server :
	echo "Launching MLflow server... "
	echo "All parameters are default in this command but you can customize them as needed."
	mlflow server --backend-store-uri sqlite:///models/mlflow.db --default-artifact-root ./models/mlartifacts --host 0.0.0.0 --port 5000

launch-docker-mlflow-server :
	echo "Launching MLflow server in Docker... "
	docker pull ghcr.io/mlflow/mlflow
	docker run -d -p 5000:5000  --name mlflow-server mlflow

###########
#ML
##########

train : 	
	python -m diamonds.train

###########
#API
##########

test_api_get:
	@curl -X 'GET' \
	'http://127.0.0.1:${PORT}/diamond_price?carat=1&cut=Ideal&color=E&clarity=SI2&depth=1&table=0&x=1&y=1&z=1' \
	-H 'accept: application/json'

test_api_post:
	curl -X 'POST' \
	'http://127.0.0.1:${PORT}/predict_one' \
	-H 'accept: application/json' \
	-H 'Content-Type: application/json' \
	-d '{"carat": 0,"cut": "Ideal","color": "E","clarity": "SI2","depth": 0,"table": 0,"x": 0,"y": 0,"z": 0}'


###########
#Docker
##########

build:
	docker build -t ${IMAGE} --file api/Dockerfile .   

run:
	 docker run -p ${HOST_PORT}:${PORT} -e PORT=${PORT} ${IMAGE}


build_gcp :
	docker build --platform=linux/amd64 -t ${REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${REPOSITORY_NAME}/${IMAGE} --file api/Dockerfile .

push_gcp : build_gcp
	docker push ${REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${REPOSITORY_NAME}/${IMAGE}

deploy_gcp : push_gcp
	gcloud run deploy ${IMAGE} --image ${REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${REPOSITORY_NAME}/${IMAGE} --region ${REGION} --platform managed --allow-unauthenticated

auth_gcp: 
	gcloud auth login
	gcloud config set project ${GCP_PROJECT_ID}



# submit_gcp:
# 	gcloud builds submit --tag gcr.io/${GCP_PROJECT_ID}/${IMAGE} .