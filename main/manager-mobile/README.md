## Xiaozhi Control Panel Mobile Version (manager-mobile)
Cross-platform mobile management client based on uni-app v3 + Vue 3 + Vite, supporting App (Android & iOS) and WeChat Mini Program.

### Platform Compatibility

| H5 | iOS | Android | WeChat Mini Program |
| -- | --- | ------- | ---------- | 
| √  | √   | √       | √          | 

Note: Different UI components have slight differences in adaptation across platforms, please refer to the corresponding component library documentation.

### Development Environment Requirements
- Node >= 18
- pnpm >= 7.30 (recommended to use `pnpm@10.x` declared in the project)
- Optional: HBuilderX (App debugging/packaging), WeChat Developer Tools (WeChat Mini Program)

### Quick Start
1) Configure environment variables
   - Copy `env/.env.example` to `env/.env.development`
   - Modify configuration items according to actual situation (especially `VITE_SERVER_BASEURL`, `VITE_UNI_APPID`, `VITE_WX_APPID`)

2) Install dependencies

```bash
pnpm i
```

3) Local development (hot reload)
- h5: `pnpm dev:h5`, then observe the ip port number displayed in the startup log
- WeChat Mini Program: `pnpm dev:mp` or `pnpm dev:mp-weixin`, then import `dist/dev/mp-weixin` with WeChat Developer Tools
- App: Import `manager-mobile` with HBuilderX, then follow the tutorial below to run

### Environment Variables and Configuration
The project uses a custom `env` directory to store environment files, named according to Vite specifications: `.env.development`, `.env.production`, etc.

Key variables (partial):
- VITE_APP_TITLE: Application name (written to `manifest.config.ts`)
- VITE_UNI_APPID: uni-app application appid (App)
- VITE_WX_APPID: WeChat Mini Program appid (mp-weixin)
- VITE_FALLBACK_LOCALE: Default language, such as `zh-Hans`
- VITE_SERVER_BASEURL: Server base address (HTTP request baseURL)
- VITE_DELETE_CONSOLE: Whether to remove console during build (`true`/`false`)
- VITE_SHOW_SOURCEMAP: Whether to generate sourcemap (default off)
- VITE_LOGIN_URL: Login page path for unauthenticated redirect (used by route interceptor)

Example (`env/.env.development`):
```env
VITE_APP_TITLE=Xiaozhi
VITE_FALLBACK_LOCALE=zh-Hans
VITE_UNI_APPID=
VITE_WX_APPID=

VITE_SERVER_BASEURL=http://localhost:8080

VITE_DELETE_CONSOLE=false
VITE_SHOW_SOURCEMAP=false
VITE_LOGIN_URL=/pages/login/index
```

Note:
- `manifest.config.ts` will read title, appid, language and other configurations from `env`.

### Important Notes
⚠️ **Configuration items that must be modified before deployment:**

1. **Application ID Configuration**
   - `VITE_UNI_APPID`: Need to create an application in [DCloud Developer Center](https://dev.dcloud.net.cn/) and get AppID
   - `VITE_WX_APPID`: Need to register a mini program in [WeChat Public Platform](https://mp.weixin.qq.com/) and get AppID

2. **Server Address**
   - `VITE_SERVER_BASEURL`: Modify to your actual server address

3. **Application Information**
   - `VITE_APP_TITLE`: Modify to your application name
   - Update icon resources such as `src/static/logo.png`

4. **Other Configuration**
   - Check application configuration information in `manifest.config.ts`
   - Modify tabbar configuration in `src/layouts/fg-tabbar/tabbarList.ts` as needed

### Detailed Operation Guide

#### 1. Get uni-app AppID
![Generate AppID](../../docs/images/manager-mobile/generate_appid.png)
- Copy the generated AppID to environment variable `VITE_UNI_APPID`

#### 2. Local Running Steps
![Local Running](../../docs/images/manager-mobile/local_running.png)

**App Local Debugging:**
1. Import `manager-mobile` directory with HBuilderX
2. Re-identify the project
3. Connect phone or use simulator for real device debugging

**Project Recognition Issue Resolution:**
![Re-identify Project](../../docs/images/manager-mobile/reidentify_project.png)

If HBuilderX cannot correctly identify the project type:
- Right-click in the project root directory and select "Re-identify Project Type"
- Ensure the project is identified as a "uni-app" project

### Routing and Authentication
- Route interceptor plugin `routeInterceptor` is registered in `src/main.ts`.
- Blacklist interception: Only validates pages configured to require login (from `getNeedLoginPages` in `@/utils`).
- Login determination: Based on user information (`useUserStore` from `pinia`), unauthenticated users will be redirected to `VITE_LOGIN_URL` with parameters to redirect back to the original page.

### Network Requests
- Based on `alova` + `@alova/adapter-uniapp`, unified instance creation in `src/http/request/alova.ts`.
- `baseURL` reads environment configuration (`getEnvBaseUrl`), can dynamically switch domains through `method.config.meta.domain`.
- Authentication: Default injection of `Authorization` header from local `token` (`uni.getStorageSync('token')`), redirect to login if missing.
- Response: Unified handling of HTTP errors with `statusCode !== 200` and business errors with `code !== 0`; `401` will clear token and redirect to login.

### Build and Release

**WeChat Mini Program:**
1. Ensure correct `VITE_WX_APPID` is configured
2. Run `pnpm build:mp`, output in `dist/build/mp-weixin`
3. Import project directory with WeChat Developer Tools and upload code
4. Submit for review in WeChat Public Platform

**Android & iOS App:**

#### 3. App Packaging and Release Steps

**Step 1: Prepare Packaging**
![Packaging Release Step 1](../../docs/images/manager-mobile/packaging_release_step1.png)

1. Ensure correct `VITE_UNI_APPID` is configured
2. Run `pnpm build:app`, output in `dist/build/app`
3. Import project directory with HBuilderX
4. Click "Release" → "Native App-Cloud Packaging" in HBuilderX

**Step 2: Configure Packaging Parameters**
![Packaging Release Step 2](../../docs/images/manager-mobile/packaging_release_step2.png)

1. **App Icon and Launch Screen**: Upload app icon and launch screen images
2. **App Version Number**: Set version number and version name
3. **Signature Certificate**:
   - Android: Upload keystore certificate file
   - iOS: Configure developer certificate and provisioning profile
4. **Package Name Configuration**: Set app package name (Bundle ID)
5. **Packaging Type**: Choose test package or release package
6. Click "Package" to start cloud packaging process

**Release to App Stores:**
- **Android**: Upload generated APK file to major Android app markets
- **iOS**: Upload generated IPA file to App Store through App Store Connect (requires Apple Developer account)

### Conventions and Engineering
- Pages and sub-packages: Generated by `@uni-helper/vite-plugin-uni-pages` and `pages.config.ts`; tabbar configuration in `src/layouts/fg-tabbar/tabbarList.ts`.
- Component and hooks auto-import: See `unplugin-auto-import` and `@uni-helper/vite-plugin-uni-components` in `vite.config.ts`.
- Styling: Uses UnoCSS and `src/style/index.scss`.
- State management: `pinia` + `pinia-plugin-persistedstate`.
- Code standards: Built-in `eslint`, `husky`, `lint-staged`, auto-format before commit (`lint-staged`).

### Common Scripts
```bash
# Development
pnpm dev:mp        # Equivalent to dev:mp-weixin

# Build
pnpm build:mp      # Equivalent to build:mp-weixin

# Others
pnpm type-check
pnpm lint && pnpm lint:fix
```

### License
MIT
