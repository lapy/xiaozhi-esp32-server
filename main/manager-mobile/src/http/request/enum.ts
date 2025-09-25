export enum ResultEnum {
  Success = 0, // Success
  Error = 400, // Error
  Unauthorized = 401, // Unauthorized
  Forbidden = 403, // Forbidden access (originally forbidden)
  NotFound = 404, // Not found (originally notFound)
  MethodNotAllowed = 405, // Method not allowed (originally methodNotAllowed)
  RequestTimeout = 408, // Request timeout (originally requestTimeout)
  InternalServerError = 500, // Server error (originally internalServerError)
  NotImplemented = 501, // Not implemented (originally notImplemented)
  BadGateway = 502, // Gateway error (originally badGateway)
  ServiceUnavailable = 503, // Service unavailable (originally serviceUnavailable)
  GatewayTimeout = 504, // Gateway timeout (originally gatewayTimeout)
  HttpVersionNotSupported = 505, // HTTP version not supported (originally httpVersionNotSupported)
}
export enum ContentTypeEnum {
  JSON = 'application/json;charset=UTF-8',
  FORM_URLENCODED = 'application/x-www-form-urlencoded;charset=UTF-8',
  FORM_DATA = 'multipart/form-data;charset=UTF-8',
}
/**
 * Generate corresponding error message based on status code
 * @param {number|string} status Status code
 * @returns {string} Error message
 */
export function ShowMessage(status: number | string): string {
  let message: string
  switch (status) {
    case 400:
      message = 'Request error (400)'
      break
    case 401:
      message = 'Unauthorized, please login again (401)'
      break
    case 403:
      message = 'Access denied (403)'
      break
    case 404:
      message = 'Request error (404)'
      break
    case 408:
      message = 'Request timeout (408)'
      break
    case 500:
      message = 'Server error (500)'
      break
    case 501:
      message = 'Service not implemented (501)'
      break
    case 502:
      message = 'Network error (502)'
      break
    case 503:
      message = 'Service unavailable (503)'
      break
    case 504:
      message = 'Network timeout (504)'
      break
    case 505:
      message = 'HTTP version not supported (505)'
      break
    default:
      message = `Connection error (${status})!`
  }
  return `${message}, please check network or contact administrator!`
}
