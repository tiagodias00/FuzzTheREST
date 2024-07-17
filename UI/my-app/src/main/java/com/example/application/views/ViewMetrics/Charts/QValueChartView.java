package com.example.application.views.ViewMetrics.Charts;

import com.vaadin.flow.component.dependency.JsModule;
import com.vaadin.flow.component.html.Div;
import com.vaadin.flow.component.orderedlayout.VerticalLayout;
import com.example.application.data.Metrics;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

@JsModule("./charts/plotly-vaadin.js")
public class QValueChartView extends VerticalLayout {

    public QValueChartView(int episodes, Metrics.RequestsMetrics.QValueConvergence qValueConvergence) {
        Div chartContainer = new Div();
        chartContainer.setId("plotlyChart");
        add(chartContainer);
        setSizeFull();

        List<List<Double>> allData = new ArrayList<>();
        List<String> xData = new ArrayList<>();
        for (int i = 1; i <= episodes; i++) {
            xData.add(String.valueOf(i));
        }

        String[] dataTypes = {"int", "float", "bool", "byte", "string"};
        for (String dataType : dataTypes) {
            Double[] avgQValues = calculateAverageQValues(episodes, qValueConvergence, dataType);
            List<Double> yData = new ArrayList<>();
            Collections.addAll(yData, avgQValues);
            allData.add(yData);
        }

        String dataJson = convertDataToJson(dataTypes, xData, allData);
        chartContainer.getElement().executeJs("window.renderPlotlyChart($0, $1)", chartContainer.getId().get(), dataJson);
    }

    private String convertDataToJson(String[] dataTypes, List<String> xData, List<List<Double>> allData) {
        StringBuilder dataBuilder = new StringBuilder("[");
        for (int i = 0; i < dataTypes.length; i++) {
            dataBuilder.append("{");
            dataBuilder.append("\"x\": ").append(xData.toString()).append(",");
            dataBuilder.append("\"y\": ").append(allData.get(i).toString()).append(",");
            dataBuilder.append("\"type\": \"scatter\",");
            dataBuilder.append("\"mode\": \"lines+markers\",");
            dataBuilder.append("\"name\": \"").append(dataTypes[i]).append("\"");
            dataBuilder.append("},");
        }
        dataBuilder.deleteCharAt(dataBuilder.length() - 1);  // Remove the last comma
        dataBuilder.append("]");
        return dataBuilder.toString();
    }

    private Double[] calculateAverageQValues(int numEpisodes, Metrics.RequestsMetrics.QValueConvergence qValueConvergence, String dataType) {
        List<List<List<Double>>> qValuesList = qValueConvergence.getQValues(dataType);
        Double[] avgQValues = new Double[numEpisodes];

        for (int i = 0; i < numEpisodes; i++) {
            double sum = 0;
            int count = 0;
            for (int j = 0; j < qValuesList.get(i).size(); j++) {
                for (int k = 0; k < qValuesList.get(i).get(j).size(); k++) {
                    sum += qValuesList.get(i).get(j).get(k);
                    count++;
                }
            }
            avgQValues[i] = count > 0 ? sum / count : 0;
        }
        return avgQValues;
    }
}
