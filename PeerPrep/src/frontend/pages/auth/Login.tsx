import GitHubLogo from "../../assets/Images/github-logo.png"
import GoogleLogo from "../../assets/Images/google-logo.png"

function Login() {
    return (
        <div className="flex  flex-col justify-center items-center">
            <div className="text-left space-y-1">
                <p className="text-xl lg:text-3xl">
                    WELCOME BACK TO
                </p>
                <p className="peerprep-logo">
                    PeerPrep
                </p>
                <div>
                    <div>
                        <p className="normal-text flex flex-col items-center  ">
                            Sign in options
                        </p>
                        {/* For signing in using an email & password */}
                        <fieldset>
                            <legend className="fieldset-legend">Email</legend>
                            <label className="input validator">
                                <svg className="h-[1em] opacity-50" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                                    <g
                                        strokeLinejoin="round"
                                        strokeLinecap="round"
                                        strokeWidth="2.5"
                                        fill="none"
                                        stroke="currentColor"
                                    >
                                        <rect width="20" height="16" x="2" y="4" rx="2"></rect>
                                        <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"></path>
                                    </g>
                                </svg>
                                <input type="email" placeholder="JaneDoe@gmail.com" required />
                            </label>

                            <legend className="fieldset-legend">Password</legend>
                            <label className="input validator">
                                <svg className="h-[1em] opacity-50" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                                    <g
                                        strokeLinejoin="round"
                                        strokeLinecap="round"
                                        strokeWidth="2.5"
                                        fill="none"
                                        stroke="currentColor"
                                    >
                                        <path
                                            d="M2.586 17.414A2 2 0 0 0 2 18.828V21a1 1 0 0 0 1 1h3a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h1a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h.172a2 2 0 0 0 1.414-.586l.814-.814a6.5 6.5 0 1 0-4-4z"
                                        ></path>
                                        <circle cx="16.5" cy="7.5" r=".5" fill="currentColor"></circle>
                                    </g>
                                </svg>
                                <input
                                    type="password"
                                    required
                                    placeholder="Password"
                                />
                            </label>
                        </fieldset>
                    </div>
                    <div className="divider divider-neutral">OR</div>
                    {/* UI to sign in using other platforms */}
                    <div className="flex w-full flex-col items-center ">
                        <ul className="menu menu-horizontal">
                            <li>
                                <a>
                                    <img
                                        src={GitHubLogo}
                                        alt="GitHubSignIn"
                                        className="h-5 w-5" // same size as original SVG
                                    />
                                </a>
                            </li>
                            <li>
                                <a>
                                    <img
                                        src={GoogleLogo}
                                        alt="GmailSignIn"
                                        className="h-5 w-5"
                                    />
                                </a>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Login