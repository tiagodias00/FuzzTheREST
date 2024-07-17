package com.example.application.views.ViewMetrics;

import com.example.application.data.Metrics;
import com.vaadin.flow.component.Text;
import com.vaadin.flow.component.UI;
import com.vaadin.flow.component.button.Button;
import com.vaadin.flow.component.dependency.CssImport;
import com.vaadin.flow.component.html.Div;
import com.vaadin.flow.component.html.H2;
import com.vaadin.flow.component.orderedlayout.HorizontalLayout;
import com.vaadin.flow.component.orderedlayout.VerticalLayout;
import com.vaadin.flow.router.Route;
import com.vaadin.flow.server.VaadinSession;


@Route("crash-details")
@CssImport("./themes/fuzztherest/styles.css")
public class CrashDetailsView extends VerticalLayout {
    String selectedId;
    public CrashDetailsView() {
        setSizeFull();
        getStyle().set("overflow-y", "auto");

        Metrics metrics = (Metrics) VaadinSession.getCurrent().getAttribute("metrics");
         selectedId = (String) VaadinSession.getCurrent().getAttribute("selectedId");

        System.out.println(metrics);
        if (metrics != null) {
            displayCrashDetails(metrics);
        }
    }

    private void displayCrashDetails(Metrics metrics) {
        Button backButton = new Button("Back to Metrics");
        backButton.addClickListener(event -> {
            UI.getCurrent().navigate("display-fuzzing-metrics/" + selectedId);
        });
        add(new HorizontalLayout(new H2("Crash Details"), backButton) );
        metrics.getCrashes().values().forEach(crash -> {
            Div crashDiv = new Div();
            crashDiv.addClassName("crash-details");

            crashDiv.add(new Div(new Text("Count: " + crash.getCount())));
            crashDiv.add(new Div(new Text("Error Message: " + crash.getError_message())));
            crashDiv.add(new Div(new Text("Sample Input: " + crash.getSample_input())));

            add(crashDiv);
        });
    }
}
