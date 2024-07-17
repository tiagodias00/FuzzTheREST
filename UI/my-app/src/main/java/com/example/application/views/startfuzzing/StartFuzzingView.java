package com.example.application.views.startfuzzing;

import com.example.application.services.FtpService;
import com.example.application.services.SchemaDataService;
import com.example.application.views.MainLayout;
import com.vaadin.flow.component.Composite;
import com.vaadin.flow.component.button.Button;
import com.vaadin.flow.component.checkbox.Checkbox;
import com.vaadin.flow.component.combobox.ComboBox;
import com.vaadin.flow.component.dependency.CssImport;
import com.vaadin.flow.component.dependency.Uses;
import com.vaadin.flow.component.grid.Grid;
import com.vaadin.flow.component.icon.Icon;
import com.vaadin.flow.component.listbox.ListBox;
import com.vaadin.flow.component.orderedlayout.FlexComponent;
import com.vaadin.flow.component.orderedlayout.HorizontalLayout;
import com.vaadin.flow.component.orderedlayout.VerticalLayout;
import com.vaadin.flow.data.provider.hierarchy.TreeData;
import com.vaadin.flow.data.provider.hierarchy.TreeDataProvider;
import com.vaadin.flow.data.renderer.ComponentRenderer;
import com.vaadin.flow.router.PageTitle;
import com.vaadin.flow.router.Route;
import com.vaadin.flow.component.notification.Notification;
import com.vaadin.flow.component.upload.Upload;
import com.vaadin.flow.component.upload.receivers.MemoryBuffer;
import com.vaadin.flow.component.treegrid.TreeGrid;


import com.vaadin.flow.router.RouteAlias;
import com.vaadin.flow.server.VaadinSession;
import io.swagger.v3.parser.OpenAPIV3Parser;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.media.Schema;
import org.springframework.beans.factory.annotation.Autowired;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import java.io.InputStream;
import java.util.stream.Collectors;

import static java.lang.Thread.sleep;


@PageTitle("StartFuzzing")
@Route(value = "", layout = MainLayout.class)
@RouteAlias(value = "", layout = MainLayout.class)
@Uses(Icon.class)
@CssImport("./themes/fuzztherest/styles.css")
public class StartFuzzingView extends Composite<VerticalLayout> {

    private  SchemaDataService schemaService;
    private String filePath;
    private TreeGrid<SchemaNode> schemaGrid;
    private TreeData<SchemaNode> treeData;
    private Button navigateButton;
    private FtpService ftpService;
    Map<String, List<String>> operations;
    private List<String> availableOperations = new ArrayList<>();
    private List<String> selectedOperations = new ArrayList<>();

    private ListBox<String> sourceList = new ListBox<>();

    private ListBox<String> targetList = new ListBox<>();

    private List<List<String>> scenarios = new ArrayList<>();
    private Grid<List<String>> sequencesGrid= new Grid<>();

    @Autowired
    public StartFuzzingView(SchemaDataService schemaService) {
        this.schemaService = schemaService;
        ftpService = new FtpService();
        sourceList.addClassName("scrollable-listbox");
        targetList.addClassName("scrollable-listbox");
        initUI();
        sequencesGrid.addColumn(sequence -> String.join(", ", sequence)).setHeader("Sequences");
    }

    private void initUI() {
        MemoryBuffer buffer = new MemoryBuffer();
        Upload upload = new Upload(buffer);
        upload.setAcceptedFileTypes(".yaml", ".json");

        ComboBox<String> algorithmComboBox = new ComboBox<>("Select Algorithm");
        algorithmComboBox.setItems("Qlearning");
        algorithmComboBox.setPlaceholder("Choose an algorithm");
        algorithmComboBox.setEnabled(false);



        navigateButton = new Button("Go to algorithm page");
        navigateButton.setVisible(false);
        navigateButton.addClickListener(event -> {
            String selectedAlgorithm = algorithmComboBox.getValue();
            if (selectedAlgorithm != null && filePath != null) {
                List<SchemaDataService.SchemaIdentifierPair> schemaIdentifierPairs = findAllSelectedIdentifiers();
                if (!schemaIdentifierPairs.isEmpty()) {
                    schemaService.setSchemaIdentifierPairs(schemaIdentifierPairs);
                    navigateToAlgorithmPage(selectedAlgorithm, filePath);
                } else {
                    Notification.show("Please select at least one identifier for a schema");
                }

            } else {
                Notification.show("Please upload a file and select an algorithm");
            }
        });


        upload.addFailedListener(event -> {
            Notification.show("Upload failed");
        });
        this.schemaGrid = createSchemaGrid();
        upload.addSucceededListener(event -> {
            InputStream fileData = buffer.getInputStream();
            String fileName = event.getFileName();
            filePath= ftpService.uploadFileToFtp(fileName, fileData);
            algorithmComboBox.setEnabled(true);
            operations=parseOpenAPI(buffer.getInputStream());
            System.out.println(operations);
            updateUIAfterUpload(operations);
            initializeListInteractions();


        });

        algorithmComboBox.addValueChangeListener(event -> {
            boolean hasSelection = event.getValue() != null;
            navigateButton.setVisible(hasSelection);
        });

        getContent().add(upload, algorithmComboBox, navigateButton, schemaGrid);
    }

    private void navigateToAlgorithmPage(String selectedAlgorithm, String filePath) {
        VaadinSession.getCurrent().setAttribute("sequencesData", scenarios);
        String route = String.format("%s?algorithm=%s&filePath=%s", selectedAlgorithm, selectedAlgorithm, filePath);
        getUI().ifPresent(ui -> ui.navigate(route));
    }

    private Map<String, List<String>> extractOperationIds(OpenAPI openAPI) {
        Map<String, List<String>> operations = new HashMap<>();
        openAPI.getPaths().forEach((path, pathItem) -> {
            List<String> operationIds = new ArrayList<>();
            if (pathItem.getGet() != null && pathItem.getGet().getOperationId() != null) {
                operationIds.add(pathItem.getGet().getOperationId());
            }
            if (pathItem.getPost() != null && pathItem.getPost().getOperationId() != null) {
                operationIds.add(pathItem.getPost().getOperationId());
            }
            if (pathItem.getPut() != null && pathItem.getPut().getOperationId() != null) {
                operationIds.add(pathItem.getPut().getOperationId());
            }
            if (pathItem.getDelete() != null && pathItem.getDelete().getOperationId() != null) {
                operationIds.add(pathItem.getDelete().getOperationId());
            }
            if (pathItem.getPatch() != null && pathItem.getPatch().getOperationId() != null) {
                operationIds.add(pathItem.getPatch().getOperationId());
            }
            operations.put(path, operationIds);
        });
        return operations;
    }
    private void updateUIAfterUpload(Map<String, List<String>> operations) {

        availableOperations.addAll(operations.values().stream().flatMap(List::stream).collect(Collectors.toList()));
        sourceList.setItems(availableOperations);
    }
    private void initializeListInteractions() {
        Button toTargetButton = new Button("Add >>", event -> {
            String selectedItem = sourceList.getValue();
            if (selectedItem != null && !selectedOperations.contains(selectedItem)) {
                selectedOperations.add(selectedItem);
                targetList.setItems(selectedOperations);
            }
        });

        Button toSourceButton = new Button("<< Remove", event -> {
            String selectedItem = targetList.getValue();
            if (selectedItem != null) {
                selectedOperations.remove(selectedItem);
                targetList.setItems(selectedOperations);
            }
        });

        Button saveSequenceButton = new Button("Save Sequence", event -> {
            if (!selectedOperations.isEmpty()) {
                saveSequence(new ArrayList<>(selectedOperations));
                updateSequencesDisplay();
                selectedOperations.clear();
                targetList.setItems(selectedOperations);
            } else {
                Notification.show("No operations selected for the sequence", 3000, Notification.Position.MIDDLE);
            }
        });



        VerticalLayout buttonsLayout = new VerticalLayout(toTargetButton, toSourceButton, saveSequenceButton);
        buttonsLayout.setAlignItems(FlexComponent.Alignment.CENTER);
        buttonsLayout.setSpacing(true); // Add spacing between buttons
        buttonsLayout.setWidth("auto"); // Adjust width based on content
        buttonsLayout.setFlexGrow(1, toTargetButton, toSourceButton, saveSequenceButton); // Distribute remaining space evenly


        sourceList.setHeight("400px");
        sourceList.setWidth("600px");
        targetList.setHeight("400px");
        targetList.setWidth("600 px");

        HorizontalLayout interactionLayout = new HorizontalLayout(sourceList, buttonsLayout, targetList);
        interactionLayout.setAlignItems(FlexComponent.Alignment.CENTER); // Align components center vertically
        interactionLayout.setWidthFull(); // Set layout to fill horizontal space
        getContent().add(interactionLayout, sequencesGrid);
    }


    private void updateSequencesDisplay() {
        sequencesGrid.setItems(scenarios);
    }


    private void saveSequence(List<String> sequence) {
        scenarios.add(sequence);
    }

    private Map<String, List<String>>  parseOpenAPI(InputStream inputStream) {
        String openApiContent = new BufferedReader(new InputStreamReader(inputStream))
                .lines().collect(Collectors.joining("\n"));

        OpenAPI openAPI = new OpenAPIV3Parser().readContents(openApiContent).getOpenAPI();
        Map<String, Schema> schemas = openAPI.getComponents().getSchemas();

        if (schemas != null) {
            updateSchemaGrid(schemaGrid, schemas);
        }

        return extractOperationIds(openAPI);

    }


    private TreeGrid<SchemaNode> createSchemaGrid() {
        TreeGrid<SchemaNode> grid = new TreeGrid<>();
        grid.addHierarchyColumn(SchemaNode::getName).setHeader("Component Schemas");

        grid.addColumn(new ComponentRenderer<>(item -> {
            if (item.hasChildren()) {
                return null;  // No checkbox for nodes with children
            }
            Checkbox checkbox = new Checkbox();
            checkbox.setValue(item.isIdentifier());
            checkbox.addValueChangeListener(event -> {
                item.setIdentifier(event.getValue());
                grid.getDataProvider().refreshAll();
                if (event.getValue()) {
                    try {
                        sleep(300);
                    } catch (InterruptedException e) {
                        throw new RuntimeException(e);
                    }
                    grid.collapse(item.getParent());  // Collapse the parent node
                }
            });
            return checkbox;
        })).setHeader("Identifier");

        return grid;
    }


    private void updateSchemaGrid(TreeGrid<SchemaNode> grid, Map<String, Schema> schemas) {
        List<SchemaNode> rootNodes = new ArrayList<>();
        schemas.forEach((name, schema) -> {
            SchemaNode rootNode = new SchemaNode(name);
            schema.getProperties().forEach((propName, propDetails) -> {
                SchemaNode childNode = new SchemaNode(propName.toString());
                childNode.setParent(rootNode);  // Set parent
                rootNode.addChild(childNode);
            });
            rootNodes.add(rootNode);
        });

        treeData = new TreeData<>();
        treeData.addItems(rootNodes, SchemaNode::getChildren);
        TreeDataProvider<SchemaNode> dataProvider = new TreeDataProvider<>(treeData);
        grid.setDataProvider(dataProvider);
    }


    public class SchemaNode {
        private String name;
        private boolean isIdentifier;
        private List<SchemaNode> children = new ArrayList<>();
        private SchemaNode parent;  // Reference to the parent node
        private SchemaNode selectedChild;  // Track the selected child

        public SchemaNode(String name) {
            this.name = name;
        }

        public void addChild(SchemaNode child) {
            children.add(child);
            child.setParent(this);  // Set the parent inside the addChild method
        }

        public String getName() {
            return name;
        }

        public List<SchemaNode> getChildren() {
            return children;
        }

        public boolean isIdentifier() {
            return isIdentifier;
        }

        public void setIdentifier(boolean identifier) {
            this.isIdentifier = identifier;
            if (!hasChildren()) {  // Only allow setting identifier for leaf nodes
                if (identifier && parent != null) {
                    parent.setSelectedChild(this);
                }
            }
        }

        public boolean hasChildren() {
            return !children.isEmpty();
        }

        public SchemaNode getParent() {
            return parent;
        }

        public void setParent(SchemaNode parent) {
            this.parent = parent;
        }

        public void setSelectedChild(SchemaNode child) {
            if (selectedChild != null && selectedChild != child) {
                selectedChild.setIdentifier(false);
            }
            selectedChild = child;
        }

    }

    private List<SchemaDataService.SchemaIdentifierPair> findAllSelectedIdentifiers() {
        List<SchemaDataService.SchemaIdentifierPair> pairs = new ArrayList<>();
        for (SchemaNode rootNode : treeData.getRootItems()) {
            findSelectedChildrenRecursive(rootNode, pairs);
        }
        return pairs;
    }

    private void findSelectedChildrenRecursive(SchemaNode node, List<SchemaDataService.SchemaIdentifierPair> pairs) {
        if (node.isIdentifier()) {
            pairs.add(new SchemaDataService.SchemaIdentifierPair(node.getParent().getName(), node.getName()));
        }
        for (SchemaNode child : node.getChildren()) {
            findSelectedChildrenRecursive(child, pairs);
        }
    }

}
