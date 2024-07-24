FROM openjdk:8-jre-alpine

WORKDIR /petstore

# Add JaCoCo Java Agent JAR to the container
COPY jacocoagent.jar /petstore/jacocoagent.jar

ENV OPENAPI_BASE_PATH=/v3

COPY target/openapi-petstore-3.0.0.jar /petstore/openapi-petstore.jar

EXPOSE 8080

# Update CMD to include the JaCoCo Java Agent and its JVM arguments
CMD ["java", "-javaagent:/petstore/jacocoagent.jar=destfile=/petstore/jacoco.exec", "-Dopenapi.openAPIPetstore.base-path=${OPENAPI_BASE_PATH}", "-jar", "/petstore/openapi-petstore.jar"]