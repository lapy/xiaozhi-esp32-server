# Tabbar Description

`tabbar` is divided into `4 types` of situations:

- 0 `No tabbar`, only one page entry, no `tabbar` display at bottom; commonly used for temporary activity pages.
- 1 `Native tabbar`, uses `switchTab` to switch tabbar, `tabbar` pages have cache.
  - Advantages: Native built-in tabbar, renders first, has cache.
  - Disadvantages: Can only use 2 sets of images to switch selected and unselected states, changing colors requires replacing images (or using iconfont).
- 2 `Cached custom tabbar`, uses `switchTab` to switch tabbar, `tabbar` pages have cache. Uses third-party UI library `tabbar` component and hides native `tabbar` display.
  - Advantages: Can freely configure desired `svg icon`, easy to switch font colors. Has cache. Can implement various fancy animations etc.
  - Disadvantages: First click on tabbar will flicker.
- 3 `No-cache custom tabbar`, uses `navigateTo` to switch `tabbar`, `tabbar` pages have no cache. Uses third-party UI library `tabbar` component.
  - Advantages: Can freely configure desired svg icons, easy to switch font colors. Can implement various fancy animations etc.
  - Disadvantages: First click on `tabbar` will flicker, no cache.


> Note: Fancy effects need to be implemented by yourself, this template does not provide them.
