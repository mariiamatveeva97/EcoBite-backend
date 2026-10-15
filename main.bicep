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

// 4. Log Analytics workspace (bestaat al; zelfde naam, dus Bicep neemt hem over)
resource logWorkspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: 'log-ecobite'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// 5. Diagnostic setting: App Service -> workspace
resource webAppDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: 'diag-to-law'
  scope: webApp
  properties: {
    workspaceId: logWorkspace.id
    logs: [
      {
        category: 'AppServiceHTTPLogs'
        enabled: true
      }
      {
        category: 'AppServiceConsoleLogs'
        enabled: true
      }
    ]
  }
}

// 6. Diagnostic setting: API Management gateway -> workspace
resource apimDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: 'diag-to-law'
  scope: apimService
  properties: {
    workspaceId: logWorkspace.id
    logAnalyticsDestinationType: 'Dedicated'
    logs: [
      {
        category: 'GatewayLogs'
        enabled: true
      }
    ]
  }
}

output webAppName string = webApp.name
output apimName string = apimService.name
output webAppHostName string = webApp.properties.defaultHostName