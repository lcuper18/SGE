import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

// Componente temporal de inicio
function HomePage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-8">
      <div className="text-center space-y-6 max-w-2xl">
        <h1 className="text-5xl font-bold text-primary-600">
          SGE Calificaciones MVP
        </h1>
        <p className="text-xl text-gray-600">
          Sistema de gestión de calificaciones offline para docentes
        </p>
        
        <div className="bg-white rounded-lg shadow-lg p-8 mt-8">
          <h2 className="text-2xl font-semibold mb-4">✅ Proyecto Inicializado</h2>
          <div className="text-left space-y-2">
            <StatusItem status="success" text="Electron configurado con hardening" />
            <StatusItem status="success" text="SQLCipher AES-256 activado" />
            <StatusItem status="success" text="React + TypeScript + Vite" />
            <StatusItem status="success" text="FastAPI backend listo" />
            <StatusItem status="pending" text="Sprint 0 en progreso..." />
          </div>
        </div>

        <div className="mt-8 flex gap-4 justify-center">
          <button className="px-6 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition">
            Configuración Inicial
          </button>
          <button className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300 transition">
            Documentación
          </button>
        </div>
      </div>
    </div>
  )
}

// Placeholder para login
function LoginPage() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full">
        <h2 className="text-2xl font-bold mb-6">Login - Próximamente</h2>
        <p className="text-gray-600">
          Sistema de autenticación con Argon2id será implementado en Sprint 0.
        </p>
      </div>
    </div>
  )
}

// Componente de ayuda
function StatusItem({ status, text }: { status: 'success' | 'pending'; text: string }) {
  return (
    <div className="flex items-center gap-3">
      <span className={`text-2xl ${status === 'success' ? '✅' : '⏳'}`}>
        {status === 'success' ? '✅' : '⏳'}
      </span>
      <span className={status === 'success' ? 'text-gray-700' : 'text-gray-500'}>
        {text}
      </span>
    </div>
  )
}

export default App
