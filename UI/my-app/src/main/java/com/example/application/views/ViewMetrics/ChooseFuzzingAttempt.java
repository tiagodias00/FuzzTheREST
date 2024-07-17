package com.example.application.views.ViewMetrics;
import com.example.application.services.MongoDBService;
import com.example.application.views.MainLayout;
import com.vaadin.flow.component.combobox.ComboBox;
import com.vaadin.flow.component.dependency.CssImport;
import com.vaadin.flow.component.notification.Notification;
import com.vaadin.flow.component.orderedlayout.VerticalLayout;
import com.vaadin.flow.router.Route;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Set;


@Route(value="choose-Fuzzing-Attempt", layout = MainLayout.class)
@CssImport("./themes/fuzztherest/styles.css")
public class ChooseFuzzingAttempt extends VerticalLayout {
    Logger logger = LoggerFactory.getLogger(ChooseFuzzingAttempt.class);


    public ChooseFuzzingAttempt(MongoDBService mongoDBService) {
        try {
            ComboBox<String> idsComboBox = new ComboBox<>("Select Fuzzing Attempt");
            idsComboBox.addClassName("fuzzing-attempt-combobox");

            Set<String> ids = mongoDBService.fetchAllIds();
            idsComboBox.setItems(ids);
            idsComboBox.addValueChangeListener(event -> {
                String selectedId = event.getValue();
                getUI().ifPresent(ui -> ui.navigate("display-fuzzing-metrics/" + selectedId));
            });

            idsComboBox.setWidthFull(); // Make the ComboBox take the full width of the layout

            add(idsComboBox);
        } catch (Exception e) {
            logger.error("Error initializing ChooseFuzzingAttempt view", e);
            Notification.show("Failed to initialize the fuzzing attempts selection: " + e.getMessage(), 5000, Notification.Position.MIDDLE);
        }
    }
}