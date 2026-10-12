param location string = resourceGroup().location
param appNamePrefix string = 'ecobite-${uniqueString(resourceGroup().id)}'

param publisherEmail string = 'mariia@example.com'
param publisherName string = 'Mariia'

// 1. Linux App Service Plan (SKU B1)
resource appServicePlan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: '${appNamePrefix}-asp'
  location: location
  kind: 'linux'
  sku: {
    name: 'B1'
    tier: 'Basic'
  }
  properties: {
    reserved: true
  }
}

// 2. Linux Web App (Python 3.11)
resource webApp 'Microsoft.Web/sites@2023-12-01' = {
  name: '${appNamePrefix}-app'
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      alwaysOn: true
      appCommandLine: 'python -m uvicorn app.main:app --host 0.0.0.0 --port 8000'
    }
  httpsOnly: true
  }
}

// 3. API Management Service (Developer tier)
resource apimService 'Microsoft.ApiManagement/service@2024-05-01' = {
  name: '${appNamePrefix}-apim'
  location: location
  sku: {
    name: 'Developer'
    capacity: 1
  }
  properties: {
    publisherEmail: publisherEmail
    publisherName: publisherName
  }
}

output webAppName string = webApp.name
output apimName string = apimService.name
output webAppHostName string = webApp.properties.defaultHostName