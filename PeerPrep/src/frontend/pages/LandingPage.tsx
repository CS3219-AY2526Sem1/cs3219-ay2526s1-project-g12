import { Link } from "react-router";
import LandingImg from "../assets/Images/landing_page_img.png";

function LandingPage() {
    return (
        <div>
            <div className="grid grid-cols-2 gap-2 h-full md:pt-40 lg:pt-20">
                {/* Left side text */}
                <div className="flex justify-center items-center">
                    <div className="text-left space-y-5">
                        <p className="peerprep-logo">
                            PeerPrep
                        </p>
                        <div className="text-4xl lg:text-5xl font-bold">
                            <p> Master Tech</p>
                            <p> Interviews</p>
                            <p>Together</p>
                        </div>
                        <p className="text-xl lg:text-3xl">
                            Connect with peers, practice problems, <br />
                            and ace your next technical interview!
                        </p>
                        <div className="grid grid-cols-2 gap-4 md:px-10 lg:px-20">
                            <button className="btn btn-primary">Get Started</button>
                            <Link
                                to="/auth/login" // route path
                                className="btn btn-primary btn-soft"
                            >
                                Go to Login
                            </Link>
                        </div>
                        <p className="pt-15 normal-text">GOOGLE /  AWS / META / MICROSOFT</p>
                    </div>
                </div>

                {/* Right side image */}
                <div className="flex justify-center items-center ">
                    <img src={LandingImg} className="max-h-screen w-auto object-contain scale-80" />
                </div>
            </div>
        </div>
    )
}

export default LandingPage