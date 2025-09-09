import type { ReactNode } from "react";
import AuthPanelImage from "../assets/Images/auth_page_panel_img.png"

type Props = {
    children: ReactNode
}

function AuthLayout({ children }: Props) { // children is used for nested props
    return (
        <div>
            <div className="grid grid-cols-2 h-screen">
                {/* Left column */}
                {children}
                {/* Right column */}
                <div>
                    <img
                        src={AuthPanelImage}
                        alt="AuthPanelImage"
                        className="object-cover w-screen h-screen"
                    />
                </div>
            </div>
        </div>
    );
}

export default AuthLayout