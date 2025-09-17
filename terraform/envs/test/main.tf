terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=4.44.0"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

module "event_grid" {
  source              = "../../modules/event-grid"
  namespace           = var.namespace
  region              = var.region
  resource_group_name = var.resource_group_name
}
