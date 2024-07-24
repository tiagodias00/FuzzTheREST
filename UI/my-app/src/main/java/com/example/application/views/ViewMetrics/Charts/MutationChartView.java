package com.example.application.views.ViewMetrics.Charts;

import com.example.application.data.Metrics;
import com.google.gson.Gson;
import com.vaadin.flow.component.dependency.JsModule;
import com.vaadin.flow.component.html.Div;
import com.vaadin.flow.component.orderedlayout.VerticalLayout;
import com.vaadin.flow.server.VaadinSession;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@JsModule("./charts/plotly-vaadin.js")
public class MutationChartView extends VerticalLayout {

    public MutationChartView(Metrics.RequestsMetrics metrics) {
        Div chartContainer = new Div();
        chartContainer.setId("mutationChart");
        add(chartContainer);
        setSizeFull();

        // Extracting and preparing data
        List<String> dataTypes = List.of("int", "float", "bool", "byte", "string");
        Map<String, Map<String, Integer>> originalMutationCounts = metrics.getMutation_counts();
        Map<String, Map<String, Integer>> mutationCounts = new HashMap<>();

        // Restructure data to have mutation methods as top-level keys
        Map<String, Map<String, Integer>> restructuredCounts = new HashMap<>();
        for (Map.Entry<String, Map<String, Integer>> entry : originalMutationCounts.entrySet()) {
            String dataTypeIndex = entry.getKey();
            String dataType = dataTypes.get(Integer.parseInt(dataTypeIndex));
            Map<String, Integer> counts = entry.getValue();

            for (Map.Entry<String, Integer> countEntry : counts.entrySet()) {
                String method = countEntry.getKey();
                Integer count = countEntry.getValue();

                restructuredCounts.computeIfAbsent(method, k -> new HashMap<>()).put(dataType, count);
            }
        }

        MutationData mutationData = new MutationData();
        mutationData.setMutationMethods(new ArrayList<>(restructuredCounts.keySet()));
        mutationData.setMutationCounts(restructuredCounts);

        Gson gson = new Gson();
        String dataJson = gson.toJson(mutationData);

        chartContainer.getElement().executeJs("window.renderMutationChart($0, $1)", chartContainer.getId().get(), dataJson);
    }

    private static class MutationData {
        private List<String> mutationMethods;
        private Map<String, Map<String, Integer>> mutationCounts;

        public List<String> getMutationMethods() {
            return mutationMethods;
        }

        public void setMutationMethods(List<String> mutationMethods) {
            this.mutationMethods = mutationMethods;
        }

        public Map<String, Map<String, Integer>> getMutationCounts() {
            return mutationCounts;
        }

        public void setMutationCounts(Map<String, Map<String, Integer>> mutationCounts) {
            this.mutationCounts = mutationCounts;
        }
    }
}
