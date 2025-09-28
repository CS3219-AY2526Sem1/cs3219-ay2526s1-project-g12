import { Link } from "react-router";
import LandingImg from "../assets/Images/landing_page_img.png";

function LandingPage() {
  return (
    <div>
      <div className="grid grid-cols-2 gap-2 h-full md:pt-40 lg:pt-20">
        {/* Left side text */}
        <div className="flex justify-center items-center px-40">
          <div className="text-left space-y-6">
            <span className="peerprep-logo mb-1">PeerPrep</span>
            <div className="text-8xl font-semibold tracking-wider leading-[0.95]">
              <span>Master Tech Interviews Together</span>
            </div>
            <p className="text-xl lg:text-3xl">
              Connect with peers, practice problems, <br />
              and ace your next technical interview!
            </p>
            <div className="grid grid-cols-2 gap-4">
              <button className="btn btn-primary">Get Started</button>
              <Link
                to="/auth/login" // route path
                className="btn btn-primary btn-soft"
              >
                Go to Login
              </Link>
            </div>
            <p className="pt-15 normal-text">GOOGLE / AWS / META / MICROSOFT</p>
          </div>
        </div>

        {/* Right side image */}
        <div className="flex justify-center items-center ">
          <img
            src={LandingImg}
            alt="PeerPrep landing page illustration"
            className="max-h-screen w-auto object-contain scale-80"
          />
        </div>
      </div>
    </div>
  );
}

export default LandingPage;
