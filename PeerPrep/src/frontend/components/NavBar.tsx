import { Link, useNavigate } from 'react-router';
import '../assets/styles.css';
import { useAuth } from '../context/AuthContext';

interface NavBarProps {
  buttons: {
    label: string;
    role: string;
    route: string;
    style: string;
  }[];
}

function NavBar({ buttons }: NavBarProps) {
  const { logout } = useAuth();
  const navigate = useNavigate();

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
        {buttons.map((btn) =>
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
