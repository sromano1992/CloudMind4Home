docker build -t cloudmind4home/streaming:v1 .
docker run cloudmind4home/streaming:v1

# FROM Google Cloud Shell
//https://cloud.google.com/kubernetes-engine/docs/tutorials/hello-app
export PROJECT_ID=cloudmind4home
git clone https://github.com/sromano1992/CloudMind4Home.git
cd streaming
mvn clean install
docker build -t gcr.io/${PROJECT_ID}/cloudmind4home/streaming:v1 .
docker push gcr.io/${PROJECT_ID}/cloudmind4home/streaming:v1
docker run gcr.io/${PROJECT_ID}/cloudmind4home/streaming:v1
## GKE deploy
//https://cloud.google.com/kubernetes-engine/docs/tutorials/hello-app
kubectl create deployment streaming-deployment --image=gcr.io/${PROJECT_ID}/cloudmind4home/streaming:v1
