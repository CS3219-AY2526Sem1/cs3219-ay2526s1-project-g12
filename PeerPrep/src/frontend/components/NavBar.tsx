import "../assets/styles.css";

function NavBar() {
  return (
    <div className="navbar">
      <div className="flex-1">
        <span className="peerprep-logo mt-[5%]">PeerPrep</span>
      </div>

      <div className="flex gap-2">
        <button className="btn btn-warning font-normal">⚠ Manage Qns</button>
        <button className="btn btn-primary font-normal">
          ✈ Initiate Match
        </button>
        <button className="btn btn-success font-normal">
          👤 Account Setting
        </button>
        <button className="btn btn-success font-normal">🚪 Logout</button>
      </div>
    </div>
  );
}

export default NavBar;
