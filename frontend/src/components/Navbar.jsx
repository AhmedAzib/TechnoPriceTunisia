import { Link } from 'react-router-dom'
import { useAuth } from '../AuthContext'

function Navbar({ searchTerm, setSearchTerm }) {
  const { user, logout } = useAuth()

  return (
    <nav style={{ backgroundColor: '#020617', padding: '15px 40px', boxShadow: '0 2px 10px rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', position: 'sticky', top: 0, zIndex: 100, borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
        <Link to="/" style={{ textDecoration: 'none' }}>
           <h1 style={{ fontSize: '1.8rem', fontWeight: '800', margin: 0, color: 'white' }}>
             Tech<span style={{ color: '#007bff' }}>Compare</span>.
           </h1>
        </Link>
        
        <div style={{ display: 'flex', gap: '20px', marginLeft: '30px' }}>
            <Link to="/products" style={{ textDecoration: 'none', color: '#cbd5e1', fontWeight: '600', fontSize: '1rem' }}>Products</Link>
            <Link to="/catalog" style={{ textDecoration: 'none', color: '#007bff', fontWeight: '700', fontSize: '1rem' }}>Series Catalog</Link>
        </div>
        
        {setSearchTerm && (
            <input 
              type="text" 
              placeholder="🔍 Search specific model..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{ padding: '10px 20px', width: '350px', borderRadius: '20px', border: '1px solid #ddd', backgroundColor: '#f1f3f5' }}
            />
        )}

        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
            {user ? (
                <>
                    <span style={{ fontWeight: '600' }}>Hi, {user?.username || "Friend"}</span>
                    <Link to="/wishlist" style={{ textDecoration: 'none', fontSize: '1.5rem' }}>❤️</Link>
                    <button onClick={logout} style={{ padding: '8px 16px', borderRadius: '20px', border: '1px solid #ddd', background: 'white', cursor: 'pointer' }}>
                        Logout
                    </button>
                </>
            ) : (
                <Link to="/login" style={{ padding: '8px 16px', borderRadius: '20px', background: '#007bff', color: 'white', textDecoration: 'none', fontWeight: '600' }}>
                    Login
                </Link>
            )}
        </div>
    </nav>
  )
}

export default Navbar
