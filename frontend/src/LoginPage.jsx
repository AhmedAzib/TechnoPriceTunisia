import { useState } from 'react'
import { useAuth } from './AuthContext'
import { useNavigate, Link, useLocation } from 'react-router-dom'

function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    const success = await login(username, password)
    if (success) {
      const from = location.state?.from?.pathname || "/";
      navigate(from);
    } else {
      setError('Invalid credentials')
    }
  }

  return (
    <div style={{ maxWidth: '400px', margin: '50px auto', padding: '30px', background: 'white', borderRadius: '12px', boxShadow: '0 4px 12px rgba(0,0,0,0.1)', fontFamily: '"Inter", sans-serif' }}>
      <h2 style={{ textAlign: 'center', marginBottom: '20px' }}>Welcome Back 👋</h2>
      {error && <div style={{ color: 'red', marginBottom: '15px', textAlign: 'center' }}>{error}</div>}
      
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
        <input 
          type="text" 
          placeholder="Username" 
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
          style={{ padding: '12px', borderRadius: '8px', border: '1px solid #ddd', fontSize: '1rem' }}
        />
        <input 
          type="password" 
          placeholder="Password" 
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          style={{ padding: '12px', borderRadius: '8px', border: '1px solid #ddd', fontSize: '1rem' }}
        />
        <button type="submit" style={{ padding: '12px', borderRadius: '8px', border: 'none', background: '#2563eb', color: 'white', fontWeight: 'bold', fontSize: '1rem', cursor: 'pointer' }}>
          Login
        </button>
      </form>
      
      <div style={{ marginTop: '20px', textAlign: 'center', fontSize: '0.9rem', color: '#666' }}>
        Don't have an account? <Link to="/register" style={{ color: '#2563eb', fontWeight: 'bold' }}>Sign Up</Link>
      </div>
    </div>
  )
}

export default LoginPage
