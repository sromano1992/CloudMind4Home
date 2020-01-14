# https://github.com/GoogleContainerTools/distroless/blob/master/java/README.md
FROM gcr.io/distroless/java:8
ENV GOOGLE_APPLICATION_CREDENTIALS /cloudmind4home-466bc3b3211d.json
# copy WAR into image
COPY target/streaming-uber-jar.jar /streaming-uber-jar.jar
COPY src/main/resources/config.properties /config.properties
COPY src/main/resources/cloudmind4home-466bc3b3211d.json /cloudmind4home-466bc3b3211d.json
# run application with this command line
CMD ["/streaming-uber-jar.jar", "/config.properties"]