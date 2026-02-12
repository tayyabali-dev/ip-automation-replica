/**
 * Configuration utility for different deployment environments
 * Supports development, production, and 4-server deployment scenarios
 */

export interface AppConfig {
  apiUrl: string;
  environment: string;
  isDevelopment: boolean;
  isProduction: boolean;
}

/**
 * Get the current application configuration
 */
export const getConfig = (): AppConfig => {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const apiUrl = `${baseUrl.replace(/\/+$/, '')}/api/v1`;
  const environment = process.env.NODE_ENV || 'development';
  
  return {
    apiUrl,
    environment,
    isDevelopment: environment === 'development',
    isProduction: environment === 'production',
  };
};

/**
 * Validate that required environment variables are set
 */
export const validateConfig = (): void => {
  const config = getConfig();
  
  if (!config.apiUrl) {
    throw new Error('NEXT_PUBLIC_API_URL environment variable is required');
  }
  
  // Validate URL format
  try {
    new URL(config.apiUrl);
  } catch (error) {
    throw new Error(`Invalid NEXT_PUBLIC_API_URL format: ${config.apiUrl}`);
  }
  
  console.log(`Frontend configured for ${config.environment} environment`);
  console.log(`API URL: ${config.apiUrl}`);
};

/**
 * Get deployment-specific configuration
 */
export const getDeploymentInfo = () => {
  const config = getConfig();
  
  return {
    ...config,
    isLocalhost: config.apiUrl.includes('localhost') || config.apiUrl.includes('127.0.0.1'),
    isRemoteServer: !config.apiUrl.includes('localhost') && !config.apiUrl.includes('127.0.0.1'),
    serverType: config.apiUrl.includes('localhost') ? 'local' : 'remote',
  };
};