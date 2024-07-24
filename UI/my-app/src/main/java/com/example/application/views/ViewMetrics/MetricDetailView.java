package com.example.application.views.ViewMetrics;

import com.example.application.data.Metrics;

import com.example.application.views.ViewMetrics.Charts.LearningCurveChartView;
import com.example.application.views.ViewMetrics.Charts.MutationChartView;
import com.example.application.views.ViewMetrics.Charts.QValueChartView;
import com.example.application.views.ViewMetrics.Charts.StateVisitsChartView;
import com.vaadin.flow.component.UI;
import com.vaadin.flow.component.button.Button;
import com.vaadin.flow.component.dependency.CssImport;
import com.vaadin.flow.component.orderedlayout.HorizontalLayout;
import com.vaadin.flow.component.orderedlayout.VerticalLayout;
import com.vaadin.flow.router.Route;
import com.vaadin.flow.router.PageTitle;
import com.vaadin.flow.server.VaadinSession;

@Route("metric-detail")
@PageTitle("Metric Details")
@CssImport("./themes/fuzztherest/styles.css")
public class MetricDetailView extends VerticalLayout{

    private Metrics.RequestsMetrics metric;
    private int episodes;
    private String selectedId;

    public MetricDetailView() {
        metric = (Metrics.RequestsMetrics) VaadinSession.getCurrent().getAttribute("selectedMetric");
        episodes= (int) VaadinSession.getCurrent().getAttribute("episodes");
        selectedId = (String) VaadinSession.getCurrent().getAttribute("selectedId");


        QValueChartView chartView = new QValueChartView(episodes, metric.getQ_value_convergence());
        MutationChartView mutationChartView = new MutationChartView(metric);
        StateVisitsChartView stateVisitsChartView = new StateVisitsChartView(metric.getState_visits());
        LearningCurveChartView learningCurveChartView = new LearningCurveChartView(metric.getEpisode_rewards(), 100);
        HorizontalLayout row1 = new HorizontalLayout(chartView, mutationChartView);
        HorizontalLayout row2 = new HorizontalLayout(stateVisitsChartView,learningCurveChartView);

        row1.setWidthFull();
        row2.setWidthFull();

        Button backButton = new Button("Back to Metrics");
        backButton.addClickListener(event -> {
            UI.getCurrent().navigate("display-fuzzing-metrics/" + selectedId);
        });

        add(backButton, row1, row2);

        setSizeFull();
    }
}



