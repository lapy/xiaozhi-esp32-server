import { getEnvBaseUrl } from './index'
import { toast } from './toast'

/**
 * File upload hook function usage example
 * @example
 * const { loading, error, data, progress, run } = useUpload<IUploadResult>(
 *   uploadUrl,
 *   {},
 *   {
 *     maxSize: 5, // Maximum 5MB
 *     sourceType: ['album'], // Only support selection from album
 *     onProgress: (p) => console.log(`Upload progress: ${p}%`),
 *     onSuccess: (res) => console.log('Upload successful', res),
 *     onError: (err) => console.error('Upload failed', err),
 *   },
 * )
 */

/**
 * Upload file URL configuration
 */
export const uploadFileUrl = {
  /** User avatar upload address (dynamically read current effective BaseURL) */
  get USER_AVATAR() {
    return `${getEnvBaseUrl()}/user/avatar`
  },
}

/**
 * General file upload function (supports direct file path input)
 * @param url Upload address
 * @param filePath Local file path
 * @param formData Additional form data
 * @param options Upload options
 */
export function useFileUpload<T = string>(url: string, filePath: string, formData: Record<string, any> = {}, options: Omit<UploadOptions, 'sourceType' | 'sizeType' | 'count'> = {}) {
  return useUpload<T>(
    url,
    formData,
    {
      ...options,
      sourceType: ['album'],
      sizeType: ['original'],
    },
    filePath,
  )
}

export interface UploadOptions {
  /** Maximum selectable image count, default is 1 */
  count?: number
  /** Selected image size, original-original, compressed-compressed */
  sizeType?: Array<'original' | 'compressed'>
  /** Image source, album-album, camera-camera */
  sourceType?: Array<'album' | 'camera'>
  /** File size limit, unit: MB */
  maxSize?: number //
  /** Upload progress callback function */
  onProgress?: (progress: number) => void
  /** Upload success callback function */
  onSuccess?: (res: Record<string, any>) => void
  /** Upload failure callback function */
  onError?: (err: Error | UniApp.GeneralCallbackResult) => void
  /** Upload complete callback function (regardless of success or failure) */
  onComplete?: () => void
}

/**
 * File upload hook function
 * @template T Data type returned after successful upload
 * @param url Upload address
 * @param formData Additional form data
 * @param options Upload options
 * @returns Upload status and control object
 */
export function useUpload<T = string>(url: string, formData: Record<string, any> = {}, options: UploadOptions = {},
  /** Pass file path directly, skip selector */
  directFilePath?: string) {
  /** Uploading status */
  const loading = ref(false)
  /** Upload error status */
  const error = ref(false)
  /** Response data after successful upload */
  const data = ref<T>()
  /** Upload progress (0-100) */
  const progress = ref(0)

  /** Destructure upload options, set default values */
  const {
    /** Maximum selectable image count */
    count = 1,
    /** Selected image dimensions */
    sizeType = ['original', 'compressed'],
    /** Image selection source */
    sourceType = ['album', 'camera'],
    /** File size limit (MB) */
    maxSize = 10,
    /** Progress callback */
    onProgress,
    /** Success callback */
    onSuccess,
    /** Failure callback */
    onError,
    /** Complete callback */
    onComplete,
  } = options

  /**
   * Check if file size exceeds limit
   * @param size File size (bytes)
   * @returns Whether passes check
   */
  const checkFileSize = (size: number) => {
    const sizeInMB = size / 1024 / 1024
    if (sizeInMB > maxSize) {
      toast.warning(`File size cannot exceed ${maxSize}MB`)
      return false
    }
    return true
  }
  /**
   * Trigger file selection and upload
   * Use different selectors based on platform:
   * - WeChat Mini Program uses chooseMedia
   * - Other platforms use chooseImage
   */
  const run = () => {
    if (directFilePath) {
      // Directly use passed file path
      loading.value = true
      progress.value = 0
      uploadFile<T>({
        url,
        tempFilePath: directFilePath,
        formData,
        data,
        error,
        loading,
        progress,
        onProgress,
        onSuccess,
        onError,
        onComplete,
      })
      return
    }

    // #ifdef MP-WEIXIN
    // Use chooseMedia API in WeChat Mini Program environment
    uni.chooseMedia({
      count,
      mediaType: ['image'], // Only support image type
      sourceType,
      success: (res) => {
        const file = res.tempFiles[0]
        // Check if file size meets limit
        if (!checkFileSize(file.size))
          return

        // Start upload
        loading.value = true
        progress.value = 0
        uploadFile<T>({
          url,
          tempFilePath: file.tempFilePath,
          formData,
          data,
          error,
          loading,
          progress,
          onProgress,
          onSuccess,
          onError,
          onComplete,
        })
      },
      fail: (err) => {
        console.error('Failed to select media file:', err)
        error.value = true
        onError?.(err)
      },
    })
    // #endif

    // #ifndef MP-WEIXIN
    // Use chooseImage API in non-WeChat Mini Program environment
    uni.chooseImage({
      count,
      sizeType,
      sourceType,
      success: (res) => {
        console.log('Image selection successful:', res)

        // Start upload
        loading.value = true
        progress.value = 0
        uploadFile<T>({
          url,
          tempFilePath: res.tempFilePaths[0],
          formData,
          data,
          error,
          loading,
          progress,
          onProgress,
          onSuccess,
          onError,
          onComplete,
        })
      },
      fail: (err) => {
        console.error('Image selection failed:', err)
        error.value = true
        onError?.(err)
      },
    })
    // #endif
  }

  return { loading, error, data, progress, run }
}

/**
 * File upload options interface
 * @template T Data type returned after successful upload
 */
interface UploadFileOptions<T> {
  /** Upload URL */
  url: string
  /** Temporary file path */
  tempFilePath: string
  /** Additional form data */
  formData: Record<string, any>
  /** Response data after successful upload */
  data: Ref<T | undefined>
  /** Upload error status */
  error: Ref<boolean>
  /** Uploading status */
  loading: Ref<boolean>
  /** Upload progress (0-100) */
  progress: Ref<number>
  /** Upload progress callback */
  onProgress?: (progress: number) => void
  /** Upload success callback */
  onSuccess?: (res: Record<string, any>) => void
  /** Upload failure callback */
  onError?: (err: Error | UniApp.GeneralCallbackResult) => void
  /** Upload complete callback */
  onComplete?: () => void
}

/**
 * Execute file upload
 * @template T Data type returned after successful upload
 * @param options Upload options
 */
function uploadFile<T>({
  url,
  tempFilePath,
  formData,
  data,
  error,
  loading,
  progress,
  onProgress,
  onSuccess,
  onError,
  onComplete,
}: UploadFileOptions<T>) {
  try {
    // Create upload task
    const uploadTask = uni.uploadFile({
      url,
      filePath: tempFilePath,
      name: 'file', // Key corresponding to file
      formData,
      header: {
        // In H5 environment, no need to manually set Content-Type, let browser handle multipart format
        // #ifndef H5
        'Content-Type': 'multipart/form-data',
        // #endif
      },
      // Ensure file name is valid
      success: (uploadFileRes) => {
        console.log('File upload successful:', uploadFileRes)
        try {
          // Parse response data
          const { data: _data } = JSON.parse(uploadFileRes.data)
          // Upload successful
          data.value = _data as T
          onSuccess?.(_data)
        }
        catch (err) {
          // Response parsing error
          console.error('Failed to parse upload response:', err)
          error.value = true
          onError?.(new Error('Upload response parsing failed'))
        }
      },
      fail: (err) => {
        // Upload request failed
        console.error('File upload failed:', err)
        error.value = true
        onError?.(err)
      },
      complete: () => {
        // Execute regardless of success or failure
        loading.value = false
        onComplete?.()
      },
    })

    // Listen to upload progress
    uploadTask.onProgressUpdate((res) => {
      progress.value = res.progress
      onProgress?.(res.progress)
    })
  }
  catch (err) {
    // Create upload task failed
    console.error('Failed to create upload task:', err)
    error.value = true
    loading.value = false
    onError?.(new Error('Failed to create upload task'))
  }
}
