@description('Location for all resources.')
param location string = resourceGroup().location

@description('Name of the virtual machine.')
param vmName string

param storageAccountName string
@secure()
param storageAccountKey string
param storageAccountEndpoint string
param xmlCfg string

resource vm 'Microsoft.Compute/virtualMachines@2022-11-01' existing = {
  name: vmName
}

resource vmDiag 'Microsoft.Compute/virtualMachines/extensions@2023-09-01' = {
  parent: vm
  name: 'Microsoft.Insights.VMDiagnosticsSettings'
  location: location
  tags: {
    CreatedOnUTC: 'Unknown'
  }
  properties: {
    autoUpgradeMinorVersion: true
    publisher: 'Microsoft.Azure.Diagnostics'
    type: 'IaaSDiagnostics'
    typeHandlerVersion: '1.5'
    settings: {
      StorageAccount: storageAccountName
      xmlCfg: xmlCfg
    }
    protectedSettings: {
      storageAccountName: storageAccountName
      storageAccountKey: storageAccountKey
      storageAccountEndPoint: storageAccountEndpoint
    }
  }
}
