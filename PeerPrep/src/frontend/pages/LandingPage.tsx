import LandingImg from "../assets/Images/landing_page_img.png";

function LandingPage() {
    return (
        <div>
            <div className="grid grid-cols-2 gap-2 h-full md:pt-40 lg:pt-20">
                {/* Left side text */}
                <div className="flex justify-center items-center">
                    <div className="text-left space-y-5">
                        <p className="text-7xl lg:text-8xl font-bold font-mono bg-gradient-to-r from-primary to-secondary text-transparent bg-clip-text">
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
                            <button className="btn btn-primary btn-soft">Login</button>
                        </div>
                        <p className="pt-15">GOOGLE /  AWS / META / MICROSOFT</p>
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