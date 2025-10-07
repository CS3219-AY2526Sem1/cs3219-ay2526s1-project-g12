import { Link } from "react-router";
import "../assets/styles.css";

interface NavBarProps {
  buttons: {
    label: string;
    role: string;
    route: string;
    style: string;
  }[];
}

function NavBar({ buttons }: NavBarProps) {
  return (
    <div className="navbar">
      <div className="flex-1">
        <span className="peerprep-logo mt-[5%]">PeerPrep</span>
      </div>

      <div className="flex gap-2">
        {buttons.map((btn) => (
          <Link to={btn.route} className={`btn ${btn.style} font-normal`}>
            {btn.label}
          </Link>
        ))}
      </div>
    </div>
  );
}

export default NavBar;
