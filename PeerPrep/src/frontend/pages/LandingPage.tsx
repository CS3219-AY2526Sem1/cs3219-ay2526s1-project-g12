import { Link } from 'react-router';
import LandingImg from '../assets/Images/landing_page_img.png';

function LandingPage() {
  return (
    <div className="grid grid-cols-2 gap-2 h-screen">
      {/* Left side text */}
      <div className="flex flex-col justify-center min-h-screen pl-40 space-y-6">
        <div className="flex-grow"></div>
        <span className="peerprep-logo pb-2 mt-[5%]">PeerPrep</span>
        <span className="text-[clamp(3rem,4.8vw,6rem)] font-semibold tracking-wider leading-[0.95] pb-4">
          <span className="whitespace-nowrap">Master Tech </span>
          <br />
          Interviews Together
        </span>
        <p className="text-[clamp(1rem,1vw,1.25rem)] tracking-widest pb-5">
          Connect with peers, practice problems, and ace your next technical
          interview!
        </p>
        <div className="grid grid-cols-2 gap-7 w-7/10">
          <Link
            to="/auth/register" // route path
            className="btn btn-primary btn-lg text-[clamp(0.9rem,1.2vw,1.5rem)] font-normal"
          >
            Get Started
          </Link>
          <Link
            to="/auth/login" // route path
            className="btn btn-primary btn-soft btn-lg text-[clamp(0.9rem,1.2vw,1.5rem)] font-normal"
          >
            Login
          </Link>
        </div>
        <div className="flex-grow"></div>
        <p className="text-[clamp(0.85rem,0.8vw,1rem)] font-medium tracking-[0.25em] mb-[5%]">
          GOOGLE / AWS / META / MICROSOFT
        </p>
      </div>

      {/* Right side image */}
      <div className="flex justify-center items-center pr-40">
        <img
          src={LandingImg}
          alt="PeerPrep landing page illustration"
          className="max-h-screen w-auto object-contain scale-80"
        />
      </div>
    </div>
  );
}

export default LandingPage;
