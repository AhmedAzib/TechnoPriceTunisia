import { useState } from 'react'
import { useAuth } from './AuthContext'
import { useNavigate, Link } from 'react-router-dom'

function RegisterPage() {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const { register } = useAuth()
  const navigate = useNavigate()
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await register(username, email, password)
      navigate('/')
    } catch (err) {
      setError('Registration failed. Try a different username.')
    }
  }

  return (
    <div style={{ maxWidth: '400px', margin: '50px auto', padding: '30px', background: 'white', borderRadius: '12px', boxShadow: '0 4px 12px rgba(0,0,0,0.1)', fontFamily: '"Inter", sans-serif' }}>
      <h2 style={{ textAlign: 'center', marginBottom: '20px' }}>Create Account 🚀</h2>
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
          type="email" 
          placeholder="Email address" 
          value={email}
          onChange={(e) => setEmail(e.target.value)}
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
        <button type="submit" style={{ padding: '12px', borderRadius: '8px', border: 'none', background: '#16a34a', color: 'white', fontWeight: 'bold', fontSize: '1rem', cursor: 'pointer' }}>
          Sign Up
        </button>
      </form>
      
      <div style={{ marginTop: '20px', textAlign: 'center', fontSize: '0.9rem', color: '#666' }}>
        Already have an account? <Link to="/login" style={{ color: '#2563eb', fontWeight: 'bold' }}>Login</Link>
      </div>
    </div>
  )
}

export default RegisterPage
