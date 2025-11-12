import { Link, useNavigate } from 'react-router';
import '../assets/styles.css';
import { useAuth } from '../context/AuthContext';
import type { RoleName } from '../types/Role';
import type { NavButton } from '../types/NavButton';

interface NavBarProps {
  buttons: NavButton[];
}

function NavBar({ buttons }: NavBarProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const userRole: RoleName = user?.role.role ?? 'user';

  const visibleButtons = buttons.filter((btn) => {
    if (userRole === 'admin') return true;
    return btn.role !== 'admin';
  });

  const handleLogout = async () => {
    await logout();
    navigate('/auth/login');
  };

  return (
    <div className="navbar">
      <div className="flex-1">
        <Link to="/dashboard" className="peerprep-logo mt-[5%]">
          PeerPrep
        </Link>
      </div>

      <div className="flex gap-2">
        {visibleButtons.map((btn) =>
          btn.route === '/auth/logout' ? (
            <Link
              key={btn.label}
              to={btn.route}
              onClick={handleLogout}
              className={`btn ${btn.style} font-normal`}
            >
              {btn.label}
            </Link>
          ) : (
            <Link
              key={btn.label}
              to={btn.route}
              className={`btn ${btn.style} font-normal`}
            >
              {btn.label}
            </Link>
          )
        )}
      </div>
    </div>
  );
}

export default NavBar;
