package com.example.application.views.ViewMetrics;

import com.example.application.data.Metrics;
import com.example.application.services.MongoDBService;
import com.vaadin.flow.component.Text;
import com.vaadin.flow.component.button.Button;
import com.vaadin.flow.component.combobox.ComboBox;
import com.vaadin.flow.component.dependency.CssImport;
import com.vaadin.flow.component.details.Details;
import com.vaadin.flow.component.orderedlayout.HorizontalLayout;
import com.vaadin.flow.component.orderedlayout.VerticalLayout;
import com.vaadin.flow.component.textfield.TextField;
import com.vaadin.flow.data.renderer.ComponentRenderer;
import com.vaadin.flow.router.Route;
import com.vaadin.flow.router.BeforeEnterObserver;
import com.vaadin.flow.router.BeforeEnterEvent;
import com.vaadin.flow.router.RouteParameters;
import com.vaadin.flow.component.UI;
import com.vaadin.flow.server.VaadinSession;

import com.vaadin.flow.component.grid.Grid;
import com.vaadin.flow.component.html.Span;

import java.util.List;
import java.util.stream.Collectors;


@Route("display-fuzzing-metrics/:id")
@CssImport("./themes/fuzztherest/styles.css")
public class DisplayFuzzingMetrics extends VerticalLayout implements BeforeEnterObserver {

    private  MongoDBService mongoDBService;
    private ComboBox<Metrics.RequestsMetrics> requestsMetricsComboBox = new ComboBox<>("Select Request Metric");
    private Button detailButton = new Button("View Details");
    private Button crashDetailsButton = new Button("View All Crashes");
    private TextField durationField = new TextField("Fuzzing Time");
    private TextField executionsPerSecondField = new TextField("Executions per Second");
    private TextField uniqueCrashes= new TextField("Unique Crashes");
    private int episodes;
    private Grid<Metrics.Hang> hangGrid = new Grid<>(Metrics.Hang.class);
    private Button backButton = new Button("Go Back");


    public DisplayFuzzingMetrics(MongoDBService mongoDBService) {
        this.mongoDBService = mongoDBService;
        setSizeFull();
        getStyle().set("overflow-y", "auto");
        setupGrids();

        requestsMetricsComboBox.setItemLabelGenerator(Metrics.RequestsMetrics::getName);
        requestsMetricsComboBox.setWidthFull();
        durationField.setReadOnly(true);
        executionsPerSecondField.setReadOnly(true);
        durationField.setWidthFull();
        uniqueCrashes.setReadOnly(true);

        backButton.addClickListener(event -> UI.getCurrent().getPage().executeJs("history.back()"));


        detailButton.addClickListener(event -> {
            Metrics.RequestsMetrics selectedMetric = requestsMetricsComboBox.getValue();
            if (selectedMetric != null) {
                VaadinSession.getCurrent().setAttribute("selectedMetric", selectedMetric);
                VaadinSession.getCurrent().setAttribute("episodes", episodes);
                UI.getCurrent().navigate("metric-detail");
            }
        });
        crashDetailsButton.addClickListener(event -> {
                UI.getCurrent().navigate("crash-details");

        });
        Span crashGridHeader = new Span("Crash Details");
        Span hangGridHeader = new Span("Hang Details");
        Span info = new Span("Info");

        add(new VerticalLayout(info,durationField,executionsPerSecondField,requestsMetricsComboBox, detailButton));
        HorizontalLayout crashLayout = new HorizontalLayout(uniqueCrashes, crashDetailsButton);
        crashLayout.setDefaultVerticalComponentAlignment(Alignment.BASELINE);
        add(new VerticalLayout(crashGridHeader, crashLayout));
        add(new VerticalLayout(hangGridHeader, hangGrid));
        add(backButton);
    }

    @Override
    public void beforeEnter(BeforeEnterEvent event) {

        RouteParameters params = event.getRouteParameters();
        String documentId = params.get("id").orElse(null);
        if (documentId != null) {
            Metrics metrics = (Metrics) VaadinSession.getCurrent().getAttribute("metrics");
            if (metrics == null || !metrics.getId().equals(documentId)) {
                metrics = mongoDBService.fetchMetricsByKey(documentId);
                metrics.setId(documentId);
                VaadinSession.getCurrent().setAttribute("metrics", metrics);
            }
            List<Metrics.RequestsMetrics> filteredMetrics = metrics.getRequests_metrics().stream()
                    .filter(metric -> !metric.getName().startsWith("Test"))
                    .collect(Collectors.toList());
            VaadinSession.getCurrent().setAttribute("selectedId", documentId);
            requestsMetricsComboBox.setItems(filteredMetrics);
            episodes=metrics.getEpisodes();
            requestsMetricsComboBox.setPlaceholder("Choose a metric...");
            String duration = calculateFuzzingDuration(metrics.getDuration());
            durationField.setValue(duration);
            int totalExecutions = metrics.getEpisodes() * metrics.getRequests_metrics().size();
            double executionsPerSecond = (double) totalExecutions / metrics.getDuration();
            executionsPerSecondField.setValue(String.format("%.2f", executionsPerSecond));
            hangGrid.setItems(metrics.getHangs().values());
            uniqueCrashes.setValue(String.valueOf(metrics.getCrashes().size()));
        }
    }
    private void setupGrids() {
        hangGrid.addClassName("wrap-cell-content");


        hangGrid.setColumns("count", "error_message", "url", "method", "parameters");
        hangGrid.getColumnByKey("count").setHeader("Count");
        hangGrid.getColumnByKey("error_message").setHeader("Error Message");
        hangGrid.getColumnByKey("url").setHeader("URL");
        hangGrid.getColumnByKey("method").setHeader("Method");
        hangGrid.getColumnByKey("parameters").setHeader("Parameters");

    }

    private String calculateFuzzingDuration(int durationInSeconds) {

        long hours = durationInSeconds / 3600;
        long minutes = (durationInSeconds % 3600) / 60;
        long seconds = durationInSeconds % 60;

        StringBuilder duration = new StringBuilder();

        if (hours > 0) {
            duration.append(hours).append(" hour");
            if (hours > 1) {
                duration.append("s");
            }
        }

        if (minutes > 0) {
            if (!duration.isEmpty()) {
                duration.append(", ");
            }
            duration.append(minutes).append(" minute");
            if (minutes > 1) {
                duration.append("s");
            }
        }

        if (seconds > 0) {
            if (!duration.isEmpty()) {
                duration.append(", and ");
            }
            duration.append(seconds).append(" second");
            if (seconds > 1) {
                duration.append("s");
            }
        }

        return duration.toString();
    }
    }


