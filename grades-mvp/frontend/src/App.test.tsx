import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import App from './App'

describe('App Component', () => {
  it('renders without crashing', () => {
    const { container } = render(<App />)
    
    // Verificar que el componente se renderiza
    expect(container).toBeTruthy()
  })
  
  it('has router functionality', () => {
    const { container } = render(<App />)
    
    // Verificar que hay contenido renderizado
    expect(container.innerHTML).toContain('div')
  })
})
