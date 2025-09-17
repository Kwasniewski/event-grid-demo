resource "azurerm_eventgrid_namespace" "namespace" {
  name                = var.namespace
  location            = var.region
  resource_group_name = var.resource_group_name

  topic_spaces_configuration {
    alternative_authentication_name_source = []
  }
}
