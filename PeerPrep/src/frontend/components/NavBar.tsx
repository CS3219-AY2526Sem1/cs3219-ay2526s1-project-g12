import "../assets/styles.css";

function NavBar() {
  return (
    <div className="navbar">
      <div className="navbar-start text-3xl font-bold">
        <span className="text-lime-800">Peer</span>
        <span className="text-blue-800">Prep</span>
      </div>
      <div className="navbar-end">
        <div className="flex  gap-10">
          <button className="btn btn-ghost btn-primary">Login</button>
          <button className="btn btn-primary">Sign Up</button>
        </div>
      </div>
    </div>
  );
}

export default NavBar;
