import { Link } from "react-router";
import GitHubLogo from "../../assets/Images/github-logo.png";
import GoogleLogo from "../../assets/Images/google-logo.png";

function Login() {
  return (
    <div className="flex flex-col justify-center max-w-md w-full mx-auto space-y-4">
      <div className="pb-3">
        <span className="text-[clamp(0.85rem,0.8vw,1rem)] font-medium tracking-[0.20em]">
          WELCOME BACK TO
        </span>
        <br />
        <span className="peerprep-logo">PeerPrep</span>
      </div>

      {/* For signing in using an email & password */}
      <fieldset className="pb-3">
        <legend className="fieldset-legend font-normal">Email</legend>
        <label className="input validator w-full">
          <svg
            className="h-[1em] opacity-50"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
          >
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

        <legend className="fieldset-legend font-normal">Password</legend>
        <label className="input validator w-full">
          <svg
            className="h-[1em] opacity-50"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
          >
            <g
              strokeLinejoin="round"
              strokeLinecap="round"
              strokeWidth="2.5"
              fill="none"
              stroke="currentColor"
            >
              <path d="M2.586 17.414A2 2 0 0 0 2 18.828V21a1 1 0 0 0 1 1h3a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h1a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h.172a2 2 0 0 0 1.414-.586l.814-.814a6.5 6.5 0 1 0-4-4z"></path>
              <circle cx="16.5" cy="7.5" r=".5" fill="currentColor"></circle>
            </g>
          </svg>
          <input type="password" required placeholder="Password" />
        </label>

        <Link to="/auth/reset" className="font-light text-sm underline">
          Forgot your password?
        </Link>
      </fieldset>

      <button className="btn btn-primary w-full font-normal">
        Continue with Email
      </button>

      <div className="divider divider-neutral mt-0">OR</div>

      {/* UI to sign in using other platforms */}
      <button className="btn btn-primary btn-soft w-full font-normal pb-3">
        Continue with Github
      </button>

      <p className="text-center">
        Don't have an account?&nbsp;
        <Link to="/auth/signup" className="underline">
          Sign up
        </Link>
      </p>
    </div>
  );
}

export default Login;
