package com.example.application.views.login;

import com.example.application.views.MainLayout;
import com.vaadin.flow.component.Composite;
import com.vaadin.flow.component.dependency.Uses;
import com.vaadin.flow.component.icon.Icon;
import com.vaadin.flow.component.login.LoginForm;
import com.vaadin.flow.component.orderedlayout.VerticalLayout;
import com.vaadin.flow.router.PageTitle;
import com.vaadin.flow.router.Route;

@PageTitle("Login")
public class LoginView extends Composite<VerticalLayout> {

    public LoginView() {
        LoginForm loginForm = new LoginForm();
        getContent().setWidth("100%");
        getContent().getStyle().set("flex-grow", "1");
        getContent().add(loginForm);
    }
}
