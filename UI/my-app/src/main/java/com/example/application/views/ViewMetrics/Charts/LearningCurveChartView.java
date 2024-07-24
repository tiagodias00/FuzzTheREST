package com.example.application.views.ViewMetrics.Charts;

import com.google.gson.Gson;
import com.vaadin.flow.component.dependency.JsModule;
import com.vaadin.flow.component.html.Div;
import com.vaadin.flow.component.orderedlayout.VerticalLayout;

import java.util.ArrayList;
import java.util.List;

@JsModule("./charts/plotly-vaadin.js")
public class LearningCurveChartView extends VerticalLayout {

    public LearningCurveChartView(List<Double> episodeRewards, int windowSize) {
        Div chartContainer = new Div();
        chartContainer.setId("learningCurveChart");
        add(chartContainer);
        setSizeFull();
        List<Double> averageRewards = calculateRollingAverage(episodeRewards, windowSize);

        LearningCurveData learningCurveData = new LearningCurveData();
        learningCurveData.setAverageRewards(averageRewards);
        learningCurveData.setWindowSize(windowSize);


        Gson gson = new Gson();
        String dataJson = gson.toJson(learningCurveData);

        chartContainer.getElement().executeJs("window.renderLearningCurveChart($0, $1)", chartContainer.getId().get(), dataJson);
    }

    private static class LearningCurveData {
        private List<Double> averageRewards;
        private int windowSize;

        public List<Double> getAverageRewards() {
            return averageRewards;
        }

        public void setAverageRewards(List<Double> averageRewards) {
            this.averageRewards = averageRewards;
        }

        public int getWindowSize() {
            return windowSize;
        }

        public void setWindowSize(int windowSize) {
            this.windowSize = windowSize;
        }
    }
    public static List<Double> calculateRollingAverage(List<Double> episodeRewards, int windowSize) {
        List<Double> averageRewards = new ArrayList<>();
        for (int i = 0; i <= episodeRewards.size() - windowSize; i=i+windowSize) {
            double sum = 0;
            for (int j = 0; j < windowSize; j++) {
                sum += episodeRewards.get(i + j);
            }
            averageRewards.add(sum / windowSize);
        }
        return averageRewards;
    }
}
