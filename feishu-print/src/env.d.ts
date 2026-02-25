/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

// TinyMCE 全局类型声明
interface Window {
  tinymce: any;
}

// 允许导入 .js 文件
declare module '*.js' {
  const content: any;
  export default content;
}

declare module '../../plugins/tinymce-plugins.js' {
  const content: any;
  export default content;
}

// file-saver 模块类型声明
declare module 'file-saver' {
  export function saveAs(data: Blob | string, filename?: string, options?: any): void;
}
