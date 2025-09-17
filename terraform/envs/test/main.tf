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

import {
  to = module.event_grid.azurerm_eventgrid_namespace.namespace
  id = "/subscriptions/e88fa6f2-4a57-4402-8c6f-861bf76a1cd3/resourceGroups/MC_production-tb_production-tb_eastus/providers/Microsoft.EventGrid/namespaces/kwasniewski-event-grid-test"
}
