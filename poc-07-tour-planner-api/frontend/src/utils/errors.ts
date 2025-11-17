/**
 * Unified error handling utilities
 */

import { ApiError } from '@/types';
import { logger } from './logger';

export class ApiException extends Error {
  constructor(
    public status: number,
    public detail: string,
    public originalError?: any
  ) {
    super(detail);
    this.name = 'ApiException';
  }
}

export class NetworkException extends Error {
  constructor(message: string, public originalError?: any) {
    super(message);
    this.name = 'NetworkException';
  }
}

export class StreamException extends Error {
  constructor(message: string, public originalError?: any) {
    super(message);
    this.name = 'StreamException';
  }
}

/**
 * Handle API errors and convert to user-friendly messages
 */
export function handleApiError(error: any): string {
  logger.error('API error occurred', error);

  if (error instanceof ApiException) {
    return error.detail || 'An API error occurred';
  }

  if (error instanceof NetworkException) {
    return 'Network connection failed. Please check your internet connection.';
  }

  if (error instanceof StreamException) {
    return 'Streaming connection failed. Please try again.';
  }

  if (error.message) {
    return error.message;
  }

  return 'An unexpected error occurred. Please try again.';
}

/**
 * Parse API error response
 */
export async function parseApiError(response: Response): Promise<ApiException> {
  try {
    const data: ApiError = await response.json();
    return new ApiException(response.status, data.detail || response.statusText);
  } catch {
    return new ApiException(response.status, response.statusText);
  }
}

/**
 * Retry logic for failed operations
 */
export async function retryOperation<T>(
  operation: () => Promise<T>,
  maxRetries: number = 3,
  delayMs: number = 1000
): Promise<T> {
  let lastError: any;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await operation();
    } catch (error) {
      lastError = error;
      logger.warn(`Operation failed (attempt ${attempt}/${maxRetries})`, error);

      if (attempt < maxRetries) {
        await new Promise(resolve => setTimeout(resolve, delayMs * attempt));
      }
    }
  }

  throw lastError;
}
