package com.example.application.services;

import com.example.application.data.Metrics;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.mongodb.client.*;
import com.mongodb.client.gridfs.GridFSBuckets;
import com.mongodb.client.gridfs.GridFSDownloadStream;
import com.mongodb.client.model.Filters;
import io.github.cdimascio.dotenv.Dotenv;
import org.bson.Document;
import org.bson.types.ObjectId;
import org.springframework.stereotype.Service;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.Objects;
import java.util.Set;
import java.util.HashSet;
import java.util.zip.GZIPInputStream;

import static org.atmosphere.annotation.AnnotationUtil.logger;

@Service
public class MongoDBService {
    private final MongoClient client;
    private final MongoDatabase database;
    private final String collectionName;
    private static final ObjectMapper objectMapper = new ObjectMapper();

    public MongoDBService() {
        Dotenv dotenv = Dotenv.load();
        String uri = dotenv.get("MONGO_URI");
        String dbName = dotenv.get("MONGO_DB_NAME");
        this.collectionName = dotenv.get("MONGO_COLLECTION_NAME");

        this.client = MongoClients.create(uri);
        this.database = client.getDatabase(dbName);
    }

    public Set<String> fetchAllIds() {
        MongoCollection<Document> collection = database.getCollection(this.collectionName, Document.class);
        MongoCursor<Document> cursor = collection.find().iterator();
        Set<String> ids = new HashSet<>();

        try {
            while (cursor.hasNext()) {
                Document document = cursor.next();
                Object idObject = document.get("key");
                if (idObject instanceof ObjectId objectId) {
                    ids.add(objectId.toString());
                } else if (idObject instanceof String) {
                    ids.add((String) idObject);
                }
            }
        } finally {
            cursor.close();
        }

        return ids;
    }


    public Metrics fetchMetricsByKey(String key) {
        try {
            Document doc = findDocumentByKey(key);
            if (doc == null || !doc.containsKey("file_id")) {
                return null;
            }

            ObjectId fileId = doc.getObjectId("file_id");
            return decompressAndDeserialize(fileId);
        } catch (Exception e) {
            logger.error("Error fetching metrics by key: {}", key, e);
            return null;
        }
    }

    private Document findDocumentByKey(String key) {
        MongoCollection<Document> collection = database.getCollection(collectionName);
        return Objects.requireNonNull(collection.find(Filters.eq("key", key)).first());
    }

    private Metrics decompressAndDeserialize(ObjectId fileId) throws IOException {
        try (GridFSDownloadStream downloadStream = GridFSBuckets.create(database).openDownloadStream(fileId);
             GZIPInputStream gzipInputStream = new GZIPInputStream(downloadStream);
             ByteArrayOutputStream decompressedStream = new ByteArrayOutputStream()) {
            byte[] buffer = new byte[8192];
            int len;
            while ((len = gzipInputStream.read(buffer)) > 0) {
                decompressedStream.write(buffer, 0, len);
            }
            String jsonString = decompressedStream.toString("UTF-8");
            return objectMapper.readValue(jsonString, Metrics.class);
        }
    }

}
