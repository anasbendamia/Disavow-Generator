import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import tailwindcss from "tailwindcss";

export default defineConfig(({ mode }) => ({
  base: mode === "production" ? "/ui/vue3/dist/" : "/",

  plugins: [vue()],

  css: {
    postcss: {
      plugins: [tailwindcss()],
    },
  },

  server: {
    cors: {
      origin: "http://localhost:44444",
      credentials: true,
    },
    allowedHosts: ["localhost"],
    hmr: {
      clientPort: 5173,
    },
  },

  build: {
    outDir: "ui/vue3/dist",
    manifest: true,
    minify: true,
    rollupOptions: {
      input: {
        global: "ui/vue3/static/css/global.css",
        __main__: "ui/vue3/static/js/MountPoints/__main__.ts",
      },
      output: {
        chunkFileNames: "disavow_[hash:16].js",
        entryFileNames: "disavow_[hash:16].js",
        assetFileNames: "disavow_[hash:16].[ext]",
      },
    },
  },
}));
