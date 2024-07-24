package com.example.application.views.Algorithms;

import com.example.application.Configuration.ApiConfig;
import com.example.application.services.SchemaDataService;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.vaadin.flow.component.Composite;
import com.vaadin.flow.component.UI;
import com.vaadin.flow.component.button.Button;
import com.vaadin.flow.component.formlayout.FormLayout;
import com.vaadin.flow.component.notification.Notification;
import com.vaadin.flow.component.orderedlayout.VerticalLayout;
import com.vaadin.flow.component.textfield.IntegerField;
import com.vaadin.flow.component.textfield.NumberField;
import com.vaadin.flow.router.BeforeEvent;
import com.vaadin.flow.router.HasUrlParameter;
import com.vaadin.flow.router.OptionalParameter;
import com.vaadin.flow.router.PageTitle;
import com.vaadin.flow.router.Route;
import com.vaadin.flow.server.VaadinSession;
import io.github.cdimascio.dotenv.Dotenv;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.*;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static com.example.application.services.SchemaDataService.SchemaIdentifierPair.convertToJson;

@PageTitle("Qlearning")
@Route(value = "Qlearning")
public class Qlearning extends Composite<VerticalLayout> implements HasUrlParameter<String> {

    private final RestTemplate restTemplate;
    private final SchemaDataService schemaDataService;
    private String algorithm;
    private String filePath;

    private IntegerField maxStepsPerEpisodeField;
    private NumberField explorationRateField;
    private IntegerField numEpisodesField;

    private String apiUrl;
    private String ids;
    private String sequencesJson;

    private Button backButton = new Button("Go Back");


    @Autowired
    public Qlearning(RestTemplate restTemplate, SchemaDataService schemaDataService) {
        this.restTemplate = restTemplate;
        this.schemaDataService = schemaDataService;
        Dotenv dotenv = Dotenv.load();
        apiUrl = dotenv.get("API.QLEARNING.URL");


    }


    @Override
    public void setParameter(BeforeEvent event, @OptionalParameter String parameter) {
        algorithm = event.getLocation().getQueryParameters().getParameters().getOrDefault("algorithm", List.of("")).get(0);
        filePath = event.getLocation().getQueryParameters().getParameters().getOrDefault("filePath", List.of("")).get(0);
        List<SchemaDataService.SchemaIdentifierPair> schemaPairs = schemaDataService.getSchemaIdentifierPairs();
        ids= convertToJson(schemaPairs);
        List<List<String>> sequences = (List<List<String>>) VaadinSession.getCurrent().getAttribute("sequencesData");
        ObjectMapper mapper = new ObjectMapper();

        try {
            sequencesJson = mapper.writeValueAsString(sequences);
        } catch (JsonProcessingException e) {
            throw new RuntimeException(e);
        }
        createForm();
    }

    private void createForm() {
        FormLayout formLayout = new FormLayout();
        backButton.addClickListener(event -> UI.getCurrent().getPage().executeJs("history.back()"));

        maxStepsPerEpisodeField = new IntegerField("Max Steps Per Episode");
        explorationRateField = new NumberField("Exploration Rate");
        explorationRateField.setStep(0.01);
        explorationRateField.setMin(0);
        explorationRateField.setMax(1);
        numEpisodesField = new IntegerField("Number of Episodes");

        maxStepsPerEpisodeField.setRequiredIndicatorVisible(true);
        explorationRateField.setRequiredIndicatorVisible(true);
        numEpisodesField.setRequiredIndicatorVisible(true);

        Button submitButton = new Button("Start Qlearning", event -> sendApiCall());

        formLayout.add(maxStepsPerEpisodeField, explorationRateField, numEpisodesField, submitButton);

        getContent().add(formLayout);
        getContent().add(backButton);
    }

    private void sendApiCall() {
        if (maxStepsPerEpisodeField.isEmpty() || explorationRateField.isEmpty() || numEpisodesField.isEmpty()) {
            Notification.show("Please fill in all fields");
            return;
        }

        int maxStepsPerEpisode = maxStepsPerEpisodeField.getValue();

        double explorationRate = explorationRateField.getValue();
        if (explorationRate < 0 || explorationRate > 1) {
            Notification.show("Exploration Rate must be between 0 and 1");
            return;
        }
        int numEpisodes = numEpisodesField.getValue();

        if (maxStepsPerEpisodeField.isEmpty() || explorationRateField.isEmpty() || numEpisodesField.isEmpty()) {
            Notification.show("Please fill in all fields");
            return;
        }

        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("file_path", filePath);
        requestBody.put("algorithm_type", algorithm);
        requestBody.put("ids", ids);
        requestBody.put("scenarios", sequencesJson);
        requestBody.put("max_steps_per_episode", maxStepsPerEpisode);
        requestBody.put("exploration_rate", explorationRate);
        requestBody.put("num_episodes", numEpisodes);


        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestBody, headers);


        try {
            ResponseEntity<String> response = restTemplate.exchange(apiUrl, HttpMethod.POST, entity, String.class);
        } catch (Exception e) {
            System.out.println("API call failed: " + e.getMessage());
        }
    }


}
