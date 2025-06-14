import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    root: '.',
    publicDir: 'public',
    build: {
        outDir: 'dist',
        emptyOutDir: true,
    },
    server: {
        port: 8080, // Mantém a mesma porta do Docker Compose
        proxy: {
            // Proxy para as chamadas de API
            '/api': {
                target: 'http://localhost:8001', // Atualizado para a nova porta do backend
                changeOrigin: true,
            },
            // Proxy para os traces do OpenTelemetry
            '/v1/traces': {
                target: 'http://localhost:4318', // Direciona para o OTel Collector
                changeOrigin: true,
            }
        }
    }
})
