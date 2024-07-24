package com.example.application.views.ViewMetrics.Charts;

import com.google.gson.Gson;
import com.vaadin.flow.component.dependency.JsModule;
import com.vaadin.flow.component.html.Div;
import com.vaadin.flow.component.orderedlayout.VerticalLayout;

import java.util.Arrays;
import java.util.List;

@JsModule("./charts/plotly-vaadin.js")
public class StateVisitsChartView extends VerticalLayout {

    public StateVisitsChartView(List<Double> stateVisits) {
        Div chartContainer = new Div();
        chartContainer.setId("stateVisitsChart");
        add(chartContainer);
        setSizeFull();

        StateVisitsData stateVisitsData = new StateVisitsData();
        stateVisitsData.setStates(Arrays.asList("1XX", "2XX", "3XX", "4XX", "5XX"));
        stateVisitsData.setVisitCounts(stateVisits);

        Gson gson = new Gson();
        String dataJson = gson.toJson(stateVisitsData);

        chartContainer.getElement().executeJs("window.renderStateVisitsChart($0, $1)", chartContainer.getId().get(), dataJson);
    }

    private static class StateVisitsData {
        private List<String> states;
        private List<Double> visitCounts;

        public List<String> getStates() {
            return states;
        }

        public void setStates(List<String> states) {
            this.states = states;
        }

        public List<Double> getVisitCounts() {
            return visitCounts;
        }

        public void setVisitCounts(List<Double> visitCounts) {
            this.visitCounts = visitCounts;
        }
    }
}
