// # After executing `pnpm upgrade`, uniapp related dependencies will be upgraded
// # After upgrade, many useless dependencies will be automatically added, which need to be deleted to reduce package size
// # Just execute the following command

const { exec } = require('node:child_process')

// Define commands to execute
const dependencies = [
  '@dcloudio/uni-app-harmony',
  // TODO: If you don't need mini programs for certain platforms, please manually delete or comment out
  '@dcloudio/uni-mp-alipay',
  '@dcloudio/uni-mp-baidu',
  '@dcloudio/uni-mp-jd',
  '@dcloudio/uni-mp-kuaishou',
  '@dcloudio/uni-mp-lark',
  '@dcloudio/uni-mp-qq',
  '@dcloudio/uni-mp-toutiao',
  '@dcloudio/uni-mp-xhs',
  '@dcloudio/uni-quickapp-webview',
  // i18n template should comment out the following
  'vue-i18n',
]

// Use exec to execute commands
exec(`pnpm un ${dependencies.join(' ')}`, (error, stdout, stderr) => {
  if (error) {
    // If there is an error, print error information
    console.error(`Execution error: ${error}`)
    return
  }
  // Print normal output
  console.log(`stdout: ${stdout}`)
  // If there is error output, print it out too
  console.error(`stderr: ${stderr}`)
})
