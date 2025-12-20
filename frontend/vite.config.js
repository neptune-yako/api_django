import { fileURLToPath, URL } from 'node:url'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
    // 加载环境变量
    const env = loadEnv(mode, process.cwd(), "")

    return {
        plugins: [
            vue(),
        ],
        build: {
            chunkSizeWarningLimit: 1500,
            rollupOptions: {
                output: {
                    manualChunks: {
                        vue: ['vue', 'vue-router', 'pinia'],
                    }
                }
            }
        },
        css: {
            preprocessorOptions: {
                scss: {
                    api: 'modern-compiler'
                }
            }
        },
        server: {
            // 是否自动打开浏览器 (加了个 || false 防止配置不存在报错)
            open: env.VITE_OPEN ? JSON.parse(env.VITE_OPEN) : false,

            // 监听所有网卡，允许外部访问
            host: '0.0.0.0',

            // 端口号 (加了个 || 8080 防止配置不存在报错)
            port: env.VITE_PORT || 8080,

            // 是否开启热更新
            hmr: true,

            // 👇👇👇【关键修改 1】解决 ngrok "Blocked request" 报错 👇👇👇
            // 设置为 true 将允许任何域名访问开发服务器
            allowedHosts: true,

            // 👇👇👇【关键修改 2】配置代理，让 ngrok 也能连上后端 👇👇👇
            proxy: {
                // 凡是 /api 开头的请求，都转发给本地的 Django (8000)
                // 注意：前端代码里的请求路径要写成 '/api/login' 这种形式
                '/api': {
                    target: 'http://127.0.0.1:8000', // 你的 Django 本地地址
                    changeOrigin: true,
                    // rewrite: (path) => path.replace(/^\/api/, '') // 如果后端不需要 /api 前缀，就去掉它
                },
                // 如果你有专门的 media 路径（比如图片），也可以加一个
                '/media': {
                    target: 'http://127.0.0.1:8000',
                    changeOrigin: true,
                }
            }
        },
        resolve: {
            // 配置路径别名
            alias: {
                // @代替src
                '@': fileURLToPath(new URL('./src', import.meta.url)),
            }
        },
        optimizeDeps: {
            include: [
                'vue',
                'pinia',
                'vue-router',
                'pinia-plugin-persistedstate'
            ],
        }
    }
})