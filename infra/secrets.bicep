param keyVaultName string

param clientAppSecretName string

@secure()
param clientAppSecret string


param serverAppSecretName string

@secure()
param serverAppSecret string

param vmPasswordSecretName string

@secure()
param vmPassword string

module clientAppSecretKV 'core/security/keyvault-secret.bicep' = if (!empty(clientAppSecret)) {
  name: 'clientsecret'
  params: {
    keyVaultName: keyVaultName
    name: clientAppSecretName
    secretValue: clientAppSecret
  }
}

module serverAppSecretKV 'core/security/keyvault-secret.bicep' = if (!empty(serverAppSecret)) {
  name: 'serversecret'
  params: {
    keyVaultName: keyVaultName
    name: serverAppSecretName
    secretValue: serverAppSecret
  }
}


module vmPasswordSecret 'core/security/keyvault-secret.bicep' = if (!empty(vmPassword)) {
  name: 'vmpassword'
  params: {
    keyVaultName: keyVaultName
    name: vmPasswordSecretName
    secretValue: vmPassword
  }
}
