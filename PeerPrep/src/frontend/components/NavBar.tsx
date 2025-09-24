import "../assets/styles.css";

function NavBar() {
  return (
    <div className="navbar">
      <div className="navbar-start text-3xl font-bold">
        <text className="text-lime-800">Peer</text>
        <text className="text-blue-800">Prep</text>
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
