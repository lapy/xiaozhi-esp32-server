# RAGFlow File API Reference

## Scope

This document covers the logical file-management endpoints exposed under
`/api/v1/file`.

## Endpoints

### `upload`

- Method: `POST`
- Path: `/api/v1/file/upload`
- Content type: `multipart/form-data`
- Purpose: Upload one or more files to a logical folder.

Common fields:

- `file`
- `parent_id`

### `create`

- Method: `POST`
- Path: `/api/v1/file/create`
- Purpose: Create a logical folder.

Common fields:

- `name`
- `parent_id`
- `type`

### `list_files`

- Method: `GET`
- Path: `/api/v1/file/list`
- Purpose: List files and folders under a parent folder.

Common query fields:

- `parent_id`
- `keywords`
- `page`
- `page_size`
- `orderby`
- `desc`

### `get`

- Method: `GET`
- Path: `/api/v1/file/get/<file_id>`
- Purpose: Return a file stream for direct download.

### `download_attachment`

- Method: `GET`
- Path: `/api/v1/file/download/<attachment_id>`
- Purpose: Download a stored attachment by storage key or attachment id.

### `rename`

- Method: `POST`
- Path: `/api/v1/file/rename`
- Purpose: Rename a file or folder.

### `move`

- Method: `POST`
- Path: `/api/v1/file/mv`
- Purpose: Move files or folders to another parent folder.

### `rm`

- Method: `DELETE`
- Path: `/api/v1/file/rm`
- Purpose: Delete files or folders.

### `get_root_folder`

- Method: `GET`
- Path: `/api/v1/file/root_folder`
- Purpose: Return the root logical folder.

### `get_parent_folder`

- Method: `GET`
- Path: `/api/v1/file/parent_folder`
- Purpose: Return a folder's direct parent.

### `get_all_parent_folders`

- Method: `GET`
- Path: `/api/v1/file/all_parent_folder`
- Purpose: Return the ancestor chain for breadcrumb navigation.

### `convert`

- Method: `POST`
- Path: `/api/v1/file/convert`
- Purpose: Convert uploaded files into dataset documents.

## Typical Returned Fields

- `id`
- `parent_id`
- `name`
- `location`
- `type`
- `size`
- `source_type`
- `create_time`
- `update_time`

## Notes

- The file APIs are storage-oriented and separate from dataset parsing.
- Folder operations are logical and may map to object storage behind the scenes.
