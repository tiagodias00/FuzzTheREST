package com.example.application.services;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicReference;
import java.util.stream.Collectors;


public class SchemaDataService {
    public SchemaDataService() {
    }
        private final AtomicReference<List<SchemaIdentifierPair>> schemaIdentifierPairs = new AtomicReference<>();


    public void setSchemaIdentifierPairs(List<SchemaIdentifierPair> pairs) {
        schemaIdentifierPairs.set(pairs);
    }

    public List<SchemaIdentifierPair> getSchemaIdentifierPairs() {
        List<SchemaIdentifierPair> data = schemaIdentifierPairs.get();
        return data;
    }



    public static class SchemaIdentifierPair {
            private final String schemaName;
            private final String identifierName;

            public SchemaIdentifierPair(String schemaName, String identifierName) {
                this.schemaName = schemaName;
                this.identifierName = identifierName;
            }

            public String getSchemaName() {
                return schemaName;
            }

            public String getIdentifierName() {
                return identifierName;
            }
        public static String convertToJson(List<SchemaIdentifierPair> pairs) {
            ObjectMapper mapper = new ObjectMapper();

            Map<String, String> idsMap = pairs.stream()
                    .collect(Collectors.toMap(
                            SchemaIdentifierPair::getSchemaName,
                            SchemaIdentifierPair::getIdentifierName,
                            (existing, replacement) -> existing));
            try {
                return mapper.writeValueAsString(idsMap);
            } catch (IOException e) {
                e.printStackTrace();
                return "{}";  // Return an empty object on failure
            }
        }

    }
    }


